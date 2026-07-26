#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Optional
from PIL import Image
from reportlab.pdfgen import canvas


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def image_paths(in_dir: Path):
    return sorted([p for p in in_dir.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES])


def byte_size(paths):
    return sum(p.stat().st_size for p in paths if p.exists())


def mb(value):
    return round(value / 1024 / 1024, 2)


def to_rgb(img: Image.Image) -> Image.Image:
    if img.mode == "RGB":
        return img
    if img.mode in {"RGBA", "LA"} or (img.mode == "P" and "transparency" in img.info):
        background = Image.new("RGB", img.size, "white")
        background.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[-1])
        return background
    return img.convert("RGB")


def prepare_compact_images(source_paths, prepared_dir: Path, quality: int):
    prepared_dir.mkdir(parents=True, exist_ok=True)
    prepared = []
    for p in source_paths:
        out = prepared_dir / f"{p.stem}.jpg"
        if out.resolve() == p.resolve() and p.suffix.lower() in {".jpg", ".jpeg"}:
            prepared.append(p)
            continue
        img = to_rgb(Image.open(p))
        img.save(
            out,
            format="JPEG",
            quality=quality,
            subsampling=0,
            optimize=True,
            progressive=True,
        )
        prepared.append(out)
    return prepared


def prepare_lossless_pngs(source_paths, prepared_dir: Path):
    prepared_dir.mkdir(parents=True, exist_ok=True)
    prepared = []
    for p in source_paths:
        out = prepared_dir / f"{p.stem}.png"
        if out.resolve() == p.resolve() and p.suffix.lower() == ".png":
            prepared.append(p)
            continue
        img = Image.open(p)
        img.save(out, format="PNG", optimize=True, compress_level=9)
        prepared.append(out)
    return prepared


def prepared_images(source_paths, mode: str, prepared_dir: Optional[Path], quality: int):
    input_parent = source_paths[0].parent.parent
    if mode == "original":
        return source_paths, None
    if mode == "compact":
        target = prepared_dir or input_parent / f"images_jpeg_q{quality}"
        return prepare_compact_images(source_paths, target, quality), target
    if mode == "lossless":
        target = prepared_dir or input_parent / "images_lossless_png"
        return prepare_lossless_pngs(source_paths, target), target
    raise ValueError(f"Unsupported mode: {mode}")


def merge_images(pdf_images, out_pdf: Path):
    first_img = Image.open(pdf_images[0])
    page_width, page_height = first_img.size
    pdf = canvas.Canvas(str(out_pdf), pagesize=(page_width, page_height), pageCompression=1)

    for p in pdf_images:
        img = Image.open(p)
        width, height = img.size
        pdf.setPageSize((width, height))
        # Passing the file path lets ReportLab preserve JPEG compression for compact mode.
        pdf.drawImage(str(p), 0, 0, width=width, height=height)
        pdf.showPage()

    pdf.save()


def update_manifest(manifest_path: Path, payload: dict):
    if not manifest_path or not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["pdf"] = payload["pdf"]
    manifest["pdf_page_count"] = payload["page_count"]
    manifest.setdefault("pdf_outputs", {})[payload["mode"]] = payload
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Merge images into a single PDF.")
    ap.add_argument("--input-dir", required=True, help="Directory containing PNG/JPG images")
    ap.add_argument("--output", required=True, help="Output PDF path")
    ap.add_argument(
        "--mode",
        choices=["compact", "original", "lossless"],
        default="compact",
        help="PDF mode. compact converts copies to high-quality JPG first; original embeds the input files; lossless optimizes PNG copies first.",
    )
    ap.add_argument("--jpeg-quality", type=int, default=95, help="JPEG quality for compact mode.")
    ap.add_argument("--prepared-dir", help="Directory for generated JPG/PNG copies.")
    ap.add_argument("--manifest", help="Optional image_manifest.json to update with PDF output details.")
    ap.add_argument("--no-manifest-update", action="store_true", help="Do not auto-update image_manifest.json.")
    args = ap.parse_args()

    in_dir = Path(args.input_dir)
    out_pdf = Path(args.output)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    source_paths = image_paths(in_dir)
    if not source_paths:
        raise RuntimeError(f"No images found in {in_dir}")
    if not (1 <= args.jpeg_quality <= 100):
        raise RuntimeError("--jpeg-quality must be between 1 and 100")

    pdf_images, prepared_dir = prepared_images(
        source_paths,
        args.mode,
        Path(args.prepared_dir) if args.prepared_dir else None,
        args.jpeg_quality,
    )
    if len(pdf_images) != len(source_paths):
        raise RuntimeError("Prepared image count does not match source image count")

    merge_images(pdf_images, out_pdf)

    payload = {
        "pdf": str(out_pdf.resolve()),
        "mode": args.mode,
        "page_count": len(pdf_images),
        "source_image_count": len(source_paths),
        "prepared_dir": str(prepared_dir.resolve()) if prepared_dir else None,
        "jpeg_quality": args.jpeg_quality if args.mode == "compact" else None,
        "source_images_size_mb": mb(byte_size(source_paths)),
        "prepared_images_size_mb": mb(byte_size(pdf_images)),
        "pdf_size_mb": mb(out_pdf.stat().st_size),
    }

    print(f"PDF written to: {out_pdf}")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if not args.no_manifest_update:
        manifest_path = Path(args.manifest) if args.manifest else in_dir.parent / "image_manifest.json"
        update_manifest(manifest_path, payload)


if __name__ == "__main__":
    main()
