#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "card_data.json"
FRONT_DIR = ROOT / "正面"
BACK_DIR = ROOT / "背面"
TEMPLATE_DIR = ROOT / "模板"
EXPORT_DIR = ROOT / "导出"
PROJECT_ROOT = ROOT.parent
RESOURCE_DIR = PROJECT_ROOT / "资源"
BAIGU_CLEAN_ASSET_DIR = RESOURCE_DIR / "UI" / "白骨阵营"
BAIGU_FALLBACK_ASSET_DIR = PROJECT_ROOT / "output" / "assets"
BAIGU_SOURCE_ASSET_DIR = PROJECT_ROOT / "视觉" / "视觉资产设计" / "白骨阵营"
FABAO_CLEAN_ASSET_DIR = RESOURCE_DIR / "UI" / "法宝卡"
FABAO_FALLBACK_ASSET_DIR = PROJECT_ROOT / "output" / "assets"

BLEED_W, BLEED_H = 815, 1110
TRIM_W, TRIM_H = 744, 1039
LAND_BLEED_W, LAND_BLEED_H = BLEED_H, BLEED_W
LAND_TRIM_W, LAND_TRIM_H = TRIM_H, TRIM_W
BLEED = round((BLEED_W - TRIM_W) / 2)
SAFE = BLEED + 34
DPI = (300, 300)

PAPER = (245, 235, 210)
INK = (54, 42, 32)
GOLD = (190, 150, 76)
DARK_GOLD = (105, 74, 38)
CREAM = (255, 248, 224)
BAIGU_BLEED_BG = (16, 36, 61)

BAIGU_LAYOUT = {
    "frame_box": (SAFE, SAFE, 673, 969),
    "art_clip": (118, 150, 579, 830),
    "star_positions": [(162, 230), (226, 230), (290, 230)],
    "star_size": (56, 56),
    "nameplate": (570, 250, 88, 330),
    "name_safe": (586, 265, 56, 290),
    "skillbar": (67, 885, 682, 116),
    "skill_safe": (157, 907, 502, 72),
}

BAIGU_CLEAN_ASSETS = {
    "frame_1": "frame_1star_clean.png",
    "frame_2": "frame_2star_clean.png",
    "frame_3": "frame_3star_clean.png",
    "nameplate": "nameplate_vertical_clean.png",
    "skillbar": "skillbar_common_clean.png",
    "star_1": "star_1_clean.png",
    "star_2": "star_2_clean.png",
    "star_3": "star_3_clean.png",
}

BAIGU_SOURCE_ASSETS = {
    "frame_1": "baigu_1star_monster_frame_chromakey_B.png",
    "frame_2": "baigu_2star_monster_frame_chromakey_C.png",
    "frame_3": "baigu_3star_monster_frame_chromakey_C.png.png",
    "nameplate": "baigu_monster_nameplate_vertical_chromakey_B.png",
    "skillbar": "baigu_skill_textbar_common_chromakey_B.png",
    "star_1": "baigu_star_1_silver_chromakey_A.png",
    "star_2": "baigu_star_2_purple_chromakey_B.png",
    "star_3": "baigu_star_3_gold_chromakey_B.png",
}

FABAO_LAYOUT = {
    "frame_box": (SAFE, SAFE, 673, 969),
    "art_clip": (133, 185, 549, 675),
    "name_safe": (198, 137, 420, 54),
    "skill_safe": (173, 893, 470, 76),
    "name_size": 56,
    "name_tracking": 8,
    "name_down": 5,
    "skill_up": 10,
}

FABAO_CLEAN_ASSETS = {
    "frame": "fabao_frame_clean_name_bg_dark30.png",
}

TYPE_COLORS = {
    "minion": {
        "main": (144, 92, 46),
        "light": (216, 154, 83),
        "dark": (82, 50, 28),
        "panel": (238, 218, 184),
    },
    "elite": {
        "main": (150, 157, 156),
        "light": (224, 228, 220),
        "dark": (75, 82, 88),
        "panel": (232, 232, 220),
    },
    "leader": {
        "main": (185, 135, 54),
        "light": (248, 211, 115),
        "dark": (74, 48, 25),
        "panel": (240, 222, 179),
    },
    "artifact": {
        "main": (118, 62, 143),
        "light": (223, 174, 247),
        "dark": (66, 34, 82),
        "panel": (237, 219, 239),
    },
    "land": {
        "main": (152, 118, 58),
        "light": (230, 196, 115),
        "dark": (78, 58, 32),
        "panel": (238, 225, 192),
    },
}

LAND_COLORS = {
    "baiguling": ((205, 199, 186), (104, 105, 112)),
    "maigupo": ((190, 174, 136), (105, 91, 68)),
    "luanzanggang": ((143, 128, 170), (78, 67, 104)),
    "huoyanshan": ((220, 89, 42), (122, 45, 24)),
    "cuiyunshan": ((88, 157, 91), (40, 100, 60)),
    "bajiaodong": ((85, 150, 98), (35, 92, 64)),
    "shituoling": ((196, 150, 72), (103, 77, 40)),
    "shituodong": ((184, 131, 66), (89, 62, 36)),
    "shituoguo": ((184, 132, 68), (88, 62, 36)),
    "pansidong": ((144, 83, 155), (72, 45, 86)),
    "huanghuaguan": ((191, 157, 62), (91, 82, 40)),
    "zhuogouquan": ((94, 150, 150), (45, 88, 92)),
}


def ensure_dirs() -> None:
    for path in (FRONT_DIR, BACK_DIR, TEMPLATE_DIR, EXPORT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def font_candidates() -> list[Path]:
    names = [
        "NotoSerifCJK-Regular.ttc",
        "NotoSerifCJKsc-Regular.otf",
        "NotoSansCJK-Regular.ttc",
        "SourceHanSerifSC-Regular.otf",
        "SourceHanSansSC-Regular.otf",
        "PingFang.ttc",
        "PingFang SC.ttf",
        "STHeiti Light.ttc",
        "STHeiti Medium.ttc",
        "SimHei.ttf",
        "WenQuanYi Micro Hei.ttf",
    ]
    dirs = [
        Path("/System/Library/Fonts"),
        Path("/System/Library/Fonts/Supplemental"),
        Path("/Library/Fonts"),
        Path.home() / "Library/Fonts",
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
    ]
    found: list[Path] = []
    for base in dirs:
        if not base.exists():
            continue
        for name in names:
            found.extend(base.rglob(name))
    return found


FONT_PATHS = font_candidates()


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(str(path), size)
        except Exception:
            continue
    if not getattr(font, "_warned", False):
        print("警告：未找到优先中文字体，使用默认字体，中文显示可能不完整。")
        setattr(font, "_warned", True)
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_w: int, start: int, min_size: int) -> ImageFont.ImageFont:
    size = start
    while size >= min_size:
        fnt = font(size)
        w, _ = text_size(draw, text, fnt)
        if w <= max_w:
            return fnt
        size -= 2
    return font(min_size)


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    fnt: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    stroke_fill: tuple[int, int, int] | None = None,
    stroke_width: int = 0,
) -> None:
    x1, y1, x2, y2 = box
    w, h = text_size(draw, text, fnt)
    x = x1 + (x2 - x1 - w) / 2
    y = y1 + (y2 - y1 - h) / 2
    draw.text((x, y), text, font=fnt, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


def star_points(cx: float, cy: float, outer: float, inner: float) -> list[tuple[float, float]]:
    pts = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        r = outer if i % 2 == 0 else inner
        pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    return pts


def draw_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, fill: tuple[int, int, int], outline: tuple[int, int, int]) -> None:
    pts = star_points(cx, cy, size, size * 0.44)
    draw.polygon(pts, fill=fill)
    draw.line(pts + [pts[0]], fill=outline, width=max(2, size // 8), joint="curve")
    draw.polygon(star_points(cx - size * 0.16, cy - size * 0.16, size * 0.32, size * 0.14), fill=(255, 244, 178))


def draw_pattern_border(
    draw: ImageDraw.ImageDraw,
    palette: dict,
    slug: str | None = None,
    size: tuple[int, int] = (BLEED_W, BLEED_H),
    bleed: int = BLEED,
    safe: int = SAFE,
) -> None:
    canvas_w, canvas_h = size
    main = palette["main"]
    light = palette["light"]
    dark = palette["dark"]

    draw.rounded_rectangle((8, 8, canvas_w - 8, canvas_h - 8), radius=44, fill=PAPER, outline=dark, width=8)
    draw.rounded_rectangle((bleed - 12, bleed - 12, canvas_w - bleed + 12, canvas_h - bleed + 12), radius=34, outline=main, width=12)
    draw.rounded_rectangle((safe - 12, safe - 12, canvas_w - safe + 12, canvas_h - safe + 12), radius=28, outline=light, width=3)
    draw.rounded_rectangle((bleed + 8, bleed + 8, canvas_w - bleed - 8, canvas_h - bleed - 8), radius=30, outline=dark, width=4)

    step = 46
    for x in range(42, canvas_w - 42, step):
        draw.arc((x - 18, 20, x + 18, 56), 0, 300, fill=main, width=3)
        draw.arc((x - 18, canvas_h - 56, x + 18, canvas_h - 20), 180, 480, fill=main, width=3)
    for y in range(70, canvas_h - 70, step):
        draw.arc((20, y - 18, 56, y + 18), 90, 390, fill=main, width=3)
        draw.arc((canvas_w - 56, y - 18, canvas_w - 20, y + 18), 270, 570, fill=main, width=3)

    for x, y, sx, sy in [
        (54, 54, 1, 1),
        (canvas_w - 54, 54, -1, 1),
        (54, canvas_h - 54, 1, -1),
        (canvas_w - 54, canvas_h - 54, -1, -1),
    ]:
        draw.ellipse((x - 26, y - 26, x + 26, y + 26), fill=dark, outline=light, width=3)
        draw.polygon([(x, y - 20 * sy), (x + 18 * sx, y), (x, y + 20 * sy), (x - 18 * sx, y)], fill=main)
        draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=light)

    if slug in LAND_COLORS:
        land_main, land_dark = LAND_COLORS[slug]
        draw.rounded_rectangle((bleed - 18, bleed - 18, canvas_w - bleed + 18, canvas_h - bleed + 18), radius=34, outline=land_dark, width=8)
        draw.rounded_rectangle((bleed - 3, bleed - 3, canvas_w - bleed + 3, canvas_h - bleed + 3), radius=30, outline=land_main, width=6)


def gradient_background(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size)
    pix = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        col = tuple(round(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(w):
            pix[x, y] = col
    return img


def load_art(card: dict, art_box: tuple[int, int, int, int]) -> tuple[Image.Image, bool]:
    art_path = resolve_art_path(card)
    x1, y1, x2, y2 = art_box
    target_w, target_h = x2 - x1, y2 - y1
    if art_path.exists():
        img = Image.open(art_path).convert("RGB")
        scale = max(target_w / img.width, target_h / img.height)
        new_size = (round(img.width * scale), round(img.height * scale))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        left = (img.width - target_w) // 2
        top = (img.height - target_h) // 2
        return img.crop((left, top, left + target_w, top + target_h)), False

    placeholder = gradient_background((target_w, target_h), (244, 235, 210), (215, 195, 156))
    d = ImageDraw.Draw(placeholder)
    d.rounded_rectangle((18, 18, target_w - 18, target_h - 18), radius=28, outline=(174, 139, 74), width=5)
    title_font = fit_font(d, card["name"], target_w - 80, 56, 24)
    draw_centered_text(d, card["name"], (30, target_h // 2 - 80, target_w - 30, target_h // 2 - 20), title_font, INK)
    note_font = font(28)
    draw_centered_text(d, "插画待补", (30, target_h // 2, target_w - 30, target_h // 2 + 60), note_font, (115, 82, 48))
    return placeholder, True


def xywh_to_box(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    x, y, w, h = box
    return x, y, x + w, y + h


def cover_crop(img: Image.Image, size: tuple[int, int], focus: tuple[float, float] = (0.5, 0.5)) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / img.width, target_h / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, min(int((resized.width - target_w) * focus[0]), resized.width - target_w))
    top = max(0, min(int((resized.height - target_h) * focus[1]), resized.height - target_h))
    return resized.crop((left, top, left + target_w, top + target_h))


def resolve_art_path(card: dict) -> Path:
    raw_path = Path(card["art_path"])
    candidates = [
        (ROOT / raw_path).resolve(),
        (PROJECT_ROOT / raw_path).resolve(),
        PROJECT_ROOT / "视觉" / "批量生成" / "插画资产" / raw_path.name,
    ]
    if card["type"] in {"minion", "elite", "leader", "artifact", "land"}:
        for prefix in ("xiyao_qiangdipan", "xiyao_zhanshanweiwang"):
            candidates.append(
                PROJECT_ROOT
                / "视觉"
                / "批量生成"
                / "插画资产"
                / f"{prefix}_{card['type']}_{card['slug']}.png"
            )
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def chroma_key_green(path: Path) -> Image.Image:
    src = Image.open(path).convert("RGBA")
    pixels = src.load()
    width, height = src.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            max_rb = max(r, b)
            green_excess = g - max_rb
            green_ratio = g / max(1, max_rb)
            keyed = g > 90 and green_excess > 24 and green_ratio > 1.18
            soft = max(0, min(1, (green_excess - 8) / 42)) * max(0, min(1, (g - 70) / 80))
            if keyed:
                pixels[x, y] = (r, min(g, round(max_rb * 0.92)), b, 0)
            elif soft > 0:
                alpha = round(a * (1 - soft))
                despill_g = min(g, round(max_rb * 0.94))
                pixels[x, y] = (r, despill_g, b, 0 if alpha < 12 else alpha)
            elif g > max_rb and green_excess > 8:
                pixels[x, y] = (r, min(g, round(max_rb * 0.96)), b, a)

    alpha = src.getchannel("A").filter(ImageFilter.GaussianBlur(0.45))
    src.putalpha(alpha)
    bbox = src.getbbox()
    if not bbox:
        return src
    pad = 4
    left, top, right, bottom = bbox
    return src.crop((max(0, left - pad), max(0, top - pad), min(src.width, right + pad), min(src.height, bottom + pad)))


def load_baigu_asset(key: str) -> Image.Image:
    clean = BAIGU_CLEAN_ASSET_DIR / BAIGU_CLEAN_ASSETS[key]
    if clean.exists():
        return Image.open(clean).convert("RGBA")
    fallback = BAIGU_FALLBACK_ASSET_DIR / BAIGU_CLEAN_ASSETS[key]
    if fallback.exists():
        return Image.open(fallback).convert("RGBA")
    source = BAIGU_SOURCE_ASSET_DIR / BAIGU_SOURCE_ASSETS[key]
    if not source.exists():
        raise FileNotFoundError(f"Missing White Bone UI asset: {clean}, {fallback}, or {source}")
    return chroma_key_green(source)


def load_fabao_asset(key: str) -> Image.Image:
    clean = FABAO_CLEAN_ASSET_DIR / FABAO_CLEAN_ASSETS[key]
    if clean.exists():
        return Image.open(clean).convert("RGBA")
    fallback = FABAO_FALLBACK_ASSET_DIR / "fabao_frame_new_clean_name_bg_dark30.png"
    if fallback.exists():
        return Image.open(fallback).convert("RGBA")
    raise FileNotFoundError(f"Missing fabao UI asset: {clean} or {fallback}")


def paste_fit_rgba(base: Image.Image, asset: Image.Image, box: tuple[int, int, int, int]) -> None:
    x, y, w, h = box
    resized = asset.resize((w, h), Image.Resampling.LANCZOS)
    base.alpha_composite(resized, (x, y))


def baigu_frame_for_stars(stars: int, box: tuple[int, int, int, int]) -> Image.Image:
    _, _, width, height = box
    return load_baigu_asset(f"frame_{stars}").resize((width, height), Image.Resampling.LANCZOS)


def make_baigu_skillbar(box: tuple[int, int, int, int]) -> Image.Image:
    _, _, width, height = box
    src = load_baigu_asset("skillbar").resize((width, height), Image.Resampling.LANCZOS)
    top_band = min(28, height // 3)
    bottom_band = min(18, height // 4)
    new_top = max(1, top_band // 2)
    top = src.crop((0, 0, width, top_band)).resize((width, new_top), Image.Resampling.LANCZOS)
    middle = src.crop((0, top_band, width, height - bottom_band)).resize(
        (width, height - new_top - bottom_band),
        Image.Resampling.LANCZOS,
    )
    bottom = src.crop((0, height - bottom_band, width, height))
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    out.alpha_composite(top, (0, 0))
    out.alpha_composite(middle, (0, new_top))
    out.alpha_composite(bottom, (0, height - bottom_band))
    return out


def draw_vertical_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    box_xywh: tuple[int, int, int, int],
    fill: tuple[int, int, int],
    stroke_fill: tuple[int, int, int],
) -> None:
    x, y, w, h = box_xywh
    size = 36 if len(text) <= 4 else 34 if len(text) <= 6 else 32
    while size >= 28:
        fnt = font(size)
        gap = 3
        metrics = []
        total_h = 0
        for char in text:
            bbox = draw.textbbox((0, 0), char, font=fnt, stroke_width=2)
            char_h = bbox[3] - bbox[1]
            metrics.append((char, char_h))
            total_h += char_h
        total_h += gap * (len(metrics) - 1)
        if total_h <= h:
            break
        size -= 1
    cx = x + w / 2
    cy = y + (h - total_h) / 2
    for char, char_h in metrics:
        draw.text((cx, cy + 2), char, font=fnt, fill=(0, 0, 0), stroke_width=2, stroke_fill=(0, 0, 0), anchor="ma")
        cy += char_h + gap
    cy = y + (h - total_h) / 2
    for char, char_h in metrics:
        draw.text((cx, cy), char, font=fnt, fill=fill, stroke_width=2, stroke_fill=stroke_fill, anchor="ma")
        cy += char_h + gap


def draw_bold_skill_text(draw: ImageDraw.ImageDraw, text: str, box_xywh: tuple[int, int, int, int]) -> None:
    x, y, w, h = box_xywh
    display = text or "无技能"
    size = 30
    while size >= 24:
        fnt = font(size)
        bbox = draw.textbbox((0, 0), display, font=fnt, stroke_width=3)
        if bbox[2] - bbox[0] <= w and bbox[3] - bbox[1] <= h:
            break
        size -= 1
    cx = x + w / 2
    cy = y + h / 2 - 10
    draw.text((cx, cy + 1), display, font=fnt, fill=(0, 0, 0), stroke_width=3, stroke_fill=(0, 0, 0), anchor="mm")
    draw.text((cx, cy), display, font=fnt, fill=(243, 238, 228), stroke_width=3, stroke_fill=(30, 26, 24), anchor="mm")
    draw.text((cx + 0.6, cy), display, font=fnt, fill=(243, 238, 228), anchor="mm")


def tracked_text_size(
    draw: ImageDraw.ImageDraw,
    text: str,
    fnt: ImageFont.ImageFont,
    tracking: int,
    stroke_width: int = 0,
) -> tuple[int, int]:
    width = 0
    height = 0
    for index, char in enumerate(text):
        bbox = draw.textbbox((0, 0), char, font=fnt, stroke_width=stroke_width)
        width += bbox[2] - bbox[0]
        height = max(height, bbox[3] - bbox[1])
        if index < len(text) - 1:
            width += tracking
    return width, height


def draw_tracked_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[float, float],
    fnt: ImageFont.ImageFont,
    fill: tuple[int, int, int] | tuple[int, int, int, int],
    tracking: int,
    stroke_width: int = 0,
    stroke_fill: tuple[int, int, int] | tuple[int, int, int, int] | None = None,
) -> None:
    x, y = xy
    for char in text:
        bbox = draw.textbbox((0, 0), char, font=fnt, stroke_width=stroke_width)
        draw.text(
            (x - bbox[0], y - bbox[1]),
            char,
            font=fnt,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        x += (bbox[2] - bbox[0]) + tracking


def draw_fabao_name(img: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(img)
    x, y, w, h = FABAO_LAYOUT["name_safe"]
    tracking = FABAO_LAYOUT["name_tracking"]
    size = FABAO_LAYOUT["name_size"]
    while size >= 42:
        fnt = font(size)
        text_w, text_h = tracked_text_size(draw, text, fnt, tracking, stroke_width=4)
        if text_w <= w and text_h <= h + 16:
            break
        size -= 2
    tx = x + (w - text_w) / 2
    ty = y + (h - text_h) / 2 + FABAO_LAYOUT["name_down"]

    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    draw_tracked_text(
        shadow_draw,
        text,
        (tx, ty + 2),
        fnt,
        (0, 0, 0, 135),
        tracking,
        stroke_width=4,
        stroke_fill=(0, 0, 0, 135),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(1.2))
    img.alpha_composite(shadow)
    draw_tracked_text(
        draw,
        text,
        (tx, ty),
        fnt,
        (250, 236, 190, 255),
        tracking,
        stroke_width=4,
        stroke_fill=(42, 24, 14, 255),
    )


def draw_fabao_skill(img: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(img)
    x, y, w, h = FABAO_LAYOUT["skill_safe"]
    display = text or "无效果"
    size = 34
    while size >= 24:
        fnt = font(size)
        bbox = draw.textbbox((0, 0), display, font=fnt, stroke_width=2)
        if bbox[2] - bbox[0] <= w - 8 and bbox[3] - bbox[1] <= h - 6:
            break
        size -= 1
    bbox = draw.textbbox((0, 0), display, font=fnt, stroke_width=2)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    tx = x + (w - text_w) / 2 - bbox[0]
    ty = y + (h - text_h) / 2 - bbox[1] - FABAO_LAYOUT["skill_up"]

    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.text(
        (tx, ty + 2),
        display,
        font=fnt,
        fill=(0, 0, 0, 130),
        stroke_width=2,
        stroke_fill=(0, 0, 0, 130),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(1.0))
    img.alpha_composite(shadow)
    draw.text(
        (tx, ty),
        display,
        font=fnt,
        fill=(246, 238, 222, 255),
        stroke_width=2,
        stroke_fill=(30, 20, 16, 255),
    )


def draw_baigu_monster_front(card: dict) -> tuple[Image.Image, bool]:
    stars = int(card["stars"])
    img = Image.new("RGBA", (BLEED_W, BLEED_H), BAIGU_BLEED_BG + (255,))

    art_box = BAIGU_LAYOUT["art_clip"]
    art_path = resolve_art_path(card)
    missing = not art_path.exists()
    if missing:
        art, _ = load_art(card, xywh_to_box(art_box))
    else:
        art = Image.open(art_path).convert("RGB")
        art = cover_crop(art, (art_box[2], art_box[3]), focus=(0.52, 0.43))
        art = ImageEnhance.Color(art).enhance(0.98)
        art = ImageEnhance.Contrast(art).enhance(1.0)
    art_rgba = art.convert("RGBA")
    art_rgba.putalpha(mask_rounded((art_box[2], art_box[3]), 32))
    img.alpha_composite(art_rgba, (art_box[0], art_box[1]))

    veil = Image.new("RGBA", (BLEED_W, BLEED_H), (0, 0, 0, 0))
    veil_draw = ImageDraw.Draw(veil)
    veil_draw.rounded_rectangle(xywh_to_box(art_box), radius=32, fill=BAIGU_BLEED_BG + (18,))
    img.alpha_composite(veil)

    skillbar = make_baigu_skillbar(BAIGU_LAYOUT["skillbar"])
    img.alpha_composite(skillbar, (BAIGU_LAYOUT["skillbar"][0], BAIGU_LAYOUT["skillbar"][1]))
    frame = baigu_frame_for_stars(stars, BAIGU_LAYOUT["frame_box"])
    img.alpha_composite(frame, (BAIGU_LAYOUT["frame_box"][0], BAIGU_LAYOUT["frame_box"][1]))
    paste_fit_rgba(img, load_baigu_asset("nameplate"), BAIGU_LAYOUT["nameplate"])

    star_asset = load_baigu_asset(f"star_{stars}")
    star_w, star_h = BAIGU_LAYOUT["star_size"]
    for x, y in BAIGU_LAYOUT["star_positions"][:stars]:
        paste_fit_rgba(img, star_asset, (x, y, star_w, star_h))

    draw = ImageDraw.Draw(img)
    name_color = (244, 227, 178) if stars == 3 else (247, 244, 238)
    draw_vertical_text(draw, card["name"], BAIGU_LAYOUT["name_safe"], name_color, (42, 33, 29))
    draw_bold_skill_text(draw, card.get("skill_text", ""), BAIGU_LAYOUT["skill_safe"])
    return img.convert("RGB"), missing


def mask_rounded(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def draw_badge(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int], palette: dict) -> None:
    draw.rounded_rectangle(box, radius=18, fill=palette["dark"], outline=palette["light"], width=3)
    fnt = fit_font(draw, text, box[2] - box[0] - 22, 30, 18)
    draw_centered_text(draw, text, box, fnt, CREAM)


def draw_stars(draw: ImageDraw.ImageDraw, stars: int, palette: dict) -> None:
    size = 29 if stars < 3 else 32
    gap = size * 2 + 10
    start = SAFE + size + 6
    cy = SAFE + 20
    plate = (SAFE - 10, SAFE - 22, SAFE + stars * gap + 50, SAFE + 62)
    draw.rounded_rectangle(plate, radius=28, fill=palette["dark"], outline=palette["light"], width=4)
    for i in range(stars):
        draw_star(draw, round(start + i * gap), cy, size, palette["light"], palette["dark"])


def draw_name_plate(draw: ImageDraw.ImageDraw, name: str, panel: tuple[int, int, int, int], palette: dict) -> None:
    x1, y1, x2, y2 = panel
    shadow = (x1 + 8, y1 + 8, x2 + 8, y2 + 8)
    draw.rounded_rectangle(shadow, radius=24, fill=(42, 28, 18))
    draw.rounded_rectangle(panel, radius=24, fill=palette["dark"], outline=palette["light"], width=5)
    draw.rounded_rectangle((x1 + 10, y1 + 10, x2 - 10, y2 - 10), radius=18, outline=palette["main"], width=2)
    fnt = fit_font(draw, name, x2 - x1 - 42, 54, 32)
    draw_centered_text(draw, name, panel, fnt, (255, 221, 128), stroke_fill=(64, 38, 20), stroke_width=2)


def draw_skill_scroll(draw: ImageDraw.ImageDraw, text: str, palette: dict, panel: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = panel
    draw.rounded_rectangle((x1 + 6, y1 + 8, x2 + 6, y2 + 8), radius=28, fill=(49, 34, 22))
    draw.rounded_rectangle(panel, radius=28, fill=(248, 232, 191), outline=palette["dark"], width=5)
    for x in (x1 + 26, x2 - 26):
        draw.ellipse((x - 20, y1 - 6, x + 20, y2 + 6), fill=palette["main"], outline=palette["dark"], width=4)
        draw.line((x, y1 + 10, x, y2 - 10), fill=palette["light"], width=3)
    draw.rounded_rectangle((x1 + 50, y1 + 13, x2 - 50, y2 - 13), radius=18, fill=(255, 244, 212), outline=palette["main"], width=2)
    display = text or "无技能"
    fnt = fit_font(draw, display, x2 - x1 - 126, 30, 18)
    draw_centered_text(draw, display, (x1 + 56, y1 + 8, x2 - 56, y2 - 8), fnt, INK)


def draw_magic_clouds(draw: ImageDraw.ImageDraw, size: tuple[int, int], palette: dict) -> None:
    w, h = size
    for i in range(11):
        x = 62 + i * 73
        y = 168 + (i % 4) * 95
        col = palette["main"] if i % 2 else palette["light"]
        draw.arc((x - 72, y - 28, x + 72, y + 54), 185, 352, fill=col, width=5)
        draw.arc((w - x - 72, h - y - 60, w - x + 72, h - y + 22), 8, 178, fill=col, width=4)
    for r, alpha_col in [(360, (255, 205, 95)), (250, (126, 74, 150)), (160, (255, 232, 140))]:
        draw.ellipse((w // 2 - r, 160 - r // 2, w // 2 + r, 160 + r // 2), outline=alpha_col, width=2)


def paste_art_with_frame(
    img: Image.Image,
    draw: ImageDraw.ImageDraw,
    art: Image.Image,
    art_box: tuple[int, int, int, int],
    palette: dict,
    radius: int,
) -> None:
    x1, y1, x2, y2 = art_box
    shadow = Image.new("RGBA", (x2 - x1, y2 - y1), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((0, 0, shadow.width, shadow.height), radius=radius, fill=(0, 0, 0, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img.paste(shadow.convert("RGB"), (x1 + 8, y1 + 10), shadow)
    img.paste(art, (x1, y1), mask_rounded(art.size, radius))
    draw.rounded_rectangle(art_box, radius=radius, outline=palette["dark"], width=7)
    draw.rounded_rectangle((x1 + 9, y1 + 9, x2 - 9, y2 - 9), radius=max(4, radius - 8), outline=palette["light"], width=3)


def draw_monster_front(card: dict) -> tuple[Image.Image, bool]:
    return draw_baigu_monster_front(card)


def draw_legacy_monster_front(card: dict) -> tuple[Image.Image, bool]:
    palette = TYPE_COLORS[card["type"]]
    img = gradient_background((BLEED_W, BLEED_H), (71, 54, 52), (23, 27, 35)).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw_magic_clouds(draw, (BLEED_W, BLEED_H), palette)
    draw_pattern_border(draw, palette)
    draw_stars(draw, int(card["stars"]), palette)

    art_box = (76, 118, BLEED_W - 76, 854)
    art, missing = load_art(card, art_box)
    paste_art_with_frame(img, draw, art, art_box, palette, 30)
    draw_name_plate(draw, card["name"], (90, 782, BLEED_W - 90, 858), palette)
    draw_skill_scroll(draw, card.get("skill_text", ""), palette, (78, 900, BLEED_W - 78, 1038))
    return img, missing


def draw_artifact_front(card: dict) -> tuple[Image.Image, bool]:
    img = Image.new("RGBA", (BLEED_W, BLEED_H), BAIGU_BLEED_BG + (255,))
    art_box = FABAO_LAYOUT["art_clip"]
    art_path = resolve_art_path(card)
    missing = not art_path.exists()
    if missing:
        art, _ = load_art(card, xywh_to_box(art_box))
    else:
        art = Image.open(art_path).convert("RGB")
        art = cover_crop(art, (art_box[2], art_box[3]), focus=(0.5, 0.5))
    img.alpha_composite(art.convert("RGBA"), (art_box[0], art_box[1]))

    frame = load_fabao_asset("frame").resize(
        (FABAO_LAYOUT["frame_box"][2], FABAO_LAYOUT["frame_box"][3]),
        Image.Resampling.LANCZOS,
    )
    img.alpha_composite(frame, (FABAO_LAYOUT["frame_box"][0], FABAO_LAYOUT["frame_box"][1]))
    draw_fabao_name(img, card["name"])
    draw_fabao_skill(img, card.get("skill_text", ""))
    return img.convert("RGB"), missing


def land_faction(slug: str) -> str:
    if slug in {"baiguling", "maigupo", "luanzanggang"}:
        return "白骨"
    if slug in {"huoyanshan", "cuiyunshan", "bajiaodong"}:
        return "火云"
    if slug in {"shituoling", "shituodong", "shituoguo"}:
        return "狮驼"
    return "盘丝"


def draw_land_emblem(draw: ImageDraw.ImageDraw, center: tuple[int, int], slug: str, palette: dict) -> None:
    cx, cy = center
    faction = land_faction(slug)
    draw.ellipse((cx - 42, cy - 42, cx + 42, cy + 42), fill=palette["dark"], outline=palette["light"], width=5)
    if faction == "白骨":
        draw.line((cx - 25, cy - 16, cx + 25, cy + 16), fill=CREAM, width=9)
        draw.line((cx - 25, cy + 16, cx + 25, cy - 16), fill=CREAM, width=9)
    elif faction == "火云":
        draw.polygon([(cx, cy - 30), (cx + 20, cy + 20), (cx, cy + 10), (cx - 20, cy + 20)], fill=(238, 91, 38))
    elif faction == "狮驼":
        draw.polygon(star_points(cx, cy, 30, 15), fill=(238, 190, 82))
    else:
        for i in range(8):
            angle = i * math.pi / 4
            draw.line((cx, cy, cx + math.cos(angle) * 30, cy + math.sin(angle) * 30), fill=(225, 184, 240), width=3)
        draw.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(145, 69, 160))


def draw_land_front(card: dict) -> tuple[Image.Image, bool]:
    palette = TYPE_COLORS["land"].copy()
    if card["slug"] in LAND_COLORS:
        land_main, land_dark = LAND_COLORS[card["slug"]]
        palette.update({"main": land_main, "dark": land_dark, "light": tuple(min(255, c + 48) for c in land_main)})
    img = gradient_background((LAND_BLEED_W, LAND_BLEED_H), (60, 48, 36), (24, 26, 27)).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw_pattern_border(draw, palette, card["slug"], size=(LAND_BLEED_W, LAND_BLEED_H))

    title_panel = (112, 44, LAND_BLEED_W - 112, 128)
    draw.rounded_rectangle((title_panel[0] + 8, title_panel[1] + 8, title_panel[2] + 8, title_panel[3] + 8), radius=28, fill=(31, 24, 18))
    draw.rounded_rectangle(title_panel, radius=28, fill=palette["dark"], outline=palette["light"], width=5)
    draw_land_emblem(draw, (title_panel[0] + 60, 86), card["slug"], palette)
    title_font = fit_font(draw, card["name"], title_panel[2] - title_panel[0] - 170, 56, 34)
    draw_centered_text(draw, card["name"], (title_panel[0] + 118, title_panel[1], title_panel[2] - 42, title_panel[3]), title_font, (255, 225, 132), stroke_fill=(62, 40, 22), stroke_width=2)

    art_box = (62, 150, LAND_BLEED_W - 62, LAND_BLEED_H - 88)
    art, missing = load_art(card, art_box)
    paste_art_with_frame(img, draw, art, art_box, palette, 28)

    bottom = (86, LAND_BLEED_H - 78, LAND_BLEED_W - 86, LAND_BLEED_H - 34)
    draw.rounded_rectangle(bottom, radius=20, fill=palette["dark"], outline=palette["light"], width=3)
    for x in range(bottom[0] + 38, bottom[2] - 38, 76):
        draw.arc((x - 34, bottom[1] + 4, x + 34, bottom[3] + 20), 180, 360, fill=palette["main"], width=3)
    draw_badge(draw, land_faction(card["slug"]), (LAND_BLEED_W - 184, 56, LAND_BLEED_W - 92, 116), palette)
    return img, missing


def draw_front(card: dict) -> tuple[Image.Image, bool]:
    if card["type"] == "land":
        return draw_land_front(card)
    if card["type"] == "artifact":
        return draw_artifact_front(card)
    return draw_monster_front(card)
    return img, missing


def draw_card_back(kind: str) -> Image.Image:
    if kind == "land":
        size = (LAND_BLEED_W, LAND_BLEED_H)
        palette = {"main": (185, 145, 74), "light": (238, 204, 126), "dark": (74, 59, 35), "panel": (242, 224, 185)}
        img = gradient_background(size, (64, 50, 35), (26, 31, 31)).convert("RGB")
    elif kind == "artifact":
        size = (BLEED_W, BLEED_H)
        palette = {"main": (118, 62, 143), "light": (223, 174, 247), "dark": (66, 34, 82), "panel": (237, 219, 239)}
        img = gradient_background(size, (58, 38, 72), (26, 22, 38)).convert("RGB")
    else:
        size = (BLEED_W, BLEED_H)
        palette = {"main": GOLD, "light": (232, 198, 116), "dark": DARK_GOLD, "panel": (242, 224, 185)}
        img = gradient_background(size, (84, 59, 47), (25, 28, 36)).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw_pattern_border(draw, palette, size=size)

    w, h = size
    center = (w // 2, h // 2)
    base_r = min(w, h) // 3
    for r, col, width in [(base_r, palette["light"], 5), (base_r - 46, palette["dark"], 3), (base_r - 100, palette["main"], 3)]:
        draw.ellipse((center[0] - r, center[1] - r, center[0] + r, center[1] + r), outline=col, width=width)

    if kind == "land":
        draw.rounded_rectangle((170, 252, w - 170, h - 182), radius=36, fill=(225, 205, 150), outline=palette["dark"], width=6)
        draw.polygon([(232, 545), (350, 345), (456, 545)], fill=(174, 138, 76))
        draw.polygon([(420, 545), (610, 285), (806, 545)], fill=(128, 101, 58))
        draw.arc((235, 320, 850, 645), 190, 350, fill=palette["main"], width=16)
        title_box = (250, 564, w - 250, 650)
        type_text = "地盘牌"
    elif kind == "artifact":
        for i in range(10):
            angle = i * math.pi / 5
            draw.line((center[0], center[1], center[0] + math.cos(angle) * (base_r + 68), center[1] + math.sin(angle) * (base_r + 68)), fill=palette["main"], width=4)
        draw.rounded_rectangle((210, 364, w - 210, 746), radius=44, fill=(230, 210, 236), outline=palette["dark"], width=7)
        draw.ellipse((center[0] - 128, center[1] - 128, center[0] + 128, center[1] + 128), fill=(98, 49, 128), outline=palette["light"], width=8)
        draw.polygon(star_points(center[0], center[1], 92, 40), fill=(238, 196, 106))
        title_box = (140, 766, w - 140, 850)
        type_text = "法宝牌"
    else:
        draw.rounded_rectangle((190, 350, w - 190, 760), radius=36, fill=(242, 226, 188), outline=palette["dark"], width=6)
        draw.arc((240, 410, 575, 780), 200, 340, fill=palette["main"], width=14)
        draw.polygon([(250, 650), (330, 520), (405, 650)], fill=(180, 142, 76))
        draw.polygon([(360, 650), (460, 470), (570, 650)], fill=(154, 116, 61))
        draw.arc((210, 455, 610, 765), 200, 330, fill=palette["dark"], width=4)
        title_box = (120, 476, w - 120, 574)
        type_text = "妖怪牌"

    title = "抢地盘"
    title_font = font(72)
    draw_centered_text(draw, title, title_box, title_font, palette["dark"], stroke_fill=(255, 248, 224), stroke_width=2)
    mark_font = font(34)
    if kind == "land":
        mark_box = (250, 662, w - 250, 712)
    elif kind == "artifact":
        mark_box = (140, 854, w - 140, 906)
    else:
        mark_box = (120, 586, w - 120, 640)
    draw_centered_text(draw, f"夕妖 · {type_text}", mark_box, mark_font, palette["main"], stroke_fill=(38, 28, 22), stroke_width=1)
    return img


def save_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, dpi=DPI)


def make_contact_sheet(files: Iterable[Path], out: Path) -> None:
    files = list(files)
    thumb_w, thumb_h = 159, 217
    label_h = 32
    cols = 6
    rows = math.ceil(len(files) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "white")
    d = ImageDraw.Draw(sheet)
    label_font = font(12)
    for idx, path in enumerate(files):
        card = Image.open(path).convert("RGB")
        card.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * thumb_w + (thumb_w - card.width) // 2
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(card, (x, y))
        d.text(((idx % cols) * thumb_w + 4, y + thumb_h + 2), path.stem.replace("xiyao_qiangdipan_card_front_", "")[:24], font=label_font, fill=(0, 0, 0))
    save_png(sheet, out)


def make_preview_all_cards(cards: list[dict], out: Path) -> None:
    picks = [
        ("妖怪卡", "xiyao_qiangdipan_card_front_niumowang.png"),
        ("妖怪卡", "xiyao_qiangdipan_card_front_xiaozuanfeng.png"),
        ("法宝卡", "xiyao_qiangdipan_card_front_zijin_honghulu.png"),
        ("地盘卡", "xiyao_qiangdipan_card_front_huoyanshan.png"),
        ("地盘卡", "xiyao_qiangdipan_card_front_baiguling.png"),
        ("妖怪牌背", "xiyao_qiangdipan_monster_back.png"),
        ("法宝牌背", "xiyao_qiangdipan_artifact_back.png"),
        ("地盘牌背", "xiyao_qiangdipan_land_back.png"),
    ]
    tile_w, tile_h = 270, 380
    label_h = 42
    cols = 4
    rows = 2
    sheet = Image.new("RGB", (cols * tile_w, rows * (tile_h + label_h)), (246, 241, 228))
    d = ImageDraw.Draw(sheet)
    label_font = font(24)
    for idx, (label, file_name) in enumerate(picks):
        path = (BACK_DIR if "back" in file_name else FRONT_DIR) / file_name
        card = Image.open(path).convert("RGB")
        card.thumbnail((tile_w - 26, tile_h - 18), Image.Resampling.LANCZOS)
        base_x = (idx % cols) * tile_w
        base_y = (idx // cols) * (tile_h + label_h)
        x = base_x + (tile_w - card.width) // 2
        y = base_y + (tile_h - card.height) // 2
        d.rounded_rectangle((base_x + 10, base_y + 8, base_x + tile_w - 10, base_y + tile_h - 8), radius=10, fill=(232, 224, 205), outline=(146, 116, 64), width=2)
        sheet.paste(card, (x, y))
        draw_centered_text(d, label, (base_x, base_y + tile_h, base_x + tile_w, base_y + tile_h + label_h), label_font, (58, 42, 28))
    save_png(sheet, out)


def main() -> None:
    ensure_dirs()
    cards = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    missing: list[str] = []
    generated: list[Path] = []

    for card in cards:
        front, is_missing = draw_front(card)
        out = FRONT_DIR / f"xiyao_qiangdipan_card_front_{card['slug']}.png"
        save_png(front, out)
        generated.append(out)
        if is_missing:
            missing.append(card["name"])

    backs = {
        "monster": BACK_DIR / "xiyao_qiangdipan_monster_back.png",
        "artifact": BACK_DIR / "xiyao_qiangdipan_artifact_back.png",
        "land": BACK_DIR / "xiyao_qiangdipan_land_back.png",
    }
    save_png(draw_card_back("monster"), backs["monster"])
    save_png(draw_card_back("artifact"), backs["artifact"])
    save_png(draw_card_back("land"), backs["land"])

    preview_card = {
        "name": "模板预览",
        "slug": "template_preview",
        "type": "leader",
        "display_type": "3星首领",
        "stars": 3,
        "skill_text": "技能短文案显示区域",
        "art_path": "__missing_template_preview__.png",
    }
    preview, _ = draw_front(preview_card)
    save_png(preview, TEMPLATE_DIR / "card_front_template_preview.png")

    make_contact_sheet(generated, EXPORT_DIR / "all_cards_contact_sheet.png")
    make_preview_all_cards(cards, EXPORT_DIR / "preview_all_cards.png")

    report = {
        "front_cards": len(generated),
        "monster_back": str(backs["monster"]),
        "artifact_back": str(backs["artifact"]),
        "land_back": str(backs["land"]),
        "template_preview": str(TEMPLATE_DIR / "card_front_template_preview.png"),
        "preview_all_cards": str(EXPORT_DIR / "preview_all_cards.png"),
        "monster_artifact_size_px": [BLEED_W, BLEED_H],
        "land_size_px": [LAND_BLEED_W, LAND_BLEED_H],
        "missing_art": missing,
    }
    (EXPORT_DIR / "generation_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
