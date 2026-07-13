#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


COMPOSITOR_VERSION = "第2版"
COMPOSITOR_ID = "card_compositor_v2"

ROOT = Path(__file__).resolve().parents[2]
CARD_TABLE = ROOT / "规则" / "V1.3-基础卡表.md"
FRAME_PATH = ROOT / "测试版" / "卡牌合成第2版_透明边框_815x1110.png"

CANVAS_SIZE = (815, 1110)
BACKGROUND = (16, 36, 61)
ART_BOX = (55, 97, 763, 840)
ICON_BOX = (76, 858, 220, 1002)
LEVEL_BOX = (43, 45, 167, 167)
NAME_BOX = (170, 55, 715, 125)
ENGLISH_NAME_BOX = (170, 120, 715, 170)
SKILL_BOX = (235, 855, 735, 925)
ENGLISH_SKILL_BOX = (235, 935, 735, 1015)
CARD_NUMBER_POS = (63, 1052)
COPYRIGHT_RIGHT = 752


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="使用第2版透明边框合成单张妖怪卡。")
    parser.add_argument("--card", default="金鼻白毛老鼠精", help="卡表中的中文卡名")
    return parser.parse_args()


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
        Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
    ]
    for path in candidates:
        if path.exists():
            index = 1 if bold and path.name == "PingFang.ttc" else 0
            return ImageFont.truetype(str(path), size, index=index)
    return ImageFont.load_default()


def pipe_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def load_card(name: str) -> dict:
    stars: int | None = None
    for raw_line in CARD_TABLE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        heading = re.match(r"## .+、([1-5])星妖怪", line)
        if heading:
            stars = int(heading.group(1))
            continue
        if stars is None or not line.startswith("|") or "---" in line or "卡号" in line:
            continue
        cells = pipe_cells(line)
        if len(cells) < 6 or cells[1] != name:
            continue
        return {
            "card_number": cells[0],
            "name": cells[1],
            "english_name": cells[2],
            "count": int(cells[3]),
            "stars": stars,
            "skill_text": cells[-2],
            "english_skill_text": cells[-1],
        }
    raise ValueError(f"未在最新卡表中找到妖怪卡：{name}")


def card_folder(card: dict) -> Path:
    return ROOT / "妖怪志" / card["name"] / "第2版"


def art_path(card: dict) -> Path:
    return card_folder(card) / f"{card['name']}_第2版_纯插画.png"


def icon_path(card: dict) -> Path:
    return card_folder(card) / f"{card['name']}_第2版_技能图标.png"


def output_path(card: dict) -> Path:
    return card_folder(card) / f"{card['name']}_第2版_完整卡牌.png"


def cover_crop(image: Image.Image, size: tuple[int, int], focus_y: float = 0.38) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = max(0, (resized.width - target_w) // 2)
    top = max(0, min(resized.height - target_h, round((resized.height - target_h) * focus_y)))
    return resized.crop((left, top, left + target_w, top + target_h))


def contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    return copy


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, minimum: int) -> ImageFont.ImageFont:
    for size in range(start, minimum - 1, -1):
        candidate = font(size, bold=True)
        box = draw.textbbox((0, 0), text, font=candidate, stroke_width=1)
        if box[2] - box[0] <= max_width:
            return candidate
    return font(minimum, bold=True)


def draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    text_font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    stroke_width: int = 0,
    stroke_fill: tuple[int, int, int] | None = None,
) -> None:
    left, top, right, bottom = box
    bounds = draw.textbbox((0, 0), text, font=text_font, stroke_width=stroke_width)
    x = left + (right - left - (bounds[2] - bounds[0])) / 2 - bounds[0]
    y = top + (bottom - top - (bounds[3] - bounds[1])) / 2 - bounds[1]
    draw.text(
        (x, y), text, font=text_font, fill=fill,
        stroke_width=stroke_width, stroke_fill=stroke_fill,
    )


def wrap_english(draw: ImageDraw.ImageDraw, text: str, width: int, text_font: ImageFont.ImageFont) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        bounds = draw.textbbox((0, 0), candidate, font=text_font)
        if bounds[2] - bounds[0] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def compose(card: dict) -> Image.Image:
    required = (FRAME_PATH, art_path(card), icon_path(card))
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"缺少第2版资源：{'、'.join(missing)}")

    canvas = Image.new("RGBA", CANVAS_SIZE, BACKGROUND + (255,))

    artwork = Image.open(art_path(card)).convert("RGB")
    art_w, art_h = ART_BOX[2] - ART_BOX[0], ART_BOX[3] - ART_BOX[1]
    artwork = cover_crop(artwork, (art_w, art_h))
    canvas.paste(artwork, ART_BOX[:2])

    icon = Image.open(icon_path(card)).convert("RGBA")
    icon_w, icon_h = ICON_BOX[2] - ICON_BOX[0], ICON_BOX[3] - ICON_BOX[1]
    icon = contain(icon, (icon_w, icon_h))
    icon_x = ICON_BOX[0] + (icon_w - icon.width) // 2
    icon_y = ICON_BOX[1] + (icon_h - icon.height) // 2
    canvas.alpha_composite(icon, (icon_x, icon_y))

    frame = Image.open(FRAME_PATH).convert("RGBA")
    if frame.size != CANVAS_SIZE:
        raise ValueError(f"边框尺寸错误：{frame.size}，应为 {CANVAS_SIZE}")
    canvas.alpha_composite(frame)

    draw = ImageDraw.Draw(canvas)
    draw_centered(
        draw, str(card["stars"]), LEVEL_BOX, font(68, bold=True),
        (255, 255, 255), stroke_width=5, stroke_fill=(50, 30, 18),
    )
    name_font = fit_font(draw, card["name"], NAME_BOX[2] - NAME_BOX[0] - 20, 48, 28)
    draw_centered(draw, card["name"], NAME_BOX, name_font, (49, 29, 18))
    english_name_font = fit_font(
        draw, card["english_name"], ENGLISH_NAME_BOX[2] - ENGLISH_NAME_BOX[0] - 20, 24, 16,
    )
    draw_centered(draw, card["english_name"], ENGLISH_NAME_BOX, english_name_font, (83, 49, 28))

    skill_font = fit_font(draw, card["skill_text"], SKILL_BOX[2] - SKILL_BOX[0] - 12, 30, 21)
    draw_centered(draw, card["skill_text"], SKILL_BOX, skill_font, (55, 34, 22))

    english_font = font(17)
    english_lines = wrap_english(
        draw, card["english_skill_text"],
        ENGLISH_SKILL_BOX[2] - ENGLISH_SKILL_BOX[0] - 10,
        english_font,
    )
    line_height = 24
    total_height = len(english_lines) * line_height
    y = ENGLISH_SKILL_BOX[1] + (ENGLISH_SKILL_BOX[3] - ENGLISH_SKILL_BOX[1] - total_height) / 2
    for line in english_lines:
        draw_centered(
            draw, line,
            (ENGLISH_SKILL_BOX[0], round(y), ENGLISH_SKILL_BOX[2], round(y + line_height)),
            english_font, (78, 49, 29),
        )
        y += line_height

    small_font = font(12)
    draw.text(CARD_NUMBER_POS, card["card_number"], font=small_font, fill=(226, 199, 136))
    copyright_text = "© 2026 夕妖：抢地盘"
    bounds = draw.textbbox((0, 0), copyright_text, font=small_font)
    draw.text(
        (COPYRIGHT_RIGHT - (bounds[2] - bounds[0]), CARD_NUMBER_POS[1]),
        copyright_text, font=small_font, fill=(226, 199, 136),
    )

    return canvas.convert("RGB")


def main() -> None:
    args = parse_args()
    card = load_card(args.card)
    image = compose(card)
    destination = output_path(card)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, dpi=(300, 300), optimize=True)
    print(json.dumps({
        "compositor_version": COMPOSITOR_VERSION,
        "compositor_id": COMPOSITOR_ID,
        "card_number": card["card_number"],
        "card": card["name"],
        "english_name": card["english_name"],
        "stars": card["stars"],
        "skill_text": card["skill_text"],
        "english_skill_text": card["english_skill_text"],
        "output": str(destination.relative_to(ROOT)),
        "size": list(image.size),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
