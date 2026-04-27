from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageDraw
from ultralytics import YOLO


DEFAULT_ALLOWED_CLASSES: tuple[str, ...] = (
    "person",
    "car",
    "bicycle",
    "motorcycle",
    "bus",
    "truck",
    "cat",
    "dog",
)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


@dataclass(frozen=True)
class DetectionRow:
    image_name: str
    class_name: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run YOLOv10 on every image in a folder, keep only detections from an allow-list, "
            "save detections to CSV, and write annotated images to an output folder."
        )
    )
    parser.add_argument("--input-dir", required=True, help="Folder containing input images.")
    parser.add_argument("--output-dir", default="outputs", help="Folder for annotated images + CSV output.")
    parser.add_argument("--model", default="yolov10n.pt", help="Path/name of YOLOv10 model weights.")
    parser.add_argument(
        "--allowed-classes",
        nargs="+",
        default=list(DEFAULT_ALLOWED_CLASSES),
        help="Only detections from these classes are saved (default is built-in allow-list).",
    )
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold (0.0 - 1.0).")
    parser.add_argument(
        "--csv-name",
        default="detections.csv",
        help="CSV filename written inside --output-dir.",
    )
    return parser.parse_args()


def iter_images(input_dir: Path) -> Iterable[Path]:
    for path in sorted(input_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            yield path


def save_csv(csv_path: Path, rows: Sequence[DetectionRow]) -> None:
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["image_name", "class_name", "confidence", "x1", "y1", "x2", "y2"])
        for row in rows:
            writer.writerow(
                [
                    row.image_name,
                    row.class_name,
                    f"{row.confidence:.6f}",
                    f"{row.x1:.2f}",
                    f"{row.y1:.2f}",
                    f"{row.x2:.2f}",
                    f"{row.y2:.2f}",
                ]
            )


def run_detector(
    input_dir: Path,
    output_dir: Path,
    model_name_or_path: str,
    allowed_classes: Sequence[str],
    conf_threshold: float,
    csv_name: str,
) -> Path:
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory does not exist or is not a directory: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    annotated_dir = output_dir / "annotated"
    annotated_dir.mkdir(parents=True, exist_ok=True)

    allow_set = {name.lower() for name in allowed_classes}
    model = YOLO(model_name_or_path)
    rows: list[DetectionRow] = []

    image_paths = list(iter_images(input_dir))
    if not image_paths:
        raise ValueError(f"No supported images found in: {input_dir}")

    for image_path in image_paths:
        results = model.predict(source=str(image_path), conf=conf_threshold, verbose=False)
        if not results:
            continue

        result = results[0]
        names = result.names

        keep_indexes: list[int] = []
        for idx, cls_id in enumerate(result.boxes.cls.tolist()):
            class_name = names[int(cls_id)]
            if class_name.lower() in allow_set:
                keep_indexes.append(idx)

        annotated_image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(annotated_image)

        for idx in keep_indexes:
            class_name = names[int(result.boxes.cls[idx].item())]
            confidence = float(result.boxes.conf[idx].item())
            x1, y1, x2, y2 = result.boxes.xyxy[idx].tolist()
            rows.append(
                DetectionRow(
                    image_name=image_path.name,
                    class_name=class_name,
                    confidence=confidence,
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                )
            )

            draw.rectangle([(x1, y1), (x2, y2)], outline="red", width=3)
            draw.text((x1, max(0, y1 - 14)), f"{class_name} {confidence:.2f}", fill="red")

        annotated_path = annotated_dir / image_path.name
        annotated_image.save(annotated_path)

    csv_path = output_dir / csv_name
    save_csv(csv_path, rows)
    return csv_path


def main() -> None:
    args = parse_args()
    csv_path = run_detector(
        input_dir=Path(args.input_dir),
        output_dir=Path(args.output_dir),
        model_name_or_path=args.model,
        allowed_classes=args.allowed_classes,
        conf_threshold=args.conf,
        csv_name=args.csv_name,
    )
    print(f"Saved detection CSV: {csv_path}")


if __name__ == "__main__":
    main()
