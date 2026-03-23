from __future__ import annotations

import argparse
import json
from uuid import uuid4

from .pipeline import DocushieldPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DocuShield virtual-environment evaluation")
    parser.add_argument("--frames", type=int, default=20, help="Number of frames to evaluate")
    parser.add_argument("--audit-path", default="artifacts/audit_log.jsonl", help="Path to JSONL audit log")
    parser.add_argument(
        "--scene-spec-path",
        default="artifacts/unity_scene_spec.json",
        help="Path to the exported Unity scene specification JSON",
    )
    parser.add_argument(
        "--mockup-path",
        default="shareables/docushield_vr_mockup.svg",
        help="Path to the shareable SVG mockup",
    )
    args = parser.parse_args()

    pipeline = DocushieldPipeline(session_id=str(uuid4()), audit_path=args.audit_path)
    pipeline.export_unity_scene_spec(args.scene_spec_path)
    mockup = pipeline.export_shareable_mockup(args.mockup_path)
    result = pipeline.run_sweep(limit_frames=args.frames)
    result["unity_integration"]["scene_spec_path"] = args.scene_spec_path
    result["shareable_mockup"] = mockup
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
