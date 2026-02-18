from __future__ import annotations

import random
from typing import Iterable, List, Set

from .models import Detection, Frame, RiskAssessment


class YoloOnnxDetector:
    """ONNX-deployable detector facade.

    In production, replace `_infer_with_ground_truth` with ONNX Runtime calls.
    This implementation keeps the same interface so Unity-side integration stays stable.
    """

    def __init__(self, classes: Iterable[str], downsample_factor: int = 2, seed: int = 11) -> None:
        self.classes: Set[str] = set(classes)
        self.downsample_factor = max(1, downsample_factor)
        self._rng = random.Random(seed)

    def infer(self, frame: Frame) -> RiskAssessment:
        detections = self._infer_with_ground_truth(frame)
        risk_score = self._compute_risk_score(frame, detections)
        return RiskAssessment(risk_score=risk_score, detections=detections)

    def _infer_with_ground_truth(self, frame: Frame) -> List[Detection]:
        detections: List[Detection] = []
        quality_factor = max(0.1, frame.lighting) * (1.0 - min(frame.motion, 0.8) * 0.35)
        quality_factor *= (1.0 - min(frame.clutter, 0.9) * 0.2)

        for obj in frame.objects:
            if obj.class_name not in self.classes:
                continue
            base_conf = 0.55 + 0.4 * quality_factor
            confidence = max(0.05, min(0.99, base_conf + self._rng.uniform(-0.12, 0.1)))
            if confidence < 0.25:
                continue
            detections.append(
                Detection(class_name=obj.class_name, bbox=obj.bbox, confidence=confidence)
            )
        return detections

    def _compute_risk_score(self, frame: Frame, detections: List[Detection]) -> float:
        if not detections:
            return 0.0
        avg_conf = sum(d.confidence for d in detections) / len(detections)
        readable_boost = 0.15
        stress_penalty = min(0.25, frame.distance * 0.08 + abs(frame.camera_angle) * 0.003)
        score = avg_conf * 0.7 + readable_boost + stress_penalty
        return max(0.0, min(1.0, score))
