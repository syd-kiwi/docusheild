# DocuShield Prototype

This repository contains a runnable prototype:

- A Unity-ready virtual home-office scene spec with a realistic desk, shelf, whiteboard, and paper artifacts.
- A YOLO-style detector facade that models how ONNX Runtime in Unity will consume rendered frames.
- Per-frame output containing bounding boxes, class labels, confidence scores, risk levels, and user notifications.
- Real-time mitigation overlays triggered by risk scoring.
- A shareable SVG mockup plus a Unity prototype kit you can show without building the full product.
- A policy layer with work mode, sharing mode, and quick override behavior.
- Local JSONL audit logging of camera-access-relevant security events.
- Evaluation metrics for detection quality, privacy exposure reduction, and system performance.

## Architecture mapping

1. **Unity VR environment** renders a realistic office layout to a `RenderTexture`.
2. **Frame handoff** copies the rendered image into a tensor-compatible buffer.
3. **YOLO + ONNX Runtime** identifies `document`, `envelope`, `notebook`, and `whiteboard` objects.
4. **Risk engine** uses confidence scores plus scene stress factors to compute a risk score.
5. **Mitigation and notification** apply blur overlays and inform the user when thresholds are exceeded.

The current codebase simulates the Unity-side rendering and inference contract in Python so the data flow, outputs, and policy behavior can be validated before a full Unity client is added.

## Shareable demo assets

- `shareables/docushield_vr_mockup.svg`: presentation-ready visual mockup of the VR scene with detections and a risk banner.
- `unity_prototype/`: importable Unity starter kit with scene bootstrap, detector contract, and overlay demo scripts.
- `artifacts/unity_scene_spec.json`: exported scene layout and detector handoff contract.

## Run

```bash
python -m pip install -e .
docushield-run \
  --frames 20 \
  --audit-path artifacts/audit_log.jsonl \
  --scene-spec-path artifacts/unity_scene_spec.json \
  --mockup-path shareables/docushield_vr_mockup.svg
```

## Outputs

- `artifacts/unity_scene_spec.json`: Unity scene layout and detector handoff contract.
- `artifacts/audit_log.jsonl`: structured event log for detections and mitigations.
- `shareables/docushield_vr_mockup.svg`: shareable visual concept image.
- CLI JSON output: frame count, mitigation rate, average risk score, latest user notification, and evaluation metrics.

## Test

```bash
python -m pip install -e .
python -m pytest -q
```
