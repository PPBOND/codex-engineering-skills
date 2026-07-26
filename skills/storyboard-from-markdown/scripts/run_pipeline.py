#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent


def run(cmd):
    print("+", " ".join(str(x) for x in cmd))
    subprocess.run([str(x) for x in cmd], check=True)


def derive_default_workdir(input_md: Path) -> Path:
    return input_md.resolve().parent / "storyboard" / input_md.stem


def write_manifest(output_path: Path, payload: dict):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Prepare storyboard assets for pure model image generation.")
    ap.add_argument("--input-md", required=True, help="Input markdown path")
    ap.add_argument("--config", required=False, help="Config JSON path")
    ap.add_argument("--workdir", required=False, help="Working directory; default is <doc_dir>/storyboard/<doc_stem>")
    args = ap.parse_args()

    input_md = Path(args.input_md).resolve()
    workdir = Path(args.workdir).resolve() if args.workdir else derive_default_workdir(input_md)
    workdir.mkdir(parents=True, exist_ok=True)
    images_dir = workdir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    parsed_outline = workdir / "parsed_outline.json"
    story_spec = workdir / "story_spec.json"
    prompt_pack = workdir / "prompt_pack.md"
    manifest = workdir / "storyboard_run.json"
    suggested_pdf = workdir / f"{input_md.stem}_storyboard_compact.pdf"

    run([
        sys.executable,
        THIS_DIR / "parse_markdown.py",
        "--input", input_md,
        "--output", parsed_outline,
    ])

    build_cmd = [
        sys.executable,
        THIS_DIR / "build_story_spec.py",
        "--input", parsed_outline,
        "--output", story_spec,
    ]
    if args.config:
        build_cmd += ["--config", args.config]
    run(build_cmd)

    run([
        sys.executable,
        THIS_DIR / "render_prompt_pack.py",
        "--input", story_spec,
        "--output", prompt_pack,
    ])

    write_manifest(manifest, {
        "input_md": str(input_md),
        "config": str(Path(args.config).resolve()) if args.config else None,
        "workdir": str(workdir),
        "parsed_outline": str(parsed_outline),
        "story_spec": str(story_spec),
        "prompt_pack": str(prompt_pack),
        "images_dir": str(images_dir),
        "suggested_pdf": str(suggested_pdf),
        "suggested_pdf_mode": "compact",
        "suggested_pdf_command": "python scripts/images_to_pdf.py --input-dir <images_dir> --output <suggested_pdf>",
    })

    print("Storyboard preparation completed successfully.")
    print(f"Workdir: {workdir}")


if __name__ == "__main__":
    main()
