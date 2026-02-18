from __future__ import annotations

import itertools
import random
from dataclasses import dataclass
from typing import Iterable, List

from .models import Frame, SceneObject


SENSITIVE_CLASSES = ("document", "envelope", "notebook", "whiteboard")


@dataclass
class StressSweepConfig:
    lighting: Iterable[float] = (0.35, 0.7, 1.0)
    clutter: Iterable[float] = (0.1, 0.5, 0.9)
    distance: Iterable[float] = (0.5, 1.0, 1.5)
    motion: Iterable[float] = (0.0, 0.2, 0.6)
    camera_angle: Iterable[float] = (-20.0, 0.0, 25.0)


class VirtualHomeOffice:
    """Synthetic virtual environment with deterministic ground truth labels."""

    def __init__(self, width: int = 1280, height: int = 720, seed: int = 7) -> None:
        self.width = width
        self.height = height
        self._rng = random.Random(seed)

    def _generate_objects(self) -> List[SceneObject]:
        presets = [
            ("obj_doc_1", "document", (180, 260, 320, 160)),
            ("obj_env_1", "envelope", (620, 280, 220, 120)),
            ("obj_notebook_1", "notebook", (900, 300, 250, 170)),
            ("obj_board_1", "whiteboard", (260, 40, 450, 230)),
            ("obj_keyboard", "nonsensitive", (520, 470, 340, 120)),
        ]
        objects: List[SceneObject] = []
        for object_id, class_name, bbox in presets:
            objects.append(
                SceneObject(
                    object_id=object_id,
                    class_name=class_name,
                    bbox=self._jitter_bbox(bbox),
                    readable=class_name in SENSITIVE_CLASSES,
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
