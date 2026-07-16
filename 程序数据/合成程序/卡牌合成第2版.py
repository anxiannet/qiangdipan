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
FRAME_PATH = ROOT / "测试版" / "卡牌合成第2版_透明边框_815x1110的副本.png"
SKILL_PANEL_PATH = ROOT / "测试版" / "卡牌合成第2版_技能栏_透明.png"
ENGLISH_NAME_DECORATION_PATH = ROOT / "测试版" / "卡牌合成第2版_英文名装饰.png"
FONT_DIR = ROOT / "资源" / "字体" / "思源字体"
FONT_PATHS = {
    "serif_heavy": FONT_DIR / "SourceHanSerifCN-Heavy.otf",
    "sans_bold": FONT_DIR / "SourceHanSansSC-Bold.otf",
    "sans_medium": FONT_DIR / "SourceHanSansSC-Medium.otf",
    "sans_regular": FONT_DIR / "SourceHanSansSC-Regular.otf",
}

CANVAS_SIZE = (815, 1110)
BACKGROUND = (16, 36, 61)
ART_BOX = (55, 97, 763, 840)
SKILL_PANEL_POS = (63, 783)
SKILL_PANEL_SIZE = (694, 265)
ICON_CENTER = (160, 913)
ICON_OPENING_RADIUS = 67
ICON_BOX = (
    ICON_CENTER[0] - ICON_OPENING_RADIUS,
    ICON_CENTER[1] - ICON_OPENING_RADIUS,
    ICON_CENTER[0] + ICON_OPENING_RADIUS,
    ICON_CENTER[1] + ICON_OPENING_RADIUS,
)
LEVEL_BOX = (51, 65, 175, 187)
NAME_ZONE_HEIGHT_RATIO = 3
NAME_ZONE_GAP = 8
NAME_BOX = (190, 91, 675, 150)
ENGLISH_NAME_BOX = (
    190,
    NAME_BOX[3] + NAME_ZONE_GAP,
    675,
    NAME_BOX[3] + NAME_ZONE_GAP
    + (NAME_BOX[3] - NAME_BOX[1]) / NAME_ZONE_HEIGHT_RATIO,
)
SKILL_BOX = (235, 840, 735, 910)
ENGLISH_SKILL_BOX = (285, 925, 685, 1005)
FOOTER_CONTENT_BOX = (61, 1042, 754, 1060)
FOOTER_ITEM_GAP = 24

LEVEL_FONT_ROLE = "sans_bold"
LEVEL_FONT_SIZE = 93
LEVEL_TEXT_COLOR = (255, 255, 255)
LEVEL_STROKE_WIDTH = 5
LEVEL_STROKE_COLOR = (0, 0, 0)

NAME_FONT_ROLE = "serif_heavy"
NAME_FONT_START = 64
NAME_FONT_MINIMUM = 28
NAME_HORIZONTAL_MARGIN = 28
NAME_CHARACTER_SPACING = 5
TEXT_COLOR = (0, 0, 0)

ENGLISH_NAME_FONT_START = 40
ENGLISH_NAME_FONT_MINIMUM = 16
ENGLISH_NAME_HORIZONTAL_MARGIN = 20
ENGLISH_NAME_CHARACTER_SPACING = 0
ENGLISH_NAME_WORD_SPACING = 5
ENGLISH_NAME_DECORATION_MAX_SIZE = (72, 18)
ENGLISH_NAME_DECORATION_WIDTH_SCALE = 0.70
ENGLISH_NAME_DECORATION_HEIGHT_SCALE = 0.50
ENGLISH_NAME_DECORATION_GAP = 20
SKILL_FONT_START = 30
SKILL_FONT_MINIMUM = 21
SKILL_HORIZONTAL_MARGIN = 12
FOOTER_FONT_SIZE = 13
FOOTER_COLOR = (226, 199, 136)
COPYRIGHT_TEXT = "© 2026 Bostage Pte. Ltd. Singapore"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="使用第2版透明边框合成单张妖怪卡。")
    parser.add_argument("--card", default="金鼻白毛老鼠精", help="卡表中的中文卡名")
    return parser.parse_args()


def font(size: int, role: str = "sans_regular") -> ImageFont.ImageFont:
    path = FONT_PATHS[role]
    if not path.exists():
        raise FileNotFoundError(f"缺少合成字体：{path.relative_to(ROOT)}")
    return ImageFont.truetype(str(path), size)


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


def validate_card(card: dict) -> None:
    forbidden_dashes = ("–", "—")
    if any(char in card["english_skill_text"] for char in forbidden_dashes):
        raise ValueError(f"英文技能包含非标准连接符：{card['english_skill_text']}")

    expected = "Place a 1-Star Defender in your Territory."
    if card["card_number"] == "QDP-014" and card["english_skill_text"] != expected:
        raise ValueError(
            "QDP-014 英文技能与卡表标准不一致："
            f"{card['english_skill_text']!r}"
        )


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


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    start: int,
    minimum: int,
    role: str = "sans_medium",
    max_height: int | None = None,
    character_spacing: int = 0,
    word_spacing: int = 0,
) -> ImageFont.ImageFont:
    for size in range(start, minimum - 1, -1):
        candidate = font(size, role)
        box = draw.textbbox((0, 0), text, font=candidate, stroke_width=1)
        measured_width = box[2] - box[0]
        if (character_spacing or word_spacing) and len(text) > 1:
            measured_width = sum(
                draw.textlength(char, font=candidate) for char in text
            )
            measured_width += character_spacing * (len(text) - 1)
            measured_width += word_spacing * text.count(" ")
        fits_width = measured_width <= max_width
        fits_height = max_height is None or box[3] - box[1] <= max_height
        if fits_width and fits_height:
            return candidate
    return font(minimum, role)


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


def draw_centered_with_spacing(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    text_font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    spacing: int,
    word_spacing: int = 0,
) -> None:
    left, top, right, bottom = box
    advances = [draw.textlength(char, font=text_font) for char in text]
    total_width = sum(advances) + spacing * max(0, len(text) - 1)
    total_width += word_spacing * text.count(" ")
    bounds = draw.textbbox((0, 0), text, font=text_font)
    x = left + (right - left - total_width) / 2
    y = top + (bottom - top - (bounds[3] - bounds[1])) / 2 - bounds[1]
    for index, (char, advance) in enumerate(zip(text, advances)):
        draw.text((x, y), char, font=text_font, fill=fill)
        x += advance
        if index < len(text) - 1:
            x += spacing
            if char == " ":
                x += word_spacing


def draw_top_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    text_font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
) -> None:
    left, top, right, _ = box
    bounds = draw.textbbox((0, 0), text, font=text_font)
    x = left + (right - left - (bounds[2] - bounds[0])) / 2 - bounds[0]
    y = top - bounds[1]
    draw.text((x, y), text, font=text_font, fill=fill)


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
    chinese_name_height = NAME_BOX[3] - NAME_BOX[1]
    english_name_height = ENGLISH_NAME_BOX[3] - ENGLISH_NAME_BOX[1]
    if abs(
        chinese_name_height - english_name_height * NAME_ZONE_HEIGHT_RATIO
    ) > 1e-6:
        raise ValueError(
            "卡名安全区高度比例错误："
            f"中文 {chinese_name_height}px，英文 {english_name_height}px"
        )

    required = (
        FRAME_PATH,
        SKILL_PANEL_PATH,
        ENGLISH_NAME_DECORATION_PATH,
        art_path(card),
        icon_path(card),
    )
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

    skill_panel = Image.open(SKILL_PANEL_PATH).convert("RGBA")
    if skill_panel.size != SKILL_PANEL_SIZE:
        raise ValueError(
            f"技能栏尺寸错误：{skill_panel.size}，应为 {SKILL_PANEL_SIZE}"
        )
    canvas.alpha_composite(skill_panel, SKILL_PANEL_POS)

    draw = ImageDraw.Draw(canvas)
    draw_centered(
        draw, str(card["stars"]), LEVEL_BOX, font(LEVEL_FONT_SIZE, LEVEL_FONT_ROLE),
        LEVEL_TEXT_COLOR,
        stroke_width=LEVEL_STROKE_WIDTH,
        stroke_fill=LEVEL_STROKE_COLOR,
    )
    name_font = fit_font(
        draw,
        card["name"],
        NAME_BOX[2] - NAME_BOX[0] - NAME_HORIZONTAL_MARGIN,
        NAME_FONT_START,
        NAME_FONT_MINIMUM,
        role=NAME_FONT_ROLE,
        max_height=NAME_BOX[3] - NAME_BOX[1],
        character_spacing=NAME_CHARACTER_SPACING,
    )
    draw_centered_with_spacing(
        draw,
        card["name"],
        NAME_BOX,
        name_font,
        TEXT_COLOR,
        NAME_CHARACTER_SPACING,
    )
    english_name_font = fit_font(
        draw,
        card["english_name"],
        ENGLISH_NAME_BOX[2] - ENGLISH_NAME_BOX[0] - ENGLISH_NAME_HORIZONTAL_MARGIN,
        ENGLISH_NAME_FONT_START,
        ENGLISH_NAME_FONT_MINIMUM,
        max_height=ENGLISH_NAME_BOX[3] - ENGLISH_NAME_BOX[1],
        character_spacing=ENGLISH_NAME_CHARACTER_SPACING,
        word_spacing=ENGLISH_NAME_WORD_SPACING,
    )
    english_name_width = sum(
        draw.textlength(char, font=english_name_font)
        for char in card["english_name"]
    ) + ENGLISH_NAME_CHARACTER_SPACING * (len(card["english_name"]) - 1)
    english_name_width += (
        ENGLISH_NAME_WORD_SPACING * card["english_name"].count(" ")
    )
    english_name_center_x = (ENGLISH_NAME_BOX[0] + ENGLISH_NAME_BOX[2]) / 2
    english_name_left = english_name_center_x - english_name_width / 2
    english_name_right = english_name_center_x + english_name_width / 2
    decoration_width = min(
        ENGLISH_NAME_DECORATION_MAX_SIZE[0],
        int(english_name_left - ENGLISH_NAME_BOX[0] - ENGLISH_NAME_DECORATION_GAP),
        int(ENGLISH_NAME_BOX[2] - english_name_right - ENGLISH_NAME_DECORATION_GAP),
    )
    if decoration_width > 0:
        decoration = Image.open(ENGLISH_NAME_DECORATION_PATH).convert("RGBA")
        decoration = contain(
            decoration,
            (decoration_width, ENGLISH_NAME_DECORATION_MAX_SIZE[1]),
        )
        decoration = decoration.resize(
            (
                max(
                    1,
                    round(
                        decoration.width
                        * ENGLISH_NAME_DECORATION_WIDTH_SCALE
                    ),
                ),
                max(
                    1,
                    round(
                        decoration.height
                        * ENGLISH_NAME_DECORATION_HEIGHT_SCALE
                    ),
                ),
            ),
            Image.Resampling.LANCZOS,
        )
        decoration_y = round(
            (ENGLISH_NAME_BOX[1] + ENGLISH_NAME_BOX[3] - decoration.height) / 2
        )
        left_decoration_x = round(
            english_name_left - ENGLISH_NAME_DECORATION_GAP - decoration.width
        )
        right_decoration_x = round(english_name_right + ENGLISH_NAME_DECORATION_GAP)
        canvas.alpha_composite(decoration, (left_decoration_x, decoration_y))
        canvas.alpha_composite(
            decoration.transpose(Image.Transpose.FLIP_LEFT_RIGHT),
            (right_decoration_x, decoration_y),
        )
    draw_centered_with_spacing(
        draw,
        card["english_name"],
        ENGLISH_NAME_BOX,
        english_name_font,
        TEXT_COLOR,
        ENGLISH_NAME_CHARACTER_SPACING,
        ENGLISH_NAME_WORD_SPACING,
    )

    skill_font = fit_font(
        draw,
        card["skill_text"],
        SKILL_BOX[2] - SKILL_BOX[0] - SKILL_HORIZONTAL_MARGIN,
        SKILL_FONT_START,
        SKILL_FONT_MINIMUM,
    )
    draw_centered(draw, card["skill_text"], SKILL_BOX, skill_font, TEXT_COLOR)

    english_font = skill_font
    english_lines = wrap_english(
        draw,
        card["english_skill_text"],
        ENGLISH_SKILL_BOX[2] - ENGLISH_SKILL_BOX[0] - 10,
        english_font,
    )
    english_font_bounds = draw.textbbox((0, 0), "Ag", font=english_font)
    line_height = english_font_bounds[3] - english_font_bounds[1] + 6
    if len(english_lines) * line_height > (
        ENGLISH_SKILL_BOX[3] - ENGLISH_SKILL_BOX[1]
    ):
        raise ValueError("英文技能使用中文字号后超出安全区高度")
    english_y = ENGLISH_SKILL_BOX[1]
    for line in english_lines:
        draw_top_centered(
            draw,
            line,
            (
                ENGLISH_SKILL_BOX[0],
                english_y,
                ENGLISH_SKILL_BOX[2],
                english_y + line_height,
            ),
            english_font,
            TEXT_COLOR,
        )
        english_y += line_height

    small_font = font(FOOTER_FONT_SIZE, "sans_regular")
    card_number_bounds = draw.textbbox(
        (0, 0), card["card_number"], font=small_font
    )
    copyright_bounds = draw.textbbox((0, 0), COPYRIGHT_TEXT, font=small_font)
    card_number_width = card_number_bounds[2] - card_number_bounds[0]
    copyright_width = copyright_bounds[2] - copyright_bounds[0]
    footer_width = card_number_width + FOOTER_ITEM_GAP + copyright_width
    footer_left = (
        FOOTER_CONTENT_BOX[0]
        + (FOOTER_CONTENT_BOX[2] - FOOTER_CONTENT_BOX[0] - footer_width) / 2
    )
    card_number_box = (
        round(footer_left),
        FOOTER_CONTENT_BOX[1],
        round(footer_left + card_number_width),
        FOOTER_CONTENT_BOX[3],
    )
    copyright_box = (
        round(footer_left + card_number_width + FOOTER_ITEM_GAP),
        FOOTER_CONTENT_BOX[1],
        round(footer_left + footer_width),
        FOOTER_CONTENT_BOX[3],
    )
    draw_centered(
        draw,
        card["card_number"],
        card_number_box,
        small_font,
        FOOTER_COLOR,
    )
    draw_centered(
        draw,
        COPYRIGHT_TEXT,
        copyright_box,
        small_font,
        FOOTER_COLOR,
    )

    return canvas.convert("RGB")


def main() -> None:
    args = parse_args()
    card = load_card(args.card)
    validate_card(card)
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
