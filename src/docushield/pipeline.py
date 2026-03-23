from __future__ import annotations

import time
from dataclasses import asdict
from statistics import mean
from typing import Dict, List

from .audit import AuditLogger
from .detector import OnnxRuntimeConfig, YoloOnnxDetector
from .evaluator import Evaluator
from .mitigation import OverlayMitigator
from .models import AuditEvent, Detection, EvaluationReport, PolicyConfig
from .policy import PolicyEngine
from .prototype_assets import ShareablePrototypeExporter
from .virtual_env import SENSITIVE_CLASSES, StressSweepConfig, VirtualHomeOffice


class DocushieldPipeline:
    def __init__(self, session_id: str, audit_path: str = "artifacts/audit_log.jsonl") -> None:
        self.session_id = session_id
        self.environment = VirtualHomeOffice()
        self.detector = YoloOnnxDetector(
            classes=SENSITIVE_CLASSES,
            config=OnnxRuntimeConfig(downsample_factor=2),
        )
        self.policy = PolicyEngine(PolicyConfig(work_mode_enabled=True, sharing_active=False))
        self.mitigator = OverlayMitigator()
        self.audit = AuditLogger(audit_path)
        self.evaluator = Evaluator()
        self.prototype_exporter = ShareablePrototypeExporter()

    def export_unity_scene_spec(self, path: str = "artifacts/unity_scene_spec.json") -> Dict[str, object]:
        return self.environment.export_unity_scene_spec(path)

    def export_shareable_mockup(self, path: str = "shareables/docushield_vr_mockup.svg") -> Dict[str, object]:
        frame = self.environment.render_frame(
            frame_id="prototype_shareable",
            lighting=0.85,
            clutter=0.35,
            distance=0.9,
            motion=0.05,
            camera_angle=0.0,
        )
        assessment = self.detector.infer(frame)
        exported_path = self.prototype_exporter.export_svg(
            frame=frame,
            detections=assessment.detections,
            path=path,
            risk_score=assessment.risk_score,
        )
        return {
            "mockup_path": str(exported_path),
            "risk_score": assessment.risk_score,
            "risk_level": assessment.risk_level,
            "detections": [asdict(detection) for detection in assessment.detections],
        }

    def run_sweep(self, limit_frames: int = 20) -> Dict[str, object]:
        frames = self.environment.sweep(StressSweepConfig())[:limit_frames]
        all_detections: List[List[Detection]] = []
        mitigation_applied: List[bool] = []
        latencies_ms: List[float] = []
        notifications: List[str] = []
        risk_scores: List[float] = []

        for frame in frames:
            if not self.policy.should_run_detection():
                all_detections.append([])
                mitigation_applied.append(False)
                notifications.append("Detection skipped by policy.")
                continue

            start = time.perf_counter()
            assessment = self.detector.infer(frame)
            latencies_ms.append((time.perf_counter() - start) * 1000.0)
            notifications.append(assessment.notification)
            risk_scores.append(assessment.risk_score)

            should_mitigate = self.policy.should_mitigate(assessment)
            mitigation_applied.append(should_mitigate)
            all_detections.append(assessment.detections)

            if should_mitigate:
                mitigation = self.mitigator.apply(
                    frame=frame,
                    detections=assessment.detections,
                    strength=self.policy.mitigation_strength(),
                )
                summary = mitigation.prompt
                event_type = "mitigation_applied"
            else:
                summary = assessment.notification
                event_type = "detection_only"

            self.audit.write_event(
                AuditEvent.create(
                    session_id=self.session_id,
                    event_type=event_type,
                    active_app="virtual_office_tester",
                    media_saved=False,
                    summary=summary,
                    risk_level=assessment.risk_level,
                    details={
                        "frame_id": frame.frame_id,
                        "frame_source": frame.source,
                        "risk_score": round(assessment.risk_score, 3),
                        "detections": [asdict(d) for d in assessment.detections],
                    },
                )
            )

        report: EvaluationReport = self.evaluator.compute(
            frames=frames,
            detections_per_frame=all_detections,
            mitigation_applied=mitigation_applied,
            latency_ms=latencies_ms,
            peak_memory_mb=220.0,
        )

        return {
            "frames_processed": len(frames),
            "mitigation_rate": mean(mitigation_applied) if mitigation_applied else 0.0,
            "average_risk_score": mean(risk_scores) if risk_scores else 0.0,
            "latest_notification": notifications[-1] if notifications else "No frames processed.",
            "unity_integration": {
                "scene_spec_path": "artifacts/unity_scene_spec.json",
                "detector_contract": self.detector.unity_inference_contract(),
            },
            "evaluation": asdict(report),
            "audit_log": str(self.audit.path),
        }
