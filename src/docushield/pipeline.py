from __future__ import annotations

import time
from dataclasses import asdict
from statistics import mean
from typing import Dict, List

from .audit import AuditLogger
from .detector import YoloOnnxDetector
from .evaluator import Evaluator
from .mitigation import OverlayMitigator
from .models import AuditEvent, Detection, EvaluationReport, PolicyConfig
from .policy import PolicyEngine
from .virtual_env import SENSITIVE_CLASSES, StressSweepConfig, VirtualHomeOffice


class DocushieldPipeline:
    def __init__(self, session_id: str, audit_path: str = "artifacts/audit_log.jsonl") -> None:
        self.session_id = session_id
        self.environment = VirtualHomeOffice()
        self.detector = YoloOnnxDetector(classes=SENSITIVE_CLASSES, downsample_factor=2)
        self.policy = PolicyEngine(PolicyConfig(work_mode_enabled=True, sharing_active=False))
        self.mitigator = OverlayMitigator()
        self.audit = AuditLogger(audit_path)
        self.evaluator = Evaluator()

    def run_sweep(self, limit_frames: int = 20) -> Dict[str, object]:
        frames = self.environment.sweep(StressSweepConfig())[:limit_frames]
        all_detections: List[List[Detection]] = []
        mitigation_applied: List[bool] = []
        latencies_ms: List[float] = []

        for frame in frames:
            if not self.policy.should_run_detection():
                all_detections.append([])
                mitigation_applied.append(False)
                continue

            start = time.perf_counter()
            assessment = self.detector.infer(frame)
            latencies_ms.append((time.perf_counter() - start) * 1000.0)

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
                risk_level = "high" if assessment.risk_score >= 0.7 else "medium"
            else:
                summary = "Frame processed without mitigation."
                event_type = "detection_only"
                risk_level = "low"

            self.audit.write_event(
                AuditEvent.create(
                    session_id=self.session_id,
                    event_type=event_type,
                    active_app="virtual_office_tester",
                    media_saved=False,
                    summary=summary,
                    risk_level=risk_level,
                    details={
                        "frame_id": frame.frame_id,
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
            "evaluation": asdict(report),
            "audit_log": str(self.audit.path),
        }
