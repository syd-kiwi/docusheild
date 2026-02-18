from __future__ import annotations

import argparse
import json
from uuid import uuid4

from .pipeline import DocushieldPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DocuShield virtual-environment evaluation")
    parser.add_argument("--frames", type=int, default=20, help="Number of frames to evaluate")
    parser.add_argument("--audit-path", default="artifacts/audit_log.jsonl", help="Path to JSONL audit log")
    args = parser.parse_args()

    pipeline = DocushieldPipeline(session_id=str(uuid4()), audit_path=args.audit_path)
    result = pipeline.run_sweep(limit_frames=args.frames)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
