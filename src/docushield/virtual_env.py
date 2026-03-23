from __future__ import annotations

import itertools
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List

from .models import Frame, SceneElement, SceneObject


SENSITIVE_CLASSES = ("document", "envelope", "notebook", "whiteboard")


@dataclass
class StressSweepConfig:
    lighting: Iterable[float] = (0.35, 0.7, 1.0)
    clutter: Iterable[float] = (0.1, 0.5, 0.9)
    distance: Iterable[float] = (0.5, 1.0, 1.5)
    motion: Iterable[float] = (0.0, 0.2, 0.6)
    camera_angle: Iterable[float] = (-20.0, 0.0, 25.0)


class VirtualHomeOffice:
    """Synthetic Unity-ready home office scene with deterministic ground truth."""

    def __init__(self, width: int = 1280, height: int = 720, seed: int = 7) -> None:
        self.width = width
        self.height = height
        self._rng = random.Random(seed)
        self.layout_elements = self._build_layout()

    def _build_layout(self) -> List[SceneElement]:
        return [
            SceneElement(
                element_id="desk_main",
                kind="desk",
                bbox=(110, 350, 980, 250),
                description="Primary wooden desk that holds active paperwork and a keyboard.",
            ),
            SceneElement(
                element_id="shelf_left",
                kind="shelf",
                bbox=(25, 120, 180, 360),
                description="Standing shelf with stored notebooks, envelopes, and reference binders.",
            ),
            SceneElement(
                element_id="whiteboard_wall",
                kind="whiteboard",
                bbox=(240, 35, 490, 240),
                description="Wall mounted whiteboard containing sprint notes and reminders.",
            ),
            SceneElement(
                element_id="monitor_center",
                kind="monitor",
                bbox=(460, 205, 280, 180),
                description="Monitor centered behind the desk to reinforce a realistic office layout.",
            ),
        ]

    def _generate_objects(self) -> List[SceneObject]:
        presets = [
            ("obj_doc_1", "document", (190, 370, 235, 145), "desk_main"),
            ("obj_doc_2", "document", (460, 395, 180, 110), "desk_main"),
            ("obj_env_1", "envelope", (655, 410, 210, 95), "desk_main"),
            ("obj_notebook_1", "notebook", (875, 360, 195, 170), "desk_main"),
            ("obj_notebook_2", "notebook", (50, 215, 120, 165), "shelf_left"),
            ("obj_board_1", "whiteboard", (260, 45, 460, 225), "whiteboard_wall"),
            ("obj_keyboard", "nonsensitive", (505, 545, 340, 70), "desk_main"),
        ]
        objects: List[SceneObject] = []
        for object_id, class_name, bbox, anchor in presets:
            objects.append(
                SceneObject(
                    object_id=object_id,
                    class_name=class_name,
                    bbox=self._jitter_bbox(bbox),
                    readable=class_name in SENSITIVE_CLASSES,
                    anchor_element_id=anchor,
                )
            )
        return objects

    def _jitter_bbox(self, bbox: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        x, y, w, h = bbox
        jx = x + self._rng.randint(-8, 8)
        jy = y + self._rng.randint(-8, 8)
        return (max(0, jx), max(0, jy), w, h)

    def render_frame(
        self,
        frame_id: str,
        lighting: float,
        clutter: float,
        distance: float,
        motion: float,
        camera_angle: float,
    ) -> Frame:
        return Frame(
            frame_id=frame_id,
            width=self.width,
            height=self.height,
            objects=self._generate_objects(),
            lighting=lighting,
            clutter=clutter,
            distance=distance,
            motion=motion,
            camera_angle=camera_angle,
            source="unity_render_texture",
            layout_elements=list(self.layout_elements),
        )

    def sweep(self, config: StressSweepConfig) -> List[Frame]:
        frames: List[Frame] = []
        combinations = itertools.product(
            config.lighting,
            config.clutter,
            config.distance,
            config.motion,
            config.camera_angle,
        )
        for idx, (lighting, clutter, distance, motion, angle) in enumerate(combinations):
            frames.append(
                self.render_frame(
                    frame_id=f"frame_{idx:05d}",
                    lighting=lighting,
                    clutter=clutter,
                    distance=distance,
                    motion=motion,
                    camera_angle=angle,
                )
            )
        return frames

    def export_unity_scene_spec(self, path: str | Path) -> dict[str, object]:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        spec = {
            "scene_name": "DocuShieldHomeOfficeVR",
            "render_resolution": {"width": self.width, "height": self.height},
            "camera": {
                "source": "MainCamera->RenderTexture",
                "transport": "Texture2D.ReadPixels -> ONNX Runtime tensor",
            },
            "layout": [asdict(element) for element in self.layout_elements],
            "sensitive_classes": list(SENSITIVE_CLASSES),
            "detection_targets": [asdict(obj) for obj in self._generate_objects() if obj.class_name in SENSITIVE_CLASSES],
        }
        output_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
        return spec
