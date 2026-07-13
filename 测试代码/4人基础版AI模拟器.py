#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《夕妖：抢地盘》V1.3 AI模拟器

适用规则版本：V1.3
当前同步卡表版本：V1.3-卡表-029

用途：
- 验证当前标准版40张牌在2~4人局中的规则闭环与收束情况。
- 对比 aggressive / human_like 两种AI行为。
- 统计直接胜利、牌库耗尽结算、超时、地盘回流与成功攻击。

说明：
- 本模拟器是规则验证型AI，不代表真人最优策略。
- 延续旧测试代码的“每人起始5张牌”测试口径。
- 喊名类效果使用概率模型：human_like 35%，aggressive 50%。
- 伶俐虫的信息收益不直接改变牌区，因此只按1星守军处理。

示例：
python3 测试代码/4人基础版AI模拟器.py --players 3 --ai human_like --games 3000 --seed 20260713 --json
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from dataclasses import dataclass, field
from statistics import mean, median
from typing import Dict, List, Optional, Sequence, Tuple

DOMAINS = {
    "白骨": ["白骨岭", "埋骨坡", "乱葬岗"],
    "火云": ["火焰山", "翠云山", "芭蕉洞"],
    "狮驼": ["狮驼岭", "狮驼洞", "狮驼国"],
    "盘丝": ["盘丝洞", "黄花观", "濯垢泉"],
}

HAND_LIMIT = 7
MAX_GUARDS = 3
MAX_TURNS = 200


@dataclass
class Card:
    name: str
    kind: str
    star: int = 0
    owner: Optional[int] = None
    uid: int = 0


@dataclass
class Territory:
    domain: str
    name: str
    owner: Optional[int] = None
    guards: List[Card] = field(default_factory=list)
    protected: bool = False


@dataclass
class GameResult:
    winner: Optional[int]
    reason: str
    turns: int
    deck_left: int
    deck_empty: bool
    territory_returns: int
    successful_attacks: int
    settlement: bool


class Game:
    def __init__(self, ai: str, players_count: int, domain_count: int, center_size: int, seed: int):
        if ai not in ("aggressive", "human_like"):
            raise ValueError(f"未知AI: {ai}")
        if players_count not in (2, 3, 4):
            raise ValueError("玩家人数仅支持2~4人")
        if domain_count not in (2, 3, 4):
            raise ValueError("妖域数量仅支持2~4")
        if center_size not in (2, 3):
            raise ValueError("中央地盘数量仅支持2或3")

        self.ai = ai
        self.players = list(range(players_count))
        self.rng = random.Random(seed)
        self.turn_index = 0
        self.turns = 0
        self.hands: Dict[int, List[Card]] = {p: [] for p in self.players}
        self.discard: List[Card] = []
        self.deck = build_public_deck()
        self.rng.shuffle(self.deck)

        self.available_domains = self.rng.sample(list(DOMAINS.keys()), domain_count)
        self.territory_deck = build_territory_deck(self.available_domains)
        self.rng.shuffle(self.territory_deck)
        self.center: List[Territory] = []
        self.owned: Dict[int, List[Territory]] = {p: [] for p in self.players}

        self.territory_returns = 0
        self.successful_attacks = 0
        self.no_progress_round = 0
        self.deck_empty_once = False
        self.center_size = center_size

        for p in self.players:
            self.draw(p, 5)
        self.refill_center()
        self.turn_index = self.rng.randrange(len(self.players))

    def draw(self, player: int, count: int = 1) -> None:
        for _ in range(count):
            if not self.deck:
                self.deck_empty_once = True
                return
            card = self.deck.pop(0)
            card.owner = player
            self.hands[player].append(card)

    def refill_center(self) -> None:
        while len(self.center) < self.center_size and self.territory_deck:
            territory = self.territory_deck.pop(0)
            territory.owner = None
            territory.guards = []
            territory.protected = False
            self.center.append(territory)

    def check_winner(self) -> Optional[int]:
        for player in self.players:
            domains: Dict[str, int] = {}
            for territory in self.owned[player]:
                domains[territory.domain] = domains.get(territory.domain, 0) + 1
            if any(count >= 3 for count in domains.values()):
                return player
        return None

    def return_empty_owned_territories(self) -> None:
        changed = True
        while changed:
            changed = False
            for player in self.players:
                for territory in list(self.owned[player]):
                    if territory.guards:
                        continue
                    self.owned[player].remove(territory)
                    territory.owner = None
                    territory.protected = False
                    self.territory_deck.append(territory)
                    self.rng.shuffle(self.territory_deck)
                    self.territory_returns += 1
                    changed = True
            self.refill_center()

    def place_guard(self, player: int, territory: Territory, card: Card, trigger_skill: bool = True) -> None:
        if len(territory.guards) >= MAX_GUARDS:
            raise ValueError("目标地盘已满")
        if territory.owner is None:
            if territory in self.center:
                self.center.remove(territory)
            territory.owner = player
            self.owned[player].append(territory)
            self.refill_center()
        territory.guards.append(card)
        card.owner = player
        if trigger_skill:
            self.resolve_enter_skill(player, card, territory)
        self.return_empty_owned_territories()

    def unprotected_enemy_territories(self, player: int) -> List[Territory]:
        return [
            territory
            for enemy in self.players
            if enemy != player
            for territory in self.owned[enemy]
            if territory.guards and not territory.protected
        ]

    def resolve_enter_skill(self, player: int, card: Card, entered: Territory) -> None:
        enemies = [p for p in self.players if p != player]
        enemy_ts = self.unprotected_enemy_territories(player)

        if card.name == "小钻风":
            own_guards = [
                (territory, guard)
                for territory in self.owned[player]
                for guard in territory.guards
                if guard.uid != card.uid
            ]
            if own_guards:
                territory, guard = min(own_guards, key=lambda pair: (pair[1].star, card_priority(pair[1].name)))
                territory.guards.remove(guard)
                self.hands[player].append(guard)

        elif card.name == "精细鬼":
            if self.hands[player]:
                self.discard_lowest(player)
                self.draw(player, 1)

        elif card.name == "急如火":
            if enemies and self.rng.random() < self.answer_probability():
                target = self.rng.choice(enemies)
                if self.hands[player] and self.hands[target]:
                    self.discard_lowest(player)
                    self.discard_lowest(target)
                    self.draw(player, 1)
                    self.draw(target, 1)

        elif card.name == "快如风":
            if enemies and self.rng.random() < self.answer_probability():
                target = self.rng.choice(enemies)
                self.draw(player, 1)
                self.draw(target, 1)

        elif card.name == "狐阿七大王":
            candidates = [c for c in self.discard if c.kind == "妖怪" and c.star == 1]
            if candidates:
                chosen = max(candidates, key=lambda c: card_priority(c.name))
                self.discard.remove(chosen)
                chosen.owner = player
                self.hands[player].append(chosen)

        elif card.name == "虎先锋":
            self.remove_one_guard(enemy_ts, star_eq=1, to_hand=False)

        elif card.name == "倚海龙":
            self.remove_one_guard(enemy_ts, star_eq=1, to_hand=True)

        elif card.name == "有来有去":
            self.resolve_you_lai_you_qu(player)

        elif card.name == "金角大王":
            valid = [p for p in enemies if self.hands[p]]
            if valid:
                target = self.rng.choice(valid)
                stolen = self.rng.choice(self.hands[target])
                self.hands[target].remove(stolen)
                stolen.owner = player
                self.hands[player].append(stolen)

        elif card.name == "银角大王":
            valid = [p for p in enemies if self.hands[p]]
            if valid and self.hands[player]:
                target = self.rng.choice(valid)
                own = self.rng.choice(self.hands[player])
                other = self.rng.choice(self.hands[target])
                self.hands[player].remove(own)
                self.hands[target].remove(other)
                own.owner = target
                other.owner = player
                self.hands[target].append(own)
                self.hands[player].append(other)

        elif card.name == "黄袍怪":
            self.remove_one_guard(enemy_ts, star_eq=1, to_hand=True, new_owner=player)

        elif card.name == "金鼻白毛老鼠精":
            candidates = [
                (territory, guard)
                for territory in enemy_ts
                for guard in territory.guards
                if guard.star == 1
            ]
            destinations = [t for t in self.owned[player] if len(t.guards) < MAX_GUARDS]
            if candidates and destinations:
                src, guard = self.rng.choice(candidates)
                dst = max(destinations, key=lambda t: domain_need_score(player, t, self.owned))
                src.guards.remove(guard)
                guard.owner = player
                dst.guards.append(guard)

        elif card.name == "黄风怪":
            candidates = [
                (territory, guard)
                for territory in enemy_ts
                for guard in territory.guards
                if guard.star <= 2
            ]
            if len(candidates) >= 2:
                chosen = sorted(
                    candidates,
                    key=lambda pair: (pair[1].star, card_priority(pair[1].name)),
                    reverse=True,
                )[:2]
                for territory, guard in chosen:
                    if guard in territory.guards:
                        territory.guards.remove(guard)
                        if guard.owner is not None:
                            self.hands[guard.owner].append(guard)

        elif card.name == "青狮精":
            self.remove_one_guard(enemy_ts, star_le=3, to_hand=False, pick_high=True)

        elif card.name == "白象精":
            self.remove_one_guard(enemy_ts, star_le=4, to_hand=True, pick_high=True)

        elif card.name == "牛魔王":
            extra = self.best_monster_in_hand(player)
            destination = self.best_place_for_guard(player)
            if extra is not None and destination is not None:
                self.hands[player].remove(extra)
                self.place_guard(player, destination, extra, trigger_skill=True)

        elif card.name == "大鹏精":
            self.try_attack(player)

    def resolve_you_lai_you_qu(self, player: int) -> None:
        if not self.deck:
            return
        top = self.deck[:2]
        self.deck = self.deck[2:]
        chosen = max(top, key=lambda c: (c.star, card_priority(c.name)))
        top.remove(chosen)
        chosen.owner = player
        self.hands[player].append(chosen)
        for unchosen in top:
            self.deck.append(unchosen)

    def answer_probability(self) -> float:
        return 0.50 if self.ai == "aggressive" else 0.35

    def remove_one_guard(
        self,
        territories: Sequence[Territory],
        *,
        star_eq: Optional[int] = None,
        star_le: Optional[int] = None,
        to_hand: bool = False,
        new_owner: Optional[int] = None,
        pick_high: bool = False,
    ) -> bool:
        candidates: List[Tuple[Territory, Card]] = []
        for territory in territories:
            for guard in territory.guards:
                if star_eq is not None and guard.star != star_eq:
                    continue
                if star_le is not None and guard.star > star_le:
                    continue
                candidates.append((territory, guard))
        if not candidates:
            return False

        src, guard = (
            max(candidates, key=lambda pair: (pair[1].star, card_priority(pair[1].name)))
            if pick_high
            else self.rng.choice(candidates)
        )
        src.guards.remove(guard)
        if new_owner is not None:
            guard.owner = new_owner
        if to_hand:
            owner = guard.owner
            if owner is not None:
                self.hands[owner].append(guard)
        else:
            self.discard_or_return(guard)
        return True

    def discard_lowest(self, player: int) -> None:
        if not self.hands[player]:
            return
        card = min(self.hands[player], key=lambda c: (c.star, card_priority(c.name)))
        self.hands[player].remove(card)
        card.owner = None
        self.discard.append(card)

    def discard_or_return(self, card: Card) -> None:
        if card.name == "白骨精":
            card.owner = None
            self.deck.append(card)
            self.rng.shuffle(self.deck)
        else:
            card.owner = None
            self.discard.append(card)

    def best_monster_in_hand(self, player: int) -> Optional[Card]:
        monsters = [c for c in self.hands[player] if c.kind == "妖怪"]
        return max(monsters, key=lambda c: (c.star, card_priority(c.name))) if monsters else None

    def best_treasure_in_hand(self, player: int) -> Optional[Card]:
        treasures = [c for c in self.hands[player] if c.kind == "法宝"]
        return max(treasures, key=lambda c: card_priority(c.name)) if treasures else None

    def best_place_for_guard(self, player: int) -> Optional[Territory]:
        candidates = [t for t in self.owned[player] if len(t.guards) < MAX_GUARDS] + list(self.center)
        return max(candidates, key=lambda t: domain_need_score(player, t, self.owned)) if candidates else None

    def consume_jingangzhuo(self, target_player: int) -> bool:
        counter = next((c for c in self.hands[target_player] if c.name == "金刚琢"), None)
        if counter is None:
            return False
        self.hands[target_player].remove(counter)
        counter.owner = None
        self.discard.append(counter)
        return True

    def use_treasure(self, player: int, card: Card) -> bool:
        enemy_ts = self.unprotected_enemy_territories(player)

        if card.name == "金刚琢":
            return False

        if card.name == "辟火罩":
            candidates = [t for t in self.owned[player] if not t.protected]
            if not candidates:
                return False
            target = max(
                candidates,
                key=lambda t: (
                    sum(1 for x in self.owned[player] if x.domain == t.domain),
                    sum(g.star for g in t.guards),
                ),
            )
            target.protected = True
            self.hands[player].remove(card)
            card.owner = None
            self.discard.append(card)
            return True

        if card.name == "幌金绳":
            candidates = [(territory, guard) for territory in enemy_ts for guard in territory.guards]
            if not candidates:
                return False
            src, guard = max(candidates, key=lambda pair: (pair[1].star, card_priority(pair[1].name)))
            target_player = src.owner
            self.hands[player].remove(card)
            card.owner = None
            self.discard.append(card)
            if target_player is not None and self.consume_jingangzhuo(target_player):
                return True
            src.guards.remove(guard)
            guard.owner = player
            self.hands[player].append(guard)
            self.return_empty_owned_territories()
            return True

        if card.name == "紫金红葫芦":
            valid_players = [
                p
                for p in self.players
                if p != player and any(t.guards and not t.protected for t in self.owned[p])
            ]
            if not valid_players:
                return False
            target_player = max(
                valid_players,
                key=lambda p: max(
                    g.star
                    for t in self.owned[p]
                    if not t.protected
                    for g in t.guards
                ),
            )
            self.hands[player].remove(card)
            card.owner = None
            self.discard.append(card)
            if self.rng.random() >= self.answer_probability():
                return True
            if self.consume_jingangzhuo(target_player):
                return True
            candidates = [
                (territory, guard)
                for territory in self.owned[target_player]
                if not territory.protected
                for guard in territory.guards
            ]
            if candidates:
                src, guard = max(candidates, key=lambda pair: (pair[1].star, card_priority(pair[1].name)))
                src.guards.remove(guard)
                guard.owner = player
                self.hands[player].append(guard)
                self.return_empty_owned_territories()
            return True

        return False

    def recruit_best(self, player: int) -> bool:
        monster = self.best_monster_in_hand(player)
        territory = self.best_place_for_guard(player)
        if monster is None or territory is None:
            return False
        self.hands[player].remove(monster)
        self.place_guard(player, territory, monster)
        return True

    def should_recruit_before_attack(self, player: int) -> bool:
        territories = self.owned[player]
        if not territories:
            return True
        if sum(len(t.guards) for t in territories) <= len(territories):
            return True
        domains: Dict[str, int] = {}
        for territory in territories:
            domains[territory.domain] = domains.get(territory.domain, 0) + 1
        return any(v >= 2 for v in domains.values()) and any(len(t.guards) < 2 for t in territories)

    def attack_score(
        self,
        player: int,
        source: Territory,
        target: Territory,
        attackers: Sequence[Card],
        survivors: Sequence[Card],
    ) -> int:
        own_same = sum(1 for t in self.owned[player] if t.domain == target.domain)
        block = False
        if target.owner is not None and target.owner != player:
            block = sum(1 for t in self.owned[target.owner] if t.domain == target.domain) >= 2
        source_empty = len(source.guards) == len(attackers)
        score = (
            own_same * 30
            + sum(g.star for g in target.guards) * 3
            + len(survivors) * 6
            - sum(g.star for g in attackers) * 2
        )
        if own_same >= 2:
            score += 120
        if block:
            score += 80
        if source_empty:
            score -= 45
        if source_empty and (own_same >= 2 or block):
            score += 35
        if target.domain not in [t.domain for t in self.owned[player]]:
            score -= 12
        return score

    def try_attack(self, player: int) -> bool:
        own = [t for t in self.owned[player] if t.guards]
        targets = self.unprotected_enemy_territories(player)
        best = None

        for source in own:
            for count in range(1, min(MAX_GUARDS, len(source.guards)) + 1):
                for attackers in itertools.combinations(list(source.guards), count):
                    for target in targets:
                        ok, survivors, dead = battle_outcome(list(attackers), list(target.guards))
                        if not ok or not survivors:
                            continue
                        score = (
                            domain_need_score(player, target, self.owned) * 10
                            + sum(g.star for g in target.guards)
                            - sum(g.star for g in attackers)
                            if self.ai == "aggressive"
                            else self.attack_score(player, source, target, list(attackers), survivors)
                        )
                        if best is None or score > best[0]:
                            best = (score, source, target, list(attackers), survivors, dead)

        if best is None:
            return False
        score, source, target, attackers, survivors, dead = best
        if self.ai == "human_like" and score < 30:
            return False

        for guard in attackers:
            if guard in source.guards:
                source.guards.remove(guard)
        for guard in list(target.guards):
            target.guards.remove(guard)
            self.discard_or_return(guard)
        for guard in dead:
            if guard in survivors:
                survivors.remove(guard)
            self.discard_or_return(guard)

        old_owner = target.owner
        if old_owner is not None and target in self.owned[old_owner]:
            self.owned[old_owner].remove(target)
        target.owner = player
        target.protected = False
        target.guards = survivors[:MAX_GUARDS]
        for guard in target.guards:
            guard.owner = player
        self.owned[player].append(target)
        self.successful_attacks += 1
        self.return_empty_owned_territories()
        return True

    def enforce_hand_limit(self, player: int) -> None:
        while len(self.hands[player]) > HAND_LIMIT:
            self.discard_lowest(player)

    def take_turn(self) -> Optional[GameResult]:
        player = self.turn_index % len(self.players)
        self.turn_index += 1
        self.turns += 1
        before = self.snapshot_progress()

        self.draw(player, 1)
        acted = False

        if self.ai == "aggressive":
            acted = self.try_attack(player)
            if not acted:
                treasure = self.best_treasure_in_hand(player)
                if treasure and card_priority(treasure.name) >= 80:
                    acted = self.use_treasure(player, treasure)
            if not acted:
                acted = self.recruit_best(player)
        else:
            if self.should_recruit_before_attack(player):
                acted = self.recruit_best(player)
            if not acted:
                acted = self.try_attack(player)
            if not acted:
                treasure = self.best_treasure_in_hand(player)
                if treasure and card_priority(treasure.name) >= 80:
                    acted = self.use_treasure(player, treasure)
            if not acted:
                acted = self.recruit_best(player)

        self.enforce_hand_limit(player)

        winner = self.check_winner()
        if winner is not None:
            return GameResult(
                winner,
                "同妖域3地盘",
                self.turns,
                len(self.deck),
                self.deck_empty_once,
                self.territory_returns,
                self.successful_attacks,
                False,
            )

        if not self.deck:
            after = self.snapshot_progress()
            self.no_progress_round = self.no_progress_round + 1 if after == before else 0
            if self.no_progress_round >= len(self.players):
                winner = self.settlement_winner()
                return GameResult(
                    winner,
                    "公共牌库耗尽结算" if winner is not None else "平局结算",
                    self.turns,
                    len(self.deck),
                    True,
                    self.territory_returns,
                    self.successful_attacks,
                    True,
                )

        if self.turns >= MAX_TURNS:
            return GameResult(
                None,
                "超时",
                self.turns,
                len(self.deck),
                self.deck_empty_once,
                self.territory_returns,
                self.successful_attacks,
                False,
            )
        return None

    def snapshot_progress(self) -> Tuple:
        return tuple(
            (
                player,
                tuple(
                    sorted(
                        (
                            territory.name,
                            territory.protected,
                            tuple(guard.name for guard in territory.guards),
                        )
                        for territory in self.owned[player]
                    )
                ),
            )
            for player in self.players
        )

    def settlement_winner(self) -> Optional[int]:
        scores = []
        for player in self.players:
            territories = self.owned[player]
            domain_max = max(
                [
                    sum(1 for t in territories if t.domain == domain)
                    for domain in self.available_domains
                ]
                or [0]
            )
            scores.append(
                (
                    len(territories),
                    sum(g.star for t in territories for g in t.guards),
                    domain_max,
                    sum(len(t.guards) for t in territories),
                    player,
                )
            )
        scores.sort(reverse=True)
        if len(scores) > 1 and scores[0][:4] == scores[1][:4]:
            return None
        return scores[0][4]


def battle_outcome(attackers: Sequence[Card], defenders: Sequence[Card]) -> Tuple[bool, List[Card], List[Card]]:
    hp = {id(g): g.star for g in defenders}
    live_def = list(defenders)
    live_atk = list(attackers)
    dead: List[Card] = []

    for attacker in sorted(attackers, key=lambda g: (g.star, card_priority(g.name))):
        if not live_def:
            break
        target = max(live_def, key=lambda g: g.star)
        hp[id(target)] -= attacker.star
        if attacker.star <= target.star:
            if attacker in live_atk:
                live_atk.remove(attacker)
            dead.append(attacker)
        if hp[id(target)] <= 0:
            live_def.remove(target)

    return len(live_def) == 0 and len(live_atk) > 0, live_atk, dead


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


def domain_need_score(player: int, territory: Territory, owned: Dict[int, List[Territory]]) -> int:
    return (
        sum(1 for t in owned[player] if t.domain == territory.domain) * 10
        + (MAX_GUARDS - len(territory.guards))
    )


def run_batch(
    ai: str,
    players_count: int,
    domain_count: int,
    center_size: int,
    games: int,
    seed: int,
) -> Dict[str, object]:
    results: List[GameResult] = []
    for index in range(games):
        game = Game(ai, players_count, domain_count, center_size, seed + index)
        result = None
        while result is None:
            result = game.take_turn()
        results.append(result)

    reasons: Dict[str, int] = {}
    for result in results:
        reasons[result.reason] = reasons.get(result.reason, 0) + 1

    turns = [r.turns for r in results]
    returns = [r.territory_returns for r in results]
    attacks = [r.successful_attacks for r in results]
    deck_left = [r.deck_left for r in results]

    direct = reasons.get("同妖域3地盘", 0)
    settle = reasons.get("公共牌库耗尽结算", 0)
    draws = reasons.get("平局结算", 0)
    timeouts = reasons.get("超时", 0)

    return {
        "rules_version": "V1.3",
        "card_table_version": "V1.3-卡表-029",
        "deck_size": 40,
        "ai": ai,
        "players": players_count,
        "domain_count": domain_count,
        "center_size": center_size,
        "games": games,
        "seed": seed,
        "reasons": reasons,
        "direct_wins": direct,
        "settlement_wins": settle,
        "settlement_draws": draws,
        "timeouts": timeouts,
        "avg_turns": round(mean(turns), 2),
        "avg_rounds": round(mean(turns) / players_count, 2),
        "median_turns": median(turns),
        "p90_turns": sorted(turns)[max(0, int(games * 0.9) - 1)],
        "avg_deck_left": round(mean(deck_left), 2),
        "deck_empty_games": sum(1 for r in results if r.deck_empty),
        "deck_empty_rate": round(sum(1 for r in results if r.deck_empty) / games, 4),
        "settlement_rate": round((settle + draws) / games, 4),
        "avg_territory_returns": round(mean(returns), 2),
        "avg_successful_attacks": round(mean(attacks), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--players", type=int, choices=[2, 3, 4], default=4)
    parser.add_argument("--domain-count", type=int, choices=[2, 3, 4], default=4)
    parser.add_argument("--center-size", type=int, choices=[2, 3], default=3)
    parser.add_argument("--ai", choices=["aggressive", "human_like"], default="human_like")
    parser.add_argument("--games", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=20260713)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = run_batch(
        args.ai,
        args.players,
        args.domain_count,
        args.center_size,
        args.games,
        args.seed,
    )
    print(
        json.dumps(summary, ensure_ascii=False, indent=2)
        if args.json
        else "\n".join(f"{key}: {value}" for key, value in summary.items())
    )


if __name__ == "__main__":
    main()
