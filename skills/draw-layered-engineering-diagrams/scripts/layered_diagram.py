from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageDraw, ImageFont


W, H = 2000, 1400
PAPER = "#FFFFFF"
INK = "#16191D"
MUTED = "#66727D"
GRID = "#D8DEE5"
SOFT = "#F6F7F9"

PALETTE = {
    "blue": ("#E5F2FC", "#1976C5", "#0B5D9A"),
    "green": ("#EAF6E7", "#3D9140", "#28732E"),
    "orange": ("#FFF1DC", "#EF7D00", "#B85B00"),
    "purple": ("#F3E6F7", "#8635B5", "#6D278F"),
    "red": ("#FDEBEC", "#E33D48", "#A82530"),
    "gray": ("#F1F3F5", "#7E8B98", "#4F5C67"),
    "teal": ("#E5F6F8", "#1596A8", "#0A7180"),
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def rounded(draw: ImageDraw.ImageDraw, bounds, fill, outline, width=2, radius=14) -> None:
    draw.rounded_rectangle(bounds, radius=radius, fill=fill, outline=outline, width=width)


def _wrap(draw: ImageDraw.ImageDraw, text: str, face, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for char in paragraph:
            candidate = current + char
            if current and draw.textlength(candidate, font=face) > max_width:
                lines.append(current)
                current = char
            else:
                current = candidate
        if current:
            lines.append(current)
    return lines


def wrapped(draw: ImageDraw.ImageDraw, xy, text: str, face, fill, max_width: int, gap: int = 5, max_lines: int | None = None) -> int:
    x, y = xy
    lines = _wrap(draw, text, face, max_width)
    if max_lines is not None:
        lines = lines[:max_lines]
    line_height = face.size + gap
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        y += line_height
    return y


def center_text(draw: ImageDraw.ImageDraw, bounds, text: str, face, fill) -> None:
    x1, y1, x2, y2 = bounds
    lines = _wrap(draw, text, face, x2 - x1)
    line_height = face.size + 4
    y = y1 + ((y2 - y1) - len(lines) * line_height) / 2
    for line in lines:
        width = draw.textlength(line, font=face)
        draw.text((x1 + ((x2 - x1) - width) / 2, y), line, font=face, fill=fill)
        y += line_height


def plate(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(image)
    rounded(draw, (24, 18, W - 24, H - 18), PAPER, GRID, 2, 30)
    title_face = font(38, True)
    subtitle_face = font(18)
    draw.text(((W - draw.textlength(title, font=title_face)) / 2, 43), title, font=title_face, fill=INK)
    draw.text(((W - draw.textlength(subtitle, font=subtitle_face)) / 2, 96), subtitle, font=subtitle_face, fill=MUTED)
    draw.line((70, 143, W - 70, 143), fill="#E5E9EE", width=2)
    return image, draw


def layer(draw: ImageDraw.ImageDraw, bounds, title: str, color: str = "blue", fill: str | None = None, title_size: int = 23) -> None:
    palette = PALETTE[color]
    rounded(draw, bounds, fill or PAPER, palette[1], 3, 18)
    draw.text((bounds[0] + 22, bounds[1] + 13), title, font=font(title_size, True), fill=INK)


def card(draw: ImageDraw.ImageDraw, bounds, title: str, body: str = "", color: str = "blue", title_size: int = 19, body_size: int = 14, center: bool = False) -> None:
    palette = PALETTE[color]
    rounded(draw, bounds, palette[0], palette[1], 2, 14)
    x1, y1, x2, y2 = bounds
    if center:
        center_text(draw, (x1 + 12, y1 + 8, x2 - 12, y1 + 44), title, font(title_size, True), palette[2])
        if body:
            center_text(draw, (x1 + 14, y1 + 43, x2 - 14, y2 - 8), body, font(body_size), INK)
        return
    draw.text((x1 + 16, y1 + 12), title, font=font(title_size, True), fill=palette[2])
    if body:
        wrapped(draw, (x1 + 16, y1 + 47), body, font(body_size), INK, x2 - x1 - 32, gap=5)


def _line(draw: ImageDraw.ImageDraw, p1, p2, fill, width: int, dashed: bool) -> None:
    if not dashed:
        draw.line((p1, p2), fill=fill, width=width)
        return
    x1, y1 = p1
    x2, y2 = p2
    length = math.hypot(x2 - x1, y2 - y1)
    if not length:
        return
    dash, gap = 12, 8
    dx, dy = (x2 - x1) / length, (y2 - y1) / length
    cursor = 0.0
    while cursor < length:
        end = min(cursor + dash, length)
        draw.line((x1 + dx * cursor, y1 + dy * cursor, x1 + dx * end, y1 + dy * end), fill=fill, width=width)
        cursor += dash + gap


def arrow(draw: ImageDraw.ImageDraw, points: Sequence[tuple[int, int]], color: str = "blue", width: int = 4, dashed: bool = False) -> None:
    stroke = PALETTE[color][1]
    for start, end in zip(points, points[1:]):
        _line(draw, start, end, stroke, width, dashed)
    if len(points) < 2:
        return
    x1, y1 = points[-2]
    x2, y2 = points[-1]
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 13
    left = (x2 - size * math.cos(angle - math.pi / 6), y2 - size * math.sin(angle - math.pi / 6))
    right = (x2 - size * math.cos(angle + math.pi / 6), y2 - size * math.sin(angle + math.pi / 6))
    draw.polygon([(x2, y2), left, right], fill=stroke)


def footer(draw: ImageDraw.ImageDraw, summary: str, legend: Iterable[tuple[str, str, bool]] | None = None) -> None:
    items = list(legend or [("主路径", "blue", False), ("索引 / 查询", "green", False), ("控制 / 恢复", "purple", True), ("持久化", "orange", False)])
    rounded(draw, (70, H - 105, W - 70, H - 38), SOFT, GRID, 1, 12)
    y = H - 82
    x = 100
    for label, color, dashed in items:
        _line(draw, (x, y), (x + 62, y), PALETTE[color][1], 5 if not dashed else 4, dashed)
        draw.text((x + 76, y - 13), label, font=font(14), fill=INK)
        x += 250
    draw.text((x + 5, y - 14), "一句话：", font=font(15, True), fill=PALETTE["green"][2])
    wrapped(draw, (x + 90, y - 17), summary, font(14), INK, W - x - 180, gap=3, max_lines=2)


def demo(output: Path) -> None:
    image, draw = plate("工程流程示例｜从请求到持久化", "用分层、颜色和线型区分数据路径、索引路径与控制边界")
    card(draw, (260, 175, 1740, 255), "上层请求", "具体 key、范围、长度与目标", "gray")
    arrow(draw, [(1000, 255), (1000, 300)])
    layer(draw, (90, 305, 1450, 570), "接口与索引层", "blue", "#F3F9FD")
    card(draw, (135, 380, 520, 520), "API", "解析请求并校验边界", "blue")
    card(draw, (590, 380, 975, 520), "Index", "定位一个或多个结果", "green")
    card(draw, (1045, 380, 1405, 520), "Result", "明确返回数据还是地址", "orange")
    arrow(draw, [(520, 450), (580, 450)], "blue")
    arrow(draw, [(975, 450), (1035, 450)], "green")
    layer(draw, (1500, 305, 1910, 570), "控制边界", "purple", "#FAF5FC")
    card(draw, (1535, 380, 1875, 520), "异步 / 恢复", "用虚线连接，不混入主路径", "purple")
    arrow(draw, [(1405, 450), (1490, 450)], "purple", dashed=True)
    arrow(draw, [(760, 570), (760, 620)], "orange")
    layer(draw, (90, 625, 1910, 900), "执行与持久化", "orange", "#FFF9F0")
    card(draw, (135, 700, 600, 840), "Execution", "展开关键步骤与顺序", "blue")
    card(draw, (760, 700, 1225, 840), "Store / Env", "append、fsync、rename", "orange")
    card(draw, (1385, 700, 1865, 840), "Media", "文件、对象或远端介质", "green")
    arrow(draw, [(600, 770), (750, 770)], "blue")
    arrow(draw, [(1225, 770), (1375, 770)], "orange")
    layer(draw, (90, 950, 1910, 1225), "结论与风险", "red", "#FFF8F7")
    card(draw, (135, 1025, 900, 1165), "已验证结论", "只写源码或测试能够证明的事实。", "green")
    card(draw, (1080, 1025, 1865, 1165), "WARN", "风险必须说明触发条件、影响与建议验证方式。", "red")
    footer(draw, "先讲请求如何流动，再讲控制边界；每个箭头都必须有明确语义。")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, "PNG", optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Reusable primitives for layered engineering diagrams")
    parser.add_argument("--demo", action="store_true", help="render a reference demo")
    parser.add_argument("--output", type=Path, default=Path("layered-diagram-demo.png"))
    args = parser.parse_args()
    if not args.demo:
        parser.error("pass --demo, or import this module from a task-specific generator")
    demo(args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()
