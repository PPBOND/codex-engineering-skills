#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import re
from typing import Dict, Any, List


def simple_slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[-\s]+", "_", value)
    return value.strip("_")


def clean_hint_text(value: str, max_chars: int) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("`", "")
    value = re.sub(r"[*#]+", "", value)
    value = re.sub(r"\s+", " ", value).strip(" -|:")
    if len(value) > max_chars:
        value = value[: max_chars - 3].rstrip() + "..."
    return value


def append_hint(hints: List[str], raw: str, max_chars: int) -> None:
    cleaned = clean_hint_text(raw, max_chars)
    if cleaned and cleaned not in hints:
        hints.append(cleaned)


def is_empty_label_line(value: str) -> bool:
    return bool(re.fullmatch(r"(目标|要求|goal|requirements?)[:：]?", value.strip(), flags=re.IGNORECASE))


def merge_hints(base: List[str], extra: List[str], max_items: int = 8) -> List[str]:
    merged: List[str] = []
    for item in base + extra:
        if item and item not in merged:
            merged.append(item)
        if len(merged) >= max_items:
            break
    return merged


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def has_keyword(text: str, keywords: List[str]) -> bool:
    normalized = normalize_text(text)
    return any(keyword in normalized for keyword in keywords)


def summarize_requirements(text: str) -> List[str]:
    bullets: List[str] = []
    plain_lines: List[str] = []
    max_chars = 140
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if re.fullmatch(r"[-|:\s]+", s):
            continue
        if is_empty_label_line(s):
            continue
        if s.startswith("### ") or s.startswith("#### "):
            append_hint(bullets, s.lstrip("#").strip(), max_chars)
            continue
        if s.startswith(">"):
            append_hint(bullets, s[1:].strip(), max_chars)
            continue
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            cells = [c for c in cells if c and not re.fullmatch(r"[-:]+", c)]
            if cells:
                append_hint(bullets, " / ".join(cells[:4]), max_chars)
            continue
        if s.startswith("-") or s.startswith("*"):
            append_hint(bullets, s[1:].strip(), max_chars)
        elif re.match(r"^\d+\.\s+", s):
            append_hint(bullets, re.sub(r"^\d+\.\s+", "", s), max_chars)
        elif s.startswith("目标") or s.startswith("要求"):
            append_hint(bullets, s, max_chars)
        else:
            plain_lines.append(clean_hint_text(s, max_chars))
    if not bullets:
        compact = " ".join(plain_lines)
        if compact:
            append_hint(bullets, compact, 220)
    elif plain_lines and len(bullets) < 8:
        for line in plain_lines[: max(0, 8 - len(bullets))]:
            append_hint(bullets, line, max_chars)
    return bullets[:8]


def infer_doc_category(title: str, intro_hints: List[str], sections: List[Dict[str, Any]]) -> str:
    combined = " ".join(
        [title] + intro_hints + [section.get("heading", "") for section in sections[:8]]
    )
    if has_keyword(combined, [
        "architecture", "design", "方案", "架构", "接口", "流程", "系统", "technical", "技术"
    ]):
        return "technical"
    if has_keyword(combined, [
        "roadmap", "milestone", "rollout", "plan", "timeline", "计划", "里程碑", "排期"
    ]):
        return "plan"
    if has_keyword(combined, [
        "meeting", "minutes", "decision", "action item", "next step", "会议", "纪要", "决策", "待办"
    ]):
        return "meeting"
    if has_keyword(combined, [
        "report", "metrics", "kpi", "result", "findings", "周报", "月报", "结果", "指标", "复盘"
    ]):
        return "report"
    return "general"


def infer_visual_type(title: str, content: str, cfg: Dict[str, Any]) -> str:
    overrides = cfg.get("title_visual_types", {})
    if title in overrides:
        return overrides[title]

    title_lower = title.lower()
    content_lower = content.lower()
    full_text = f"{title_lower} {content_lower}"

    if any(k in title_lower for k in ["错误码", "error code"]):
        return "error code matrix"
    if any(k in title_lower for k in ["可观测性", "观测", "metrics", "prometheus", "告警", "日志"]):
        return "observability dashboard"
    if any(k in title_lower for k in ["评审摘要", "摘要", "summary", "总结", "结论", "overview", "highlights"]):
        return "summary slide"
    if any(k in title_lower for k in ["goal", "goals", "objective", "objectives", "目标"]):
        return "goal roadmap"
    if any(k in title_lower for k in ["status", "update", "progress", "health", "状态", "进展", "周报", "月报"]):
        return "status dashboard"
    if any(k in title_lower for k in ["decision", "decisions", "决策", "结论"]):
        return "decision board"
    if any(k in title_lower for k in ["设计方案", "架构", "architecture", "solution", "system design"]):
        return "architecture diagram"
    if any(k in title_lower for k in ["流程", "时序", "数据流", "flow", "workflow", "步骤", "process"]):
        return "flow diagram"
    if any(k in title_lower for k in ["接口", "api", "proto", "contract"]):
        return "API contract slide"
    if any(k in title_lower for k in ["测试", "ut", "integration", "用例", "validation", "checklist"]):
        return "test plan slide"
    if any(k in title_lower for k in ["计划", "roadmap", "timeline", "milestone", "phase", "排期", "里程碑"]):
        return "timeline slide"
    if any(k in title_lower for k in ["风险", "risk", "issue", "blocker", "challenge"]):
        return "risk matrix"
    if any(k in title_lower for k in ["对比", "comparison", "tradeoff", "选型"]):
        return "comparison table"
    if any(k in title_lower for k in ["行动项", "todo", "action item", "next step", "next steps", "待办"]):
        return "action checklist"
    if any(k in title_lower for k in ["组织", "owner", "stakeholder", "team", "角色"]):
        return "stakeholder map"
    if any(k in full_text for k in ["架构", "architecture"]):
        return "architecture diagram"
    if any(k in full_text for k in ["数据流", "flow", "read path", "write path", "workflow", "process", "步骤"]):
        return "flow diagram"
    if any(k in full_text for k in ["接口", "api", "proto", "contract"]):
        return "API contract slide"
    if any(k in full_text for k in ["总结", "summary", "conclusion", "highlights", "overview"]):
        return "summary slide"
    if any(k in full_text for k in ["测试", "ut", "integration", "用例", "validation", "checklist"]):
        return "test plan slide"
    if any(k in full_text for k in ["背景", "pain point", "痛点", "context", "problem"]):
        return "problem overview illustration"
    if any(k in full_text for k in ["设计点", "highlight", "亮点", "takeaway", "key point"]):
        return "key points infographic"
    if any(k in full_text for k in ["timeline", "roadmap", "milestone", "phase", "里程碑", "排期"]):
        return "timeline slide"
    if any(k in full_text for k in ["risk", "blocker", "issue", "challenge", "风险"]):
        return "risk matrix"
    if any(k in full_text for k in ["comparison", "tradeoff", "option", "对比", "选型"]):
        return "comparison table"
    if any(k in full_text for k in ["action item", "next step", "todo", "待办", "行动项"]):
        return "action checklist"
    return str(cfg.get("default_visual_type", "concept summary illustration"))


def score_section(title: str, content: str) -> int:
    score = 0
    full_text = f"{title}\n{content}"
    text = normalize_text(full_text)

    if has_keyword(text, ["summary", "overview", "highlights", "abstract", "tl;dr", "摘要", "总结", "概览", "结论"]):
        score += 8
    if has_keyword(text, ["goal", "objective", "scope", "background", "context", "problem", "目标", "范围", "背景", "上下文", "问题"]):
        score += 6
    if has_keyword(text, ["decision", "proposal", "approach", "solution", "design", "architecture", "决策", "方案", "设计", "架构"]):
        score += 7
    if has_keyword(text, ["workflow", "process", "steps", "plan", "timeline", "roadmap", "milestone", "流程", "步骤", "计划", "里程碑", "排期"]):
        score += 6
    if has_keyword(text, ["result", "finding", "impact", "metric", "report", "comparison", "tradeoff", "结果", "发现", "影响", "指标", "对比", "权衡"]):
        score += 6
    if has_keyword(text, ["risk", "issue", "blocker", "action item", "next step", "todo", "风险", "问题", "阻塞", "待办", "行动项"]):
        score += 6
    if has_keyword(text, ["appendix", "reference", "glossary", "raw log", "附录", "参考", "术语", "原始日志", "变更记录", "changelog"]):
        score -= 6

    hint_count = len(summarize_requirements(content))
    score += min(hint_count, 4)

    content_len = len(content.strip())
    if content_len > 600:
        score += 2
    elif content_len > 120:
        score += 1
    elif content_len < 40:
        score -= 2

    return score


def select_sections(sections: List[Dict[str, Any]], slots: int, cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    if slots <= 0 or not sections:
        return []

    mode = str(cfg.get("selection_mode", "auto")).strip().lower() or "auto"
    auto_core_threshold = int(cfg.get("auto_core_threshold", 6))
    core_page_target = int(cfg.get("core_page_target", min(6, slots)))
    core_page_target = max(1, min(core_page_target, slots))

    if mode == "all":
        return sections[:slots]

    if mode == "core":
        selected_count = core_page_target
    elif len(sections) <= auto_core_threshold:
        selected_count = min(len(sections), slots)
    else:
        selected_count = core_page_target

    scored = [
        {
            "index": index,
            "score": score_section(section.get("heading", ""), section.get("content", "")),
            "section": section,
        }
        for index, section in enumerate(sections)
    ]
    if mode != "all" and len(sections) > auto_core_threshold:
        positive_or_neutral = [item for item in scored if item["score"] >= 0]
        if positive_or_neutral:
            scored = positive_or_neutral
            selected_count = min(selected_count, len(scored))
    top = sorted(scored, key=lambda item: (-item["score"], item["index"]))[:selected_count]
    selected_indexes = {item["index"] for item in top}
    return [section for index, section in enumerate(sections) if index in selected_indexes]


def build_cover_page(doc_title: str, intro_hints: List[str], doc_category: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    extra = cfg.get("cover_prompt_extra", "")
    style = cfg.get("style") or "clean editorial presentation, strong hierarchy, consistent visual system"
    prompt_parts = [
        f"Create the cover page for a visual summary document titled '{doc_title}'.",
        f"The document category is {doc_category}.",
        "The image should look like a polished presentation cover.",
        f"Global style: {style}.",
    ]
    if intro_hints:
        prompt_parts.append("Add a concise subtitle or supporting message based on: " + "; ".join(intro_hints))
    if extra:
        prompt_parts.append(extra)
    return {
        "page_no": 1,
        "id": "001",
        "slug": "cover",
        "filename": "001_cover.png",
        "title": doc_title,
        "visual_type": "cover page",
        "text_hints": [doc_title] + intro_hints,
        "prompt": " ".join(prompt_parts)
    }


def main():
    ap = argparse.ArgumentParser(description="Build story spec JSON from parsed markdown outline.")
    ap.add_argument("--input", required=True, help="Parsed outline JSON path")
    ap.add_argument("--config", required=False, help="Config JSON path")
    ap.add_argument("--output", required=True, help="Output story spec JSON path")
    args = ap.parse_args()

    outline = json.loads(Path(args.input).read_text(encoding="utf-8"))
    cfg = {}
    if args.config:
        cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))

    title = outline.get("title", "Untitled Document")
    intro_hints = summarize_requirements(outline.get("intro", ""))
    source_sections = outline.get("sections", [])
    doc_category = infer_doc_category(title, intro_hints, source_sections)
    pages = []
    page_no = 1
    generate_cover = cfg.get("generate_cover", True)

    if generate_cover:
        pages.append(build_cover_page(title, intro_hints, doc_category, cfg))
        page_no += 1

    page_prompt_extra = cfg.get("page_prompt_extra", "")
    style = cfg.get("style") or "clean editorial presentation, strong hierarchy, consistent visual system"
    include_page_number_hint = cfg.get("include_page_number_hint", True)
    max_pages = int(cfg.get("max_pages", 20))
    include_titles = [str(x).strip() for x in cfg.get("include_titles", []) if str(x).strip()]
    include_title_set = set(include_titles)
    skip_titles = {x.strip() for x in cfg.get("skip_titles", []) if str(x).strip()}
    title_prompt_extras = cfg.get("title_prompt_extras", {})
    title_hint_overrides = cfg.get("title_hint_overrides", {})
    pending_intro_hints = intro_hints if not generate_cover else []
    available_slots = max(0, max_pages - len(pages))

    candidate_sections = []
    for section in source_sections:
        heading = section.get("heading", "").strip()
        if include_title_set and heading not in include_title_set:
            continue
        if heading in skip_titles:
            continue
        candidate_sections.append(section)

    if include_title_set:
        selected_sections = candidate_sections[:available_slots]
    else:
        selected_sections = select_sections(candidate_sections, available_slots, cfg)

    for section in selected_sections:
        heading = section.get("heading", f"Page {page_no}")
        content = section.get("content", "")
        if heading in title_hint_overrides:
            bullets = []
            for item in title_hint_overrides[heading]:
                append_hint(bullets, str(item), 140)
        else:
            bullets = summarize_requirements(content)
        if pending_intro_hints:
            bullets = merge_hints(pending_intro_hints, bullets)
        visual_type = infer_visual_type(heading, content, cfg)
        page_id = f"{page_no:03d}"
        slug = simple_slugify(heading) or f"page_{page_id}"
        filename = f"{page_id}_{slug}.png"
        prompt_parts = [
            f"Create page {page_no} of a multi-page visual summary document.",
            f"Page title: '{heading}'.",
            f"Document category: {doc_category}.",
            f"Visual type: {visual_type}.",
            f"Global style: {style}.",
            "Make the page presentation-ready, visually clear, and suitable for inclusion in a PDF report."
        ]
        if include_page_number_hint:
            prompt_parts.append(f"Keep consistency with the rest of the document. This is page {page_no}.")
        if bullets:
            prompt_parts.append("Core information to preserve: " + "; ".join(bullets))
        if page_prompt_extra:
            prompt_parts.append(page_prompt_extra)
        if heading in title_prompt_extras:
            prompt_parts.append(str(title_prompt_extras[heading]).strip())

        pages.append({
            "page_no": page_no,
            "id": page_id,
            "slug": slug,
            "filename": filename,
            "title": heading,
            "visual_type": visual_type,
            "text_hints": [heading] + bullets,
            "prompt": " ".join(prompt_parts)
        })
        pending_intro_hints = []
        page_no += 1

    spec = {
        "document_title": title,
        "document_category": doc_category,
        "selection_mode": str(cfg.get("selection_mode", "auto")).strip().lower() or "auto",
        "source_section_count": len(source_sections),
        "selected_section_count": len(selected_sections),
        "config": cfg,
        "pages": pages
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote story spec to: {out}")


if __name__ == "__main__":
    main()
