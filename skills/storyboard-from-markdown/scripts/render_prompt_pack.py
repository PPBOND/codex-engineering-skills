#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def render_page(page: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"## {page['id']} {page['title']}")
    lines.append("")
    lines.append(f"- visual_type: `{page['visual_type']}`")
    lines.append(f"- slug: `{page['slug']}`")
    if page.get("filename"):
        lines.append(f"- output_file: `{page['filename']}`")
    if page.get("text_hints"):
        lines.append("- text_hints:")
        for hint in page["text_hints"]:
            lines.append(f"  - {hint}")
    lines.append("")
    lines.append("```text")
    lines.append(page["prompt"])
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Render a readable markdown prompt pack from story_spec.json.")
    ap.add_argument("--input", required=True, help="Story spec JSON path")
    ap.add_argument("--output", required=True, help="Output markdown path")
    args = ap.parse_args()

    spec = json.loads(Path(args.input).read_text(encoding="utf-8"))
    pages: List[Dict[str, Any]] = spec.get("pages", [])
    title = spec.get("document_title", "Untitled Document")

    parts = [
        f"# {title} Prompt Pack",
        "",
        f"- total_pages: `{len(pages)}`",
        "- Save generated images into the sibling `images/` directory using the exact `output_file` names below.",
        "",
    ]
    for page in pages:
        parts.append(render_page(page))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(parts).strip() + "\n", encoding="utf-8")
    print(f"Wrote prompt pack to: {output_path}")


if __name__ == "__main__":
    main()
