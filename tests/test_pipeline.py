import unittest
from pathlib import Path

from docushield.pipeline import DocushieldPipeline


class PipelineTests(unittest.TestCase):
    def test_pipeline_runs_and_writes_audit(self) -> None:
        tmp_dir = Path("artifacts/test_tmp")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        audit_path = tmp_dir / "audit.jsonl"
        if audit_path.exists():
            audit_path.unlink()

        pipeline = DocushieldPipeline(session_id="test-session", audit_path=audit_path)
        result = pipeline.run_sweep(limit_frames=8)

        self.assertEqual(result["frames_processed"], 8)
        self.assertGreaterEqual(result["mitigation_rate"], 0.0)
        self.assertLessEqual(result["mitigation_rate"], 1.0)
        eval_report = result["evaluation"]
        self.assertGreaterEqual(eval_report["precision"], 0.0)
        self.assertLessEqual(eval_report["precision"], 1.0)
        self.assertGreaterEqual(eval_report["recall"], 0.0)
        self.assertLessEqual(eval_report["recall"], 1.0)
        self.assertTrue(audit_path.exists())
        lines = audit_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 8)


if __name__ == "__main__":
    unittest.main()
