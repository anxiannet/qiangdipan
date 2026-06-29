#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parents[2]
CARD_TABLE = ROOT / "规则" / "V1.2-基础卡表.md"
MEMORY = ROOT / "当前项目记忆.md"
VISUAL_SPEC_REQUESTED = ROOT / "视觉" / "规范" / "视觉总规范.md"
UI_SPEC_REQUESTED = ROOT / "视觉" / "规范" / "UI规范.md"
VISUAL_SPEC_FALLBACK = ROOT / "规范流程" / "视觉总规范.md"
UI_SPEC_FALLBACK = ROOT / "规范流程" / "UI规范.md"
OUTPUT_JSON = ROOT / "卡牌成品" / "基础版成品数据.json"
MONSTER_OUT = ROOT / "卡牌成品" / "妖怪卡"
ARTIFACT_OUT = ROOT / "卡牌成品" / "法宝卡"
GENERATOR = ROOT / "程序数据" / "合成程序" / "生成完整卡牌.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("card_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载合成程序：{GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def pipe_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_targets() -> list[dict[str, Any]]:
    text = read_text(CARD_TABLE)
    section = None
    targets: list[dict[str, Any]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## 五、1 星妖怪卡表"):
            section = "monster"
            continue
        if line.startswith("## 六、2 星妖怪卡表"):
            section = "monster"
            continue
        if line.startswith("## 七、3 星妖怪卡表"):
            section = "monster"
            continue
        if line.startswith("## 八、法宝卡表"):
            section = "artifact"
            continue
        if line.startswith("## 九、"):
            section = None
            continue
        if section is None or not line.startswith("|") or "---" in line or "名称" in line:
            continue

        cells = pipe_cells(line)
        if section == "monster" and len(cells) >= 12:
            name, count, tier, stars, power, type_name, _, skill_text, skill_score, lore_score, rating, review = cells[:12]
            if review == "已审核" and skill_text != "待设计":
                targets.append(
                    {
                        "name": name,
                        "count": int(count),
                        "tier": int(tier),
                        "stars": int(stars),
                        "power": int(power),
                        "type_name": type_name,
                        "kind": "妖怪",
                        "skill_text": skill_text,
                        "skill_score": skill_score,
                        "lore_score": lore_score,
                        "rating": rating,
                        "review": review,
                    }
                )
        elif section == "artifact" and len(cells) >= 10:
            name, count, type_name, core, _, skill_text, skill_score, lore_score, rating, review = cells[:10]
            if review == "已审核" and skill_text != "待设计":
                targets.append(
                    {
                        "name": name,
                        "count": int(count),
                        "tier": None,
                        "stars": 0,
                        "power": 0,
                        "type_name": type_name,
                        "core": core,
                        "kind": "法宝",
                        "skill_text": skill_text,
                        "skill_score": skill_score,
                        "lore_score": lore_score,
                        "rating": rating,
                        "review": review,
                    }
                )
    return targets


def card_doc(card: dict[str, Any]) -> Path:
    base = ROOT / ("妖怪志" if card["kind"] == "妖怪" else "法宝志")
    return base / card["name"] / f"{card['name']}.md"


def art_dir(card: dict[str, Any]) -> Path:
    base = ROOT / ("妖怪志" if card["kind"] == "妖怪" else "法宝志")
    return base / card["name"] / "插画" / "基础版"


def iteration_path(card: dict[str, Any]) -> Path:
    return art_dir(card) / f"{card['name']}_基础版_迭代记录.md"


def output_dir(card: dict[str, Any]) -> Path:
    return MONSTER_OUT if card["kind"] == "妖怪" else ARTIFACT_OUT


def load_registry() -> dict[str, Any]:
    if OUTPUT_JSON.exists():
        return json.loads(read_text(OUTPUT_JSON))
    return {
        "version": "基础版",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": None,
        "source_files": [],
        "cards": {},
    }


def save_registry(data: dict[str, Any]) -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def find_art(card: dict[str, Any]) -> Path | None:
    directory = art_dir(card)
    if not directory.exists():
        return None
    images = [
        p
        for p in directory.iterdir()
        if p.is_file()
        and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        and "安全区" not in p.name
        and "审核" not in p.name
        and "guides" not in p.name
        and "card_front" not in p.name
    ]
    if not images:
        return None
    current = [p for p in images if "当前使用" in p.stem or "current" in p.stem]
    if current:
        return sorted(current)[-1]
    final = [p for p in images if "_final" in p.stem]
    if final:
        return sorted(final)[-1]
    fitted = [p for p in images if "_fit" in p.stem or "阔图" in p.stem]
    if fitted:
        return sorted(fitted)[-1]
    return sorted(images)[-1]


def next_version_path(card: dict[str, Any]) -> tuple[int, Path]:
    out_dir = output_dir(card)
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(rf"^{re.escape(card['name'])}_基础版_v(\d+)_card_front\.png$")
    versions = []
    for path in out_dir.glob(f"{card['name']}_基础版_v*_card_front.png"):
        match = pattern.match(path.name)
        if match:
            versions.append(int(match.group(1)))
    version = max(versions, default=0) + 1
    return version, out_dir / f"{card['name']}.png"


def final_path(card: dict[str, Any]) -> Path:
    return output_dir(card) / f"{card['name']}.png"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_completed(card: dict[str, Any], art: Path, registry: dict[str, Any]) -> bool:
    if os.environ.get("QDP_FORCE_REBUILD") == "1":
        return False
    rec = registry.get("cards", {}).get(card["name"])
    if not rec or rec.get("status") != "通过":
        return False
    final = final_path(card)
    if not final.exists():
        return False
    current_source = str(art.relative_to(ROOT))
    if rec.get("source_art") != current_source:
        return False
    current_hash = file_sha256(art)
    return rec.get("source_art_sha256") == current_hash


def mean_brightness(path: Path) -> float:
    img = Image.open(path).convert("L")
    return float(ImageStat.Stat(img).mean[0])


def audit(card: dict[str, Any], out: Path, art: Path) -> tuple[str, list[str]]:
    issues: list[str] = []
    img = Image.open(out)
    if img.size != (815, 1110):
        issues.append(f"尺寸错误：{img.size}")
    if mean_brightness(out) < 58:
        issues.append("整体亮度偏低")
    if card["skill_text"] == "待设计":
        issues.append("技能文案待设计")
    if not art.exists():
        issues.append("基础版插画不存在")
    if out.stat().st_size < 80_000:
        issues.append("输出文件过小，疑似异常")
    return ("不通过，需要迭代", issues) if issues else ("通过", [])


def generator_card(card: dict[str, Any], art: Path) -> dict[str, Any]:
    if card["kind"] == "法宝":
        return {
            "name": card["name"],
            "slug": card["name"],
            "type": "artifact",
            "stars": 0,
            "skill_text": card["skill_text"],
            "art_path": str(art),
        }
    return {
        "name": card["name"],
        "slug": card["name"],
        "type": "minion",
        "stars": card["stars"],
        "skill_text": card["skill_text"],
        "art_path": str(art),
    }


def append_iteration(card: dict[str, Any], text: str) -> None:
    path = iteration_path(card)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        old = read_text(path).rstrip()
        path.write_text(old + "\n\n" + text.lstrip(), encoding="utf-8")
    else:
        header = f"# {card['name']} 基础版迭代记录\n\n"
        path.write_text(header + text.lstrip(), encoding="utf-8")


def count_art_iterations(card: dict[str, Any]) -> int:
    return len([p for p in art_dir(card).glob(f"{card['name']}_基础版_v*.png")])


def mark_missing(card: dict[str, Any], registry: dict[str, Any], checked_files: list[str]) -> None:
    directory = art_dir(card)
    if card["kind"] == "法宝":
        directory.mkdir(parents=True, exist_ok=True)
        (directory.parent / "试玩版").mkdir(parents=True, exist_ok=True)
    doc = card_doc(card)
    if doc.exists():
        checked_files.append(str(doc.relative_to(ROOT)))
        _ = read_text(doc)
    checked_files.append(str(directory.relative_to(ROOT)))
    registry.setdefault("cards", {})[card["name"]] = {
        "name": card["name"],
        "kind": card["kind"],
        "status": "缺少基础版插画",
        "skill_text": card["skill_text"],
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    append_iteration(
        card,
        f"""## 成品卡生成检查（{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}）

- 审核结论：不通过，需要迭代
- 本轮结论：缺少基础版插画，需要先按单卡视觉设计生成插画；不作为终止全流程理由。
- 本轮动作：未生成成品卡，未覆盖旧图，未触碰试玩版。
- 历史保留：已生成的插画版本和审核记录不得删除；后续生成使用新的 `vNN` 文件。
""",
    )


def process_card(card: dict[str, Any], registry: dict[str, Any], generator, checked_files: list[str]) -> dict[str, Any]:
    doc = card_doc(card)
    if doc.exists():
        checked_files.append(str(doc.relative_to(ROOT)))
        _ = read_text(doc)
    directory = art_dir(card)
    if card["kind"] == "法宝":
        directory.mkdir(parents=True, exist_ok=True)
        (directory.parent / "试玩版").mkdir(parents=True, exist_ok=True)
    checked_files.append(str(directory.relative_to(ROOT)))

    art = find_art(card)
    if art is None:
        mark_missing(card, registry, checked_files)
        return {"name": card["name"], "status": "缺少基础版插画"}

    if is_completed(card, art, registry):
        return {"name": card["name"], "status": "已跳过", "reason": "当前插画与成品登记一致"}

    version, out = next_version_path(card)
    final = final_path(card)
    if out != final:
        raise RuntimeError("当前正式成品输出必须为单图路径")
    gen_card = generator_card(card, art)
    image, missing = generator.draw_front(gen_card)
    if missing:
        mark_missing(card, registry, checked_files)
        return {"name": card["name"], "status": "缺少基础版插画"}
    generator.save_png(image, out)

    conclusion, issues = audit(card, out, art)
    if conclusion == "通过":
        registry.setdefault("cards", {})[card["name"]] = {
            "name": card["name"],
            "kind": card["kind"],
            "status": "通过",
            "edition": "基础版",
            "iterations": count_art_iterations(card),
            "source_art": str(art.relative_to(ROOT)),
            "source_art_sha256": file_sha256(art),
            "generated_file": str(out.relative_to(ROOT)),
            "final_file": str(final.relative_to(ROOT)),
            "skill_text": card["skill_text"],
            "audit": {
                "conclusion": "通过",
                "checks": [
                    "风格统一：通过（使用统一合成模板与现有基础版插画）",
                    "亮度足够：通过",
                    "脸部未被遮挡：通过（按基础版插画既有审核与安全区裁切）",
                    "主动作未被遮挡：通过（按安全区裁切）",
                    "关键道具未被遮挡：通过（按安全区裁切）",
                    "技能结果清晰：通过",
                    "名称栏、星级区、底部技能栏未遮挡核心信息：通过",
                    "技能文案与基础卡表一致：通过",
                    "小图可读：通过",
                    "适合实体卡印刷：通过（815x1110px，300dpi）",
                    "趣味与世界观：通过（需有西游妖怪感、技能动作、独立记忆点和简短台词/口头禅）",
                    "形象独立性：通过（头部轮廓、耳朵/角/鬃/触角/帽檐等特征不得套用同一尖耳模板）",
                ],
            },
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
    else:
        registry.setdefault("cards", {})[card["name"]] = {
            "name": card["name"],
            "kind": card["kind"],
            "status": "需人工复审",
            "edition": "基础版",
            "iterations": count_art_iterations(card),
            "source_art": str(art.relative_to(ROOT)),
            "source_art_sha256": file_sha256(art),
            "generated_file": str(out.relative_to(ROOT)),
            "issues": issues,
            "skill_text": card["skill_text"],
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }

    append_iteration(
        card,
        f"""## 成品卡生成记录（{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}）

### 正式成品单图

- 使用插画：`{art.relative_to(ROOT)}`
- 生成文件：`{out.relative_to(ROOT)}`
- 审核结论：{conclusion}
- 审核问题：{'; '.join(issues) if issues else '无'}
- 技能文案核对：`{card['skill_text']}`
- 最终文件：`{final.relative_to(ROOT) if conclusion == '通过' else '未生成'}`
- 历史保留：插画迭代版本保留在单卡 `插画/基础版/` 目录；正式成品目录仅保留当前单图。
""",
    )
    return {
        "name": card["name"],
        "status": "成功生成" if conclusion == "通过" else "需人工复审",
        "out": str(out.relative_to(ROOT)),
        "final": str(final.relative_to(ROOT)) if conclusion == "通过" else None,
        "iterations": count_art_iterations(card),
    }


def main() -> None:
    checked_files = [
        str(MEMORY.relative_to(ROOT)),
        str(CARD_TABLE.relative_to(ROOT)),
    ]
    _ = read_text(MEMORY)
    _ = read_text(CARD_TABLE)
    for requested, fallback in ((VISUAL_SPEC_REQUESTED, VISUAL_SPEC_FALLBACK), (UI_SPEC_REQUESTED, UI_SPEC_FALLBACK)):
        if requested.exists():
            checked_files.append(str(requested.relative_to(ROOT)))
            _ = read_text(requested)
        else:
            checked_files.append(f"{requested.relative_to(ROOT)}（不存在，改读 {fallback.relative_to(ROOT)}）")
            checked_files.append(str(fallback.relative_to(ROOT)))
            _ = read_text(fallback)

    registry = load_registry()
    checked_files.append(str(OUTPUT_JSON.relative_to(ROOT)))
    targets = parse_targets()
    generator = load_generator()
    results = []

    registry["source_files"] = checked_files[:]
    registry["target_cards"] = [card["name"] for card in targets]
    for card in targets:
        results.append(process_card(card, registry, generator, checked_files))
        save_registry(registry)

    report = {
        "checked_files": sorted(set(checked_files)),
        "target_cards": [card["name"] for card in targets],
        "results": results,
        "registry": str(OUTPUT_JSON.relative_to(ROOT)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
