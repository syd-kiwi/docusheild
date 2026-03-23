from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import Detection, Frame, SceneElement


class ShareablePrototypeExporter:
    """Create lightweight visual artifacts that can be shown without running Unity."""

    _COLORS = {
        "desk": "#8b5e3c",
        "shelf": "#6d4c41",
        "whiteboard": "#f5f5f5",
        "monitor": "#37474f",
        "document": "#fffde7",
        "envelope": "#fff3e0",
        "notebook": "#e3f2fd",
        "nonsensitive": "#cfd8dc",
    }

    def export_svg(self, frame: Frame, detections: Iterable[Detection], path: str | Path, risk_score: float) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        svg = self._build_svg(frame, list(detections), risk_score)
        output_path.write_text(svg, encoding="utf-8")
        return output_path

    def _build_svg(self, frame: Frame, detections: list[Detection], risk_score: float) -> str:
        layout_shapes = "\n".join(self._scene_element_svg(element) for element in frame.layout_elements)
        object_shapes = "\n".join(
            self._artifact_svg(obj.class_name, obj.bbox, obj.object_id) for obj in frame.objects
        )
        detection_shapes = "\n".join(self._detection_svg(detection) for detection in detections)
        risk_level = "HIGH" if risk_score >= 0.72 else "MEDIUM" if risk_score >= 0.4 else "LOW"
        banner_color = "#d32f2f" if risk_level == "HIGH" else "#f9a825" if risk_level == "MEDIUM" else "#2e7d32"
        detected_names = ", ".join(sorted({d.class_name for d in detections})) or "none"
        return f"""<svg xmlns='http://www.w3.org/2000/svg' width='{frame.width}' height='{frame.height}' viewBox='0 0 {frame.width} {frame.height}'>
  <rect width='100%' height='100%' fill='#f0f4f8'/>
  <rect x='0' y='0' width='{frame.width}' height='110' fill='#102a43'/>
  <text x='36' y='52' font-family='Arial, sans-serif' font-size='34' font-weight='700' fill='white'>DocuShield VR Prototype Mockup</text>
  <text x='36' y='88' font-family='Arial, sans-serif' font-size='20' fill='#d9e2ec'>Unity layout + YOLO/ONNX detection overlay preview</text>
  <rect x='950' y='24' rx='14' ry='14' width='290' height='58' fill='{banner_color}'/>
  <text x='972' y='60' font-family='Arial, sans-serif' font-size='24' font-weight='700' fill='white'>RISK {risk_level}: {risk_score:.2f}</text>
  {layout_shapes}
  {object_shapes}
  {detection_shapes}
  <rect x='40' y='620' rx='16' ry='16' width='1200' height='70' fill='#243b53' opacity='0.94'/>
  <text x='64' y='662' font-family='Arial, sans-serif' font-size='24' fill='white'>Detected sensitive artifacts: {detected_names}. User notification: reposition or blur protected items.</text>
</svg>
"""

    def _scene_element_svg(self, element: SceneElement) -> str:
        x, y, w, h = element.bbox
        fill = self._COLORS.get(element.kind, "#bcccdc")
        label_fill = "#1f2933" if element.kind == "whiteboard" else "white"
        return (
            f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='12' ry='12' fill='{fill}' stroke='#486581' stroke-width='3'/>"
            f"<text x='{x + 14}' y='{y + 28}' font-family='Arial, sans-serif' font-size='20' font-weight='700' fill='{label_fill}'>{element.kind.upper()}</text>"
        )

    def _artifact_svg(self, class_name: str, bbox: tuple[int, int, int, int], object_id: str) -> str:
        x, y, w, h = bbox
        fill = self._COLORS.get(class_name, "#d9e2ec")
        return (
            f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='8' ry='8' fill='{fill}' stroke='#52606d' stroke-width='2' opacity='0.95'/>"
            f"<text x='{x + 8}' y='{y + 24}' font-family='Arial, sans-serif' font-size='18' fill='#102a43'>{object_id}</text>"
        )

    def _detection_svg(self, detection: Detection) -> str:
        x, y, w, h = detection.bbox
        label = f"{detection.class_name} {detection.confidence:.2f}"
        return f"""
  <rect x='{x - 4}' y='{y - 4}' width='{w + 8}' height='{h + 8}' fill='none' stroke='#ef5350' stroke-width='5' stroke-dasharray='14 8'/>
  <rect x='{x - 4}' y='{max(112, y - 38)}' width='210' height='32' fill='#ef5350'/>
  <text x='{x + 8}' y='{max(135, y - 14)}' font-family='Arial, sans-serif' font-size='18' font-weight='700' fill='white'>{label}</text>
"""
