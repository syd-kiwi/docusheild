from __future__ import annotations

from typing import List, Sequence

from .models import Detection, EvaluationReport, Frame


class Evaluator:
    def compute(
        self,
        frames: Sequence[Frame],
        detections_per_frame: Sequence[List[Detection]],
        mitigation_applied: Sequence[bool],
        latency_ms: Sequence[float],
        peak_memory_mb: float,
    ) -> EvaluationReport:
        tp, fp, fn = 0, 0, 0
        readable_visible = 0
        total_sensitive = 0

        for frame, dets, mitigated in zip(frames, detections_per_frame, mitigation_applied):
            gt = {obj.class_name for obj in frame.objects if obj.class_name != "nonsensitive"}
            pred = {d.class_name for d in dets}
            tp += len(gt & pred)
            fp += len(pred - gt)
            fn += len(gt - pred)

            total_sensitive += len(gt)
            if not mitigated:
                readable_visible += len(gt)

        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        readable_exposure_rate = readable_visible / total_sensitive if total_sensitive else 0.0
        readable_exposure_duration_s = readable_visible * 0.06
        avg_latency = sum(latency_ms) / len(latency_ms) if latency_ms else 0.0
        battery_impact = min(1.0, (avg_latency / 100.0) * 0.45 + (peak_memory_mb / 1024.0) * 0.55)
        forensic_completeness = 1.0 if len(frames) == len(detections_per_frame) else 0.0

        return EvaluationReport(
            precision=precision,
            recall=recall,
            readable_exposure_rate=readable_exposure_rate,
            readable_exposure_duration_s=readable_exposure_duration_s,
            avg_latency_ms=avg_latency,
            peak_memory_mb=peak_memory_mb,
            battery_impact_score=battery_impact,
            forensic_completeness=forensic_completeness,
        )
