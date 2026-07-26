#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import re
from typing import List, Dict, Any


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def parse_heading(line: str):
    match = HEADING_RE.match(line)
    if not match:
        return None
    return len(match.group(1)), match.group(2).strip()


def detect_section_level(lines: List[str]) -> int | None:
    levels: List[int] = []
    title_seen = False
    for raw in lines:
        parsed = parse_heading(raw.rstrip())
        if not parsed:
            continue
        level, heading = parsed
        if level == 1 and heading and not title_seen:
            title_seen = True
            continue
        if level > 1 and heading:
            levels.append(level)
    if not levels:
        return None
    return min(levels)


def parse_sections(markdown_text: str) -> Dict[str, Any]:
    lines = markdown_text.splitlines()
    title = None
    intro_lines: List[str] = []
    sections: List[Dict[str, Any]] = []
    current = None
    section_level = detect_section_level(lines)

    for raw in lines:
        line = raw.rstrip()
        parsed = parse_heading(line)
        if parsed:
            level, heading = parsed
        else:
            level, heading = None, None

        if level == 1 and title is None:
            title = heading
            continue

        if section_level is not None and level == section_level:
            if current:
                current["content"] = current["content"].strip()
                sections.append(current)
            current = {
                "heading": heading,
                "content": ""
            }
            continue

        if current is not None:
            current["content"] += (line + "\n")
        else:
            if line.strip():
                intro_lines.append(line)

    if current:
        current["content"] = current["content"].strip()
        sections.append(current)

    if section_level is None:
        fallback_content = "\n".join(intro_lines).strip()
        if fallback_content:
            sections = [{"heading": title or "Document", "content": fallback_content}]
        else:
            sections = []

    return {
        "title": title or "Untitled Document",
        "intro": "\n".join(intro_lines).strip(),
        "section_level": section_level,
        "sections": sections
    }


def main():
    ap = argparse.ArgumentParser(description="Parse markdown into a simple outline JSON.")
    ap.add_argument("--input", required=True, help="Input markdown path")
    ap.add_argument("--output", required=True, help="Output JSON path")
    args = ap.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    text = input_path.read_text(encoding="utf-8")
    parsed = parse_sections(text)
    output_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote parsed outline to: {output_path}")


if __name__ == "__main__":
    main()
