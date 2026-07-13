from __future__ import annotations

from typing import Dict, List, Sequence

from .models import Card, Territory

DOMAINS = {
    "白骨": ["白骨岭", "埋骨坡", "乱葬岗"],
    "火云": ["火焰山", "翠云山", "芭蕉洞"],
    "狮驼": ["狮驼岭", "狮驼洞", "狮驼国"],
    "盘丝": ["盘丝洞", "黄花观", "濯垢泉"],
}

HAND_LIMIT = 7
MAX_GUARDS = 3
MAX_TURNS = 200


def build_public_deck() -> List[Card]:
    counts = {
        "小钻风": ("妖怪", 1, 2),
        "精细鬼": ("妖怪", 1, 2),
        "伶俐虫": ("妖怪", 1, 2),
        "急如火": ("妖怪", 1, 2),
        "快如风": ("妖怪", 1, 2),
        "狐阿七大王": ("妖怪", 2, 2),
        "虎先锋": ("妖怪", 2, 2),
        "倚海龙": ("妖怪", 2, 2),
        "有来有去": ("妖怪", 2, 2),
        "金角大王": ("妖怪", 3, 2),
        "银角大王": ("妖怪", 3, 2),
        "白骨精": ("妖怪", 3, 2),
        "黄袍怪": ("妖怪", 3, 2),
        "金鼻白毛老鼠精": ("妖怪", 3, 2),
        "黄风怪": ("妖怪", 4, 2),
        "青狮精": ("妖怪", 4, 2),
        "白象精": ("妖怪", 4, 2),
        "牛魔王": ("妖怪", 5, 1),
        "大鹏精": ("妖怪", 5, 1),
        "紫金红葫芦": ("法宝", 0, 1),
        "金刚琢": ("法宝", 0, 1),
        "幌金绳": ("法宝", 0, 1),
        "辟火罩": ("法宝", 0, 1),
    }
    deck: List[Card] = []
    uid = 0
    for name, (kind, star, count) in counts.items():
        for _ in range(count):
            deck.append(Card(name, kind, star, uid=uid))
            uid += 1
    if len(deck) != 40:
        raise AssertionError(f"标准版牌库应为40张，当前为{len(deck)}张")
    return deck


def build_territory_deck(domains: Sequence[str]) -> List[Territory]:
    return [Territory(domain, name) for domain in domains for name in DOMAINS[domain]]


def card_priority(name: str) -> int:
    return {
        "幌金绳": 94,
        "金刚琢": 90,
        "大鹏精": 88,
        "辟火罩": 86,
        "青狮精": 82,
        "黄风怪": 80,
        "白象精": 78,
        "牛魔王": 76,
        "金角大王": 70,
        "金鼻白毛老鼠精": 68,
        "黄袍怪": 66,
        "银角大王": 62,
        "白骨精": 60,
        "虎先锋": 54,
        "倚海龙": 52,
        "狐阿七大王": 50,
        "有来有去": 48,
        "紫金红葫芦": 46,
        "小钻风": 38,
        "精细鬼": 36,
        "快如风": 34,
        "急如火": 32,
        "伶俐虫": 28,
    }.get(name, 0)


def domain_need_score(
    player: int,
    territory: Territory,
    owned: Dict[int, List[Territory]],
) -> int:
    return (
        sum(1 for item in owned[player] if item.domain == territory.domain) * 10
        + (MAX_GUARDS - len(territory.guards))
    )
