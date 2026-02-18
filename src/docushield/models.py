from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Tuple


BBox = Tuple[int, int, int, int]


@dataclass
class SceneObject:
    object_id: str
    class_name: str
    bbox: BBox
    readable: bool = True


@dataclass
class Frame:
    frame_id: str
    width: int
    height: int
    objects: List[SceneObject]
    lighting: float
    clutter: float
    distance: float
    motion: float
    camera_angle: float


@dataclass
class Detection:
    class_name: str
    bbox: BBox
    confidence: float


@dataclass
class RiskAssessment:
    risk_score: float
    detections: List[Detection]


@dataclass
class PolicyConfig:
    work_mode_enabled: bool = True
    sharing_active: bool = False
    mitigation_threshold: float = 0.45
    sharing_threshold: float = 0.30
    quick_override: bool = False


@dataclass
class AuditEvent:
    timestamp: str
    session_id: str
    event_type: str
    active_app: str
    media_saved: bool
    summary: str
    risk_level: str
    details: Dict[str, object] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        session_id: str,
        event_type: str,
        active_app: str,
        media_saved: bool,
        summary: str,
        risk_level: str,
        details: Dict[str, object] | None = None,
    ) -> "AuditEvent":
        return cls(
            timestamp=datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            session_id=session_id,
            event_type=event_type,
            active_app=active_app,
            media_saved=media_saved,
            summary=summary,
            risk_level=risk_level,
            details=details or {},
        )


@dataclass
class EvaluationReport:
    precision: float
    recall: float
    readable_exposure_rate: float
    readable_exposure_duration_s: float
    avg_latency_ms: float
    peak_memory_mb: float
    battery_impact_score: float
    forensic_completeness: float
