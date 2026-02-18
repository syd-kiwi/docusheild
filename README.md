# DocuShield Prototype

This repository contains a runnable prototype implementing the requested end-to-end strategy:

- Virtual home-office scene generation with deterministic ground truth labels.
- YOLO-style detector interface designed for ONNX Runtime deployment.
- Real-time mitigation overlays triggered by risk scoring.
- Policy layer with work mode, sharing mode, and quick override behavior.
- Local JSONL audit logging of camera-access-relevant security events.
- Evaluation metrics for detection quality, privacy exposure reduction, and system performance.

## Run

```bash
python -m pip install -e .
docushield-run --frames 20 --audit-path artifacts/audit_log.jsonl
```

## Test

```bash
python -m pip install -e .
python -m pytest -q
```
