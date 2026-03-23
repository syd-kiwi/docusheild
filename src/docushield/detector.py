from __future__ import annotations

import random
from dataclasses import dataclass, asdict
from typing import Iterable, List, Set

from .models import Detection, Frame, RiskAssessment


@dataclass
class OnnxRuntimeConfig:
    model_path: str = "Assets/StreamingAssets/yolo/docushield_yolo.onnx"
    execution_provider: str = "CPUExecutionProvider"
    input_width: int = 640
    input_height: int = 640
    conf_threshold: float = 0.25
    iou_threshold: float = 0.45
    downsample_factor: int = 2


class YoloOnnxDetector:
    """ONNX-deployable detector facade.

    In production, replace `_infer_with_ground_truth` with ONNX Runtime for Unity calls.
    This implementation keeps the same interface so Unity-side integration stays stable.
    """

    _CLASS_WEIGHTS = {
        "document": 1.0,
        "envelope": 0.8,
        "notebook": 0.7,
        "whiteboard": 0.9,
    }

    def __init__(self, classes: Iterable[str], config: OnnxRuntimeConfig | None = None, seed: int = 11) -> None:
        self.classes: Set[str] = set(classes)
        self.config = config or OnnxRuntimeConfig()
        self._rng = random.Random(seed)

    def infer(self, frame: Frame) -> RiskAssessment:
        detections = self._infer_with_ground_truth(frame)
        risk_score = self._compute_risk_score(frame, detections)
        risk_level = self._risk_level(risk_score)
        return RiskAssessment(
            risk_score=risk_score,
            detections=detections,
            risk_level=risk_level,
            notification=self._notification_text(risk_level, detections),
        )

    def _infer_with_ground_truth(self, frame: Frame) -> List[Detection]:
        detections: List[Detection] = []
        quality_factor = max(0.1, frame.lighting) * (1.0 - min(frame.motion, 0.8) * 0.35)
        quality_factor *= (1.0 - min(frame.clutter, 0.9) * 0.2)
        quality_factor *= 1.0 - min(frame.distance, 1.7) * 0.08

        for obj in frame.objects:
            if obj.class_name not in self.classes:
                continue
            base_conf = 0.55 + 0.4 * quality_factor
            confidence = max(0.05, min(0.99, base_conf + self._rng.uniform(-0.12, 0.1)))
            if confidence < self.config.conf_threshold:
                continue
            detections.append(
                Detection(class_name=obj.class_name, bbox=obj.bbox, confidence=confidence)
            )
        return detections

    def _compute_risk_score(self, frame: Frame, detections: List[Detection]) -> float:
        if not detections:
            return 0.0
        weighted_confidence = sum(
            d.confidence * self._CLASS_WEIGHTS.get(d.class_name, 0.5) for d in detections
        ) / len(detections)
        readable_boost = 0.12 + 0.03 * len(detections)
        stress_penalty = min(0.25, frame.distance * 0.08 + abs(frame.camera_angle) * 0.003)
        score = weighted_confidence * 0.68 + readable_boost + stress_penalty
        return max(0.0, min(1.0, score))

    def unity_inference_contract(self) -> dict[str, object]:
        return {
            "pipeline": "Unity RenderTexture -> Texture2D frame extraction -> ONNX Runtime tensor -> YOLO postprocess",
            "onnx": asdict(self.config),
            "outputs": ["bounding_boxes", "class_labels", "confidence_scores", "risk_score", "risk_level"],
        }

    def _risk_level(self, score: float) -> str:
        if score >= 0.72:
            return "high"
        if score >= 0.4:
            return "medium"
        return "low"

    def _notification_text(self, risk_level: str, detections: List[Detection]) -> str:
        if not detections:
            return "No sensitive physical artifacts detected in the rendered frame."
        classes = ", ".join(sorted({d.class_name for d in detections}))
        if risk_level == "high":
            return f"High exposure risk: {classes} detected. Blur overlays and user warning should be shown."
        if risk_level == "medium":
            return f"Moderate exposure risk: {classes} detected. Notify the user and monitor subsequent frames."
        return f"Low exposure risk: {classes} detected. Keep the scene under observation."
