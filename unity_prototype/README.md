# DocuShield Unity Prototype Kit

This folder is a lightweight Unity prototype starter that you can share with teammates or import into a fresh Unity URP/3D project.

## Included pieces

- `Assets/Scripts/DocuShieldSceneBootstrap.cs`: creates a simple desk/shelf/whiteboard office scene in code.
- `Assets/Scripts/DocuShieldDetectorContract.cs`: documents the rendered-frame handoff and mock detector output shape.
- `Assets/Scripts/DocuShieldOverlayDemo.cs`: renders label panels and risk notifications from detections.
- `Assets/StreamingAssets/docushield_scene_spec.json`: scene and detection-target metadata exported from the Python prototype.

## Quick demo flow

1. Create a new Unity 2022/2023 3D or URP project.
2. Copy the `Assets` folder from this directory into the Unity project.
3. Create an empty GameObject named `DocuShieldPrototype` and attach:
   - `DocuShieldSceneBootstrap`
   - `DocuShieldDetectorContract`
   - `DocuShieldOverlayDemo`
4. Press Play to generate the office scene and a mock sensitive-object alert overlay.

## Notes

- This is a visual/shareable prototype, not a complete ONNX Runtime integration.
- The Python code in `src/docushield` remains the source of truth for risk scoring and synthetic frame generation.
