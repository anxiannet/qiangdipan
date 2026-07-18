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
CARD_TABLE = ROOT / "第2版" / "全卡面文案.md"
QUANTITY_TABLE = ROOT / "规则" / "V1.3-基础卡表.md"
FORMAL_ART_DIR = ROOT / "第2版" / "插画"
FORMAL_ICON_DIR = ROOT / "第2版" / "技能图标"
PRINT_DIR = ROOT / "第2版" / "印刷文件" / "手牌"
FRAME_PATH = ROOT / "测试版" / "卡牌合成第2版_透明边框_815x1110的副本.png"
SKILL_PANEL_PATH = ROOT / "测试版" / "卡牌合成第2版_技能栏_透明.png"
SKILL_ICON_FRAME_PATH = ROOT / "测试版" / "卡牌合成第2版_技能图标圆框_透明.png"
ENGLISH_NAME_DECORATION_PATH = ROOT / "测试版" / "卡牌合成第2版_英文名装饰.png"
STAMP_PATH = ROOT / "测试版" / "夕妖印章_透明.png"
FOOTER_BACKGROUND_PATH = ROOT / "测试版" / "卡牌合成第2版_版权背景纹理.png"
FONT_DIR = ROOT / "资源" / "字体" / "思源字体"
FONT_PATHS = {
    "serif_heavy": FONT_DIR / "SourceHanSerifCN-Heavy.otf",
    "sans_bold": FONT_DIR / "SourceHanSansSC-Bold.otf",
    "sans_medium": FONT_DIR / "SourceHanSansSC-Medium.otf",
    "sans_regular": FONT_DIR / "SourceHanSansSC-Regular.otf",
}

CANVAS_SIZE = (815, 1110)
BACKGROUND = (16, 36, 61)
ART_BOX = (36, 36, 780, 1075)
ART_CORNER_RADIUS = 56
STAMP_SIZE = (49, 69)
STAMP_POS = (686, 718)
SKILL_PANEL_POS = (63, 813)
SKILL_PANEL_SIZE = (694, 215)
ICON_CENTER = (160, 919)
ICON_OPENING_RADIUS = 54
SKILL_ICON_FRAME_SIZE = (142, 142)
SKILL_ICON_FRAME_POS = (
    ICON_CENTER[0] - SKILL_ICON_FRAME_SIZE[0] // 2,
    ICON_CENTER[1] - SKILL_ICON_FRAME_SIZE[1] // 2,
)
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
SKILL_BOX = (235, 854, 735, 911)
ENGLISH_SKILL_BOX = (285, 933, 685, 1015)
FOOTER_CONTENT_BOX = (61, 1032, 754, 1061)
FOOTER_ITEM_GAP = 24
FOOTER_BACKGROUND_BOX = (55, 995, 763, 1066)

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
FOOTER_FONT_SIZE = 25
FOOTER_COLOR = (242, 220, 168)
COPYRIGHT_TEXT = "© 2026 Bostage Pte. Ltd., Singapore"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="使用第2版透明边框合成单张妖怪卡。")
    parser.add_argument("--card", default="金鼻白毛老鼠精", help="卡表中的中文卡名")
    parser.add_argument(
        "--formal",
        action="store_true",
        help="使用第2版正式插画与技能图标，按卡表数量输出印刷文件",
    )
    return parser.parse_args()


def font(size: int, role: str = "sans_regular") -> ImageFont.ImageFont:
    path = FONT_PATHS[role]
    if not path.exists():
        raise FileNotFoundError(f"缺少合成字体：{path.relative_to(ROOT)}")
    return ImageFont.truetype(str(path), size)


def load_card(name: str) -> dict:
    card: dict[str, str | int] | None = None
    for raw_line in CARD_TABLE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        heading = re.fullmatch(r"### (QDP-\d{3}) (.+)", line)
        if heading:
            card = {
                "card_number": heading.group(1),
                "heading_name": heading.group(2),
            }
            continue
        if card is None or not line.startswith("- "):
            continue
        field = re.fullmatch(r"- ([^：]+)：(.*)", line)
        if not field:
            continue
        key, value = field.groups()
        field_names = {
            "中文名": "name",
            "英文名": "english_name",
            "类型": "card_type",
            "中文技能": "skill_text",
            "英文技能": "english_skill_text",
            "卡号": "listed_card_number",
        }
        if key == "星级":
            star_match = re.fullmatch(r"([1-5])星", value)
            if not star_match:
                raise ValueError(f"卡面文案星级格式错误：{value!r}")
            card["stars"] = int(star_match.group(1))
        elif key in field_names:
            card[field_names[key]] = value

        if key != "卡号" or card.get("name") != name:
            continue
        if card["listed_card_number"] != card["card_number"]:
            raise ValueError(
                "卡面文案标题与卡号字段不一致："
                f"{card['card_number']} / {card['listed_card_number']}"
            )
        if card["heading_name"] != card["name"]:
            raise ValueError(
                "卡面文案标题与中文名字段不一致："
                f"{card['heading_name']} / {card['name']}"
            )
        required = (
            "card_number",
            "name",
            "english_name",
            "skill_text",
            "english_skill_text",
        )
        missing = [key for key in required if key not in card]
        if missing:
            raise ValueError(
                f"卡面文案缺少字段：{card['card_number']} {', '.join(missing)}"
            )
        result = {key: card[key] for key in required}
        result["stars"] = card.get("stars")
        result["card_type"] = card.get("card_type", "")
        return result
    raise ValueError(f"未在第2版全卡面文案中找到妖怪卡：{name}")


def card_folder(card: dict) -> Path:
    return ROOT / "妖怪志" / card["name"] / "第2版"


def art_path(card: dict) -> Path:
    return FORMAL_ART_DIR / f"{card['card_number']}-{card['name']}.png"


def icon_path(card: dict) -> Path:
    return FORMAL_ICON_DIR / f"{card['card_number']}-{card['name']}.png"


def output_path(card: dict) -> Path:
    return card_folder(card) / f"{card['name']}_第2版_完整卡牌.png"


def validate_card(card: dict) -> None:
    forbidden_dashes = ("–", "—")
    if any(char in card["english_skill_text"] for char in forbidden_dashes):
        raise ValueError(f"英文技能包含非标准连接符：{card['english_skill_text']}")


def load_print_quantity(card: dict) -> int:
    for raw_line in QUANTITY_TABLE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or "---" in line or "卡号" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0] != card["card_number"]:
            continue
        if cells[1] != card["name"]:
            raise ValueError(
                "印刷数量卡表与第2版文案中文名不一致："
                f"{cells[1]} / {card['name']}"
            )
        quantity = int(cells[3])
        if quantity < 1:
            raise ValueError(f"印刷数量必须大于0：{card['card_number']}")
        return quantity
    raise ValueError(f"未找到印刷数量：{card['card_number']} {card['name']}")


def formal_resource_cards() -> list[dict]:
    cards: list[dict] = []
    for art in sorted(FORMAL_ART_DIR.glob("QDP-???-*.png")):
        match = re.fullmatch(r"(QDP-\d{3})-(.+)\.png", art.name)
        if not match:
            continue
        number, name = match.groups()
        card = load_card(name)
        if card["card_number"] != number:
            raise ValueError(f"正式插画文件名卡号不一致：{art.name}")
        cards.append(card)
    return cards


def formal_print_paths(card: dict, quantity: int) -> list[Path]:
    stem = f"{card['card_number']}-{card['name']}_第2版_完整卡牌"
    return [PRINT_DIR / f"每样{quantity}张" / f"{stem}.png"]

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
    if card["stars"] is None:
        raise ValueError(
            f"当前第2版卡框仅支持有星级妖怪卡：{card['card_number']} {card['name']}"
        )
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
        SKILL_ICON_FRAME_PATH,
        ENGLISH_NAME_DECORATION_PATH,
        STAMP_PATH,
        FOOTER_BACKGROUND_PATH,
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
    card_inner_mask = Image.new("L", CANVAS_SIZE, 0)
    ImageDraw.Draw(card_inner_mask).rounded_rectangle(
        (ART_BOX[0], ART_BOX[1], ART_BOX[2] - 1, ART_BOX[3] - 1),
        radius=ART_CORNER_RADIUS,
        fill=255,
    )
    canvas.paste(
        artwork,
        ART_BOX[:2],
        card_inner_mask.crop(ART_BOX),
    )

    footer_background_size = (
        FOOTER_BACKGROUND_BOX[2] - FOOTER_BACKGROUND_BOX[0],
        FOOTER_BACKGROUND_BOX[3] - FOOTER_BACKGROUND_BOX[1],
    )
    footer_background = Image.open(FOOTER_BACKGROUND_PATH).convert("RGB")
    footer_background = cover_crop(
        footer_background,
        footer_background_size,
        focus_y=0.5,
    )
    canvas.paste(
        footer_background,
        FOOTER_BACKGROUND_BOX[:2],
        card_inner_mask.crop(FOOTER_BACKGROUND_BOX),
    )
    stamp = Image.open(STAMP_PATH).convert("RGBA")
    stamp = contain(stamp, STAMP_SIZE)
    stamp_x = STAMP_POS[0] + (STAMP_SIZE[0] - stamp.width) // 2
    stamp_y = STAMP_POS[1] + (STAMP_SIZE[1] - stamp.height) // 2
    canvas.alpha_composite(stamp, (stamp_x, stamp_y))

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

    skill_icon_frame = Image.open(SKILL_ICON_FRAME_PATH).convert("RGBA")
    if skill_icon_frame.size != SKILL_ICON_FRAME_SIZE:
        raise ValueError(
            "技能图标圆框尺寸错误："
            f"{skill_icon_frame.size}，应为 {SKILL_ICON_FRAME_SIZE}"
        )
    canvas.alpha_composite(skill_icon_frame, SKILL_ICON_FRAME_POS)

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
        role="sans_bold",
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
    if args.formal:
        PRINT_DIR.mkdir(parents=True, exist_ok=True)
        generated: list[dict] = []
        blocked: list[dict] = []
        for card in formal_resource_cards():
            missing = [
                str(path.relative_to(ROOT))
                for path in (art_path(card), icon_path(card))
                if not path.exists()
            ]
            if missing:
                blocked.append({
                    "card_number": card["card_number"],
                    "card": card["name"],
                    "reason": f"正式资源不完整：{'、'.join(missing)}",
                })
                continue
            if card["stars"] is None:
                blocked.append({
                    "card_number": card["card_number"],
                    "card": card["name"],
                    "reason": "当前第2版程序没有已审核的无星级法宝卡框",
                })
                continue
            validate_card(card)
            quantity = load_print_quantity(card)
            image = compose(card)
            destinations = formal_print_paths(card, quantity)
            for destination in destinations:
                destination.parent.mkdir(parents=True, exist_ok=True)
                image.save(destination, dpi=(300, 300), optimize=True)
            generated.append({
                "card_number": card["card_number"],
                "card": card["name"],
                "quantity": quantity,
                "files": [str(path.relative_to(ROOT)) for path in destinations],
            })

        icon_only = sorted(
            path.name for path in FORMAL_ICON_DIR.glob("QDP-???-*.png")
            if not (FORMAL_ART_DIR / path.name).exists()
        )
        for filename in icon_only:
            match = re.fullmatch(r"(QDP-\d{3})-(.+)\.png", filename)
            if not match:
                continue
            number, name = match.groups()
            blocked.append({
                "card_number": number,
                "card": name,
                "reason": "第2版/插画中缺少同名正式插画",
            })

        manifest = {
            "compositor_version": COMPOSITOR_VERSION,
            "compositor_id": COMPOSITOR_ID,
            "copy_source": str(CARD_TABLE.relative_to(ROOT)),
            "quantity_source": str(QUANTITY_TABLE.relative_to(ROOT)),
            "art_source": str(FORMAL_ART_DIR.relative_to(ROOT)),
            "icon_source": str(FORMAL_ICON_DIR.relative_to(ROOT)),
            "canvas_size": list(CANVAS_SIZE),
            "dpi": 300,
            "generated": generated,
            "blocked": blocked,
        }
        manifest_path = PRINT_DIR / "印刷清单.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return

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
