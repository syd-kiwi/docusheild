from __future__ import annotations

from .models import PolicyConfig, RiskAssessment


class PolicyEngine:
    def __init__(self, config: PolicyConfig) -> None:
        self.config = config

    def should_run_detection(self) -> bool:
        return self.config.work_mode_enabled and not self.config.quick_override

    def should_mitigate(self, assessment: RiskAssessment) -> bool:
        if self.config.quick_override:
            return False
        threshold = (
            self.config.sharing_threshold
            if self.config.sharing_active
            else self.config.mitigation_threshold
        )
        return assessment.risk_score >= threshold

    def mitigation_strength(self) -> float:
        if self.config.sharing_active:
            return 0.95
        if self.config.work_mode_enabled:
            return 0.75
        return 0.4
