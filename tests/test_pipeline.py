import json
import unittest
from pathlib import Path

from docushield.pipeline import DocushieldPipeline


class PipelineTests(unittest.TestCase):
    def test_pipeline_runs_and_writes_audit(self) -> None:
        tmp_dir = Path("artifacts/test_tmp")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        audit_path = tmp_dir / "audit.jsonl"
        scene_spec_path = tmp_dir / "unity_scene_spec.json"
        mockup_path = tmp_dir / "docushield_vr_mockup.svg"
        for path in (audit_path, scene_spec_path, mockup_path):
            if path.exists():
                path.unlink()

        pipeline = DocushieldPipeline(session_id="test-session", audit_path=audit_path)
        spec = pipeline.export_unity_scene_spec(scene_spec_path)
        mockup = pipeline.export_shareable_mockup(mockup_path)
        result = pipeline.run_sweep(limit_frames=8)

        self.assertEqual(result["frames_processed"], 8)
        self.assertGreaterEqual(result["mitigation_rate"], 0.0)
        self.assertLessEqual(result["mitigation_rate"], 1.0)
        self.assertGreaterEqual(result["average_risk_score"], 0.0)
        self.assertLessEqual(result["average_risk_score"], 1.0)
        self.assertIn("desk", {item["kind"] for item in spec["layout"]})
        self.assertIn("shelf", {item["kind"] for item in spec["layout"]})
        self.assertTrue(scene_spec_path.exists())
        self.assertTrue(mockup_path.exists())
        self.assertEqual(mockup["mockup_path"], str(mockup_path))
        self.assertIn("document", mockup_path.read_text(encoding="utf-8"))

        eval_report = result["evaluation"]
        self.assertGreaterEqual(eval_report["precision"], 0.0)
        self.assertLessEqual(eval_report["precision"], 1.0)
        self.assertGreaterEqual(eval_report["recall"], 0.0)
        self.assertLessEqual(eval_report["recall"], 1.0)
        self.assertTrue(audit_path.exists())
        lines = audit_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 8)
        first_event = json.loads(lines[0])
        self.assertIn("risk_level", first_event)
        self.assertIn("frame_source", first_event["details"])


if __name__ == "__main__":
    unittest.main()
