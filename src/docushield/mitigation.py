from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .models import Detection, Frame


@dataclass
class OverlayRegion:
    bbox: Tuple[int, int, int, int]
    mode: str
    strength: float


@dataclass
class MitigationResult:
    frame_id: str
    overlays: List[OverlayRegion]
    prompt: str


class OverlayMitigator:
    def apply(self, frame: Frame, detections: List[Detection], strength: float) -> MitigationResult:
        overlays = [
            OverlayRegion(bbox=d.bbox, mode="blur", strength=max(0.0, min(1.0, strength)))
            for d in detections
        ]
        prompt = (
            "Sensitive artifacts detected. Please reposition documents or adjust view."
            if overlays
            else "No mitigation required."
        )
        return MitigationResult(frame_id=frame.frame_id, overlays=overlays, prompt=prompt)
