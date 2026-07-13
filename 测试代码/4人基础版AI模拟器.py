#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《夕妖：抢地盘》V1.3 AI模拟器

适用规则版本：V1.3
当前同步卡表版本：V1.3-卡表-029
核心规则来源：规则/V1.3-核心规则.md

用途：
- 验证当前标准版40张牌在2~4人局中的规则闭环与收束情况。
- 对比 aggressive / human_like 两种AI行为。
- 统计直接胜利、牌库耗尽结算、超时、地盘回流与成功/失败攻击。

说明：
- 本模拟器是规则验证型AI，不代表真人最优策略。
- 每人起始5张、每回合抽1张、手牌上限7张，按V1.3核心规则执行。
- 喊名类效果使用概率模型：human_like 35%，aggressive 50%。
- 伶俐虫的信息收益未进入AI决策，只按1星守军处理。
- 战斗会枚举攻方顺序与每次守方目标，允许成功和失败两类战斗。
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
class BattleResult:
    success: bool
    attack_order: Tuple[Card, ...]
    surviving_attackers: List[Card]
    dead_attackers: List[Card]
    surviving_defenders: List[Card]
    dead_defenders: List[Card]


@dataclass
class BattlePlan:
    score: float
    source: Territory
    target: Territory
    result: BattleResult


@dataclass
class GameResult:
    winner: Optional[int]
    reason: str
    turns: int
    deck_left: int
    deck_empty: bool
    territory_returns: int
    successful_attacks: int
    failed_attacks: int
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
        self.available_domains = self.rng.sample(list(DOMAINS), domain_count)
        self.territory_deck = build_territory_deck(self.available_domains)
        self.rng.shuffle(self.territory_deck)
        self.center: List[Territory] = []
        self.owned: Dict[int, List[Territory]] = {p: [] for p in self.players}
        self.center_size = center_size
        self.territory_returns = 0
        self.successful_attacks = 0
        self.failed_attacks = 0
        self.no_progress_round = 0
        self.deck_empty_once = False
        self.played_public_card_this_turn = False
        self.control_changed_this_turn = False
        self.immediate_winner: Optional[int] = None

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
            counts: Dict[str, int] = {}
            for territory in self.owned[player]:
                counts[territory.domain] = counts.get(territory.domain, 0) + 1
            if any(value >= 3 for value in counts.values()):
                return player
        return None

    def mark_immediate_winner(self) -> bool:
        winner = self.check_winner()
        if winner is not None:
            self.immediate_winner = winner
            return True
        return False

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
                    self.control_changed_this_turn = True
                    changed = True
            self.refill_center()

    def place_guard(self, player: int, territory: Territory, card: Card, trigger_skill: bool = True) -> None:
        if len(territory.guards) >= MAX_GUARDS:
            raise ValueError("目标地盘已满")
        gained = territory.owner is None
        if gained:
            if territory in self.center:
                self.center.remove(territory)
            territory.owner = player
            self.owned[player].append(territory)
            self.control_changed_this_turn = True
            self.refill_center()
        territory.guards.append(card)
        card.owner = player

        if gained and self.mark_immediate_winner():
            return
        if trigger_skill:
            self.resolve_enter_skill(player, card)
        self.return_empty_owned_territories()

    def unprotected_enemy_territories(self, player: int) -> List[Territory]:
        return [
            territory
            for enemy in self.players
            if enemy != player
            for territory in self.owned[enemy]
            if territory.guards and not territory.protected
        ]

    def resolve_enter_skill(self, player: int, card: Card) -> None:
        if self.immediate_winner is not None:
            return
        enemies = [p for p in self.players if p != player]
        enemy_ts = self.unprotected_enemy_territories(player)

        if card.name == "小钻风":
            candidates = [
                (territory, guard)
                for territory in self.owned[player]
                for guard in territory.guards
                if guard.uid != card.uid
            ]
            if candidates:
                territory, guard = min(
                    candidates,
                    key=lambda pair: (pair[1].star, card_priority(pair[1].name)),
                )
                territory.guards.remove(guard)
                self.hands[player].append(guard)

        elif card.name == "精细鬼":
            if self.hands[player]:
                self.discard_lowest(player)
                self.draw(player)

        elif card.name == "急如火":
            valid = [p for p in enemies if self.hands[p]]
            if valid and self.hands[player] and self.rng.random() < self.answer_probability():
                target = self.rng.choice(valid)
                own_card = min(self.hands[player], key=lambda c: (c.star, card_priority(c.name)))
                target_card = min(self.hands[target], key=lambda c: (c.star, card_priority(c.name)))
                self.hands[player].remove(own_card)
                self.hands[target].remove(target_card)
                own_card.owner = target
                target_card.owner = player
                self.hands[target].append(own_card)
                self.hands[player].append(target_card)

        elif card.name == "快如风":
            if enemies and self.rng.random() < self.answer_probability():
                target = self.rng.choice(enemies)
                self.draw(player)
                self.draw(target)

        elif card.name == "狐阿七大王":
            candidates = [c for c in self.discard if c.kind == "妖怪" and c.star == 1]
            if candidates:
                chosen = max(candidates, key=lambda c: card_priority(c.name))
                self.discard.remove(chosen)
                chosen.owner = player
                self.hands[player].append(chosen)

        elif card.name == "虎先锋":
            self.remove_one_guard(enemy_ts, star_eq=1)

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
                source, guard = self.rng.choice(candidates)
                destination = max(
                    destinations,
                    key=lambda t: domain_need_score(player, t, self.owned),
                )
                source.guards.remove(guard)
                guard.owner = player
                destination.guards.append(guard)

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
            self.remove_one_guard(enemy_ts, star_le=3, pick_high=True)

        elif card.name == "白象精":
            self.remove_one_guard(enemy_ts, star_le=4, to_hand=True, pick_high=True)

        elif card.name == "牛魔王":
            extra = self.best_monster_in_hand(player)
            destination = self.best_place_for_guard(player)
            if extra is not None and destination is not None:
                self.hands[player].remove(extra)
                self.played_public_card_this_turn = True
                self.place_guard(player, destination, extra)

        elif card.name == "大鹏精":
            self.try_attack(player, force=True)

    def resolve_you_lai_you_qu(self, player: int) -> None:
        if not self.deck:
            return
        top = self.deck[:2]
        self.deck = self.deck[2:]
        chosen = max(top, key=lambda c: (c.star, card_priority(c.name)))
        top.remove(chosen)
        chosen.owner = player
        self.hands[player].append(chosen)
        self.deck.extend(top)

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

        source, guard = (
            max(candidates, key=lambda pair: (pair[1].star, card_priority(pair[1].name)))
            if pick_high
            else self.rng.choice(candidates)
        )
        source.guards.remove(guard)
        if new_owner is not None:
            guard.owner = new_owner
        if to_hand:
            if guard.owner is not None:
                self.hands[guard.owner].append(guard)
        else:
            self.discard_or_return(guard)
        self.return_empty_owned_territories()
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

    def best_place_for_guard(self, player: int) -> Optional[Territory]:
        candidates = [t for t in self.owned[player] if len(t.guards) < MAX_GUARDS] + list(self.center)
        return max(candidates, key=lambda t: domain_need_score(player, t, self.owned)) if candidates else None

    def consume_jingangzhuo(self, excluding_player: int) -> bool:
        holders = [
            player
            for player in self.players
            if player != excluding_player
            and any(card.name == "金刚琢" for card in self.hands[player])
        ]
        if not holders:
            return False
        user = max(holders, key=lambda player: len(self.hands[player]))
        counter = next(card for card in self.hands[user] if card.name == "金刚琢")
        self.hands[user].remove(counter)
        counter.owner = None
        self.discard.append(counter)
        self.played_public_card_this_turn = True
        return True

    def legal_active_treasures(self, player: int) -> List[Card]:
        result: List[Card] = []
        for card in self.hands[player]:
            if card.name == "金刚琢":
                continue
            if card.name == "辟火罩" and any(not t.protected for t in self.owned[player]):
                result.append(card)
            elif card.name in ("幌金绳", "紫金红葫芦") and self.unprotected_enemy_territories(player):
                result.append(card)
        return result

    def use_treasure(self, player: int, card: Card) -> bool:
        enemy_ts = self.unprotected_enemy_territories(player)

        if card.name == "辟火罩":
            candidates = [t for t in self.owned[player] if not t.protected]
            if not candidates:
                return False
            self.hands[player].remove(card)
            card.owner = None
            self.discard.append(card)
            self.played_public_card_this_turn = True
            if self.consume_jingangzhuo(player):
                return True
            target = max(
                candidates,
                key=lambda t: (
                    sum(1 for x in self.owned[player] if x.domain == t.domain),
                    sum(g.star for g in t.guards),
                ),
            )
            target.protected = True
            return True

        if card.name == "幌金绳":
            candidates = [(territory, guard) for territory in enemy_ts for guard in territory.guards]
            if not candidates:
                return False
            self.hands[player].remove(card)
            card.owner = None
            self.discard.append(card)
            self.played_public_card_this_turn = True
            if self.consume_jingangzhuo(player):
                return True
            source, guard = max(
                candidates,
                key=lambda pair: (pair[1].star, card_priority(pair[1].name)),
            )
            source.guards.remove(guard)
            guard.owner = player
            self.hands[player].append(guard)
            self.return_empty_owned_territories()
            return True

        if card.name == "紫金红葫芦":
            valid_players = [
                target
                for target in self.players
                if target != player
                and any(t.guards and not t.protected for t in self.owned[target])
            ]
            if not valid_players:
                return False
            target_player = max(
                valid_players,
                key=lambda target: max(
                    guard.star
                    for territory in self.owned[target]
                    if not territory.protected
                    for guard in territory.guards
                ),
            )
            self.hands[player].remove(card)
            card.owner = None
            self.discard.append(card)
            self.played_public_card_this_turn = True
            if self.rng.random() >= self.answer_probability():
                return True
            if self.consume_jingangzhuo(player):
                return True
            candidates = [
                (territory, guard)
                for territory in self.owned[target_player]
                if not territory.protected
                for guard in territory.guards
            ]
            source, guard = max(
                candidates,
                key=lambda pair: (pair[1].star, card_priority(pair[1].name)),
            )
            source.guards.remove(guard)
            guard.owner = player
            self.hands[player].append(guard)
            self.return_empty_owned_territories()
            return True

        return False

    def recruit_best(self, player: int) -> bool:
        monster = self.best_monster_in_hand(player)
        destination = self.best_place_for_guard(player)
        if monster is None or destination is None:
            return False
        self.hands[player].remove(monster)
        self.played_public_card_this_turn = True
        self.place_guard(player, destination, monster)
        return True

    def should_recruit_before_attack(self, player: int) -> bool:
        territories = self.owned[player]
        if not territories or sum(len(t.guards) for t in territories) <= len(territories):
            return True
        domains: Dict[str, int] = {}
        for territory in territories:
            domains[territory.domain] = domains.get(territory.domain, 0) + 1
        return any(value >= 2 for value in domains.values()) and any(
            len(t.guards) < 2 for t in territories
        )

    def generate_battle_results(
        self,
        attackers: Sequence[Card],
        defenders: Sequence[Card],
    ) -> List[BattleResult]:
        results: List[BattleResult] = []

        for order in itertools.permutations(attackers):
            def recurse(
                index: int,
                live_defenders: List[Card],
                damage: Dict[int, int],
                live_attackers: List[Card],
                dead_attackers: List[Card],
                dead_defenders: List[Card],
            ) -> None:
                if index >= len(order) or not live_defenders:
                    results.append(
                        BattleResult(
                            success=not live_defenders and bool(live_attackers),
                            attack_order=order,
                            surviving_attackers=list(live_attackers),
                            dead_attackers=list(dead_attackers),
                            surviving_defenders=list(live_defenders),
                            dead_defenders=list(dead_defenders),
                        )
                    )
                    return

                attacker = order[index]
                for target in list(live_defenders):
                    next_live_defenders = list(live_defenders)
                    next_damage = dict(damage)
                    next_live_attackers = list(live_attackers)
                    next_dead_attackers = list(dead_attackers)
                    next_dead_defenders = list(dead_defenders)

                    next_damage[target.uid] = next_damage.get(target.uid, 0) + attacker.star

                    if target.star >= attacker.star:
                        next_live_attackers.remove(attacker)
                        next_dead_attackers.append(attacker)

                    if next_damage[target.uid] >= target.star:
                        next_live_defenders.remove(target)
                        next_dead_defenders.append(target)

                    recurse(
                        index + 1,
                        next_live_defenders,
                        next_damage,
                        next_live_attackers,
                        next_dead_attackers,
                        next_dead_defenders,
                    )

            recurse(0, list(defenders), {}, list(order), [], [])

        unique: Dict[Tuple, BattleResult] = {}
        for result in results:
            key = (
                tuple(card.uid for card in result.attack_order),
                tuple(sorted(card.uid for card in result.surviving_attackers)),
                tuple(sorted(card.uid for card in result.surviving_defenders)),
            )
            unique[key] = result
        return list(unique.values())

    def battle_score(
        self,
        player: int,
        source: Territory,
        target: Territory,
        result: BattleResult,
    ) -> float:
        own_same = sum(1 for t in self.owned[player] if t.domain == target.domain)
        target_threat = 0
        if target.owner is not None:
            target_threat = sum(
                1 for t in self.owned[target.owner] if t.domain == target.domain
            )

        value_killed = sum(
            guard.star * 5 + card_priority(guard.name) / 20
            for guard in result.dead_defenders
        )
        value_lost = sum(
            guard.star * 5 + card_priority(guard.name) / 20
            for guard in result.dead_attackers
        )
        score = value_killed - value_lost

        if result.success:
            score += 55 + own_same * 35
            if own_same >= 2:
                score += 200
            if target_threat >= 2:
                score += 90
        else:
            score -= 8
            if not result.surviving_defenders:
                score += 20

        if len(source.guards) == len(result.attack_order) and not result.surviving_attackers:
            score -= 25
        return score

    def choose_battle_plan(self, player: int) -> Optional[BattlePlan]:
        plans: List[BattlePlan] = []
        sources = [t for t in self.owned[player] if t.guards]
        targets = self.unprotected_enemy_territories(player)

        for source in sources:
            for target in targets:
                for count in range(1, min(MAX_GUARDS, len(source.guards)) + 1):
                    for group in itertools.combinations(source.guards, count):
                        for result in self.generate_battle_results(group, target.guards):
                            plans.append(
                                BattlePlan(
                                    score=self.battle_score(player, source, target, result),
                                    source=source,
                                    target=target,
                                    result=result,
                                )
                            )
        return max(plans, key=lambda plan: plan.score) if plans else None

    def try_attack(self, player: int, force: bool = False) -> bool:
        plan = self.choose_battle_plan(player)
        if plan is None:
            return False

        threshold = -999 if force else (-5 if self.ai == "aggressive" else 10)
        if plan.score < threshold:
            return False

        source = plan.source
        target = plan.target
        result = plan.result

        for guard in result.attack_order:
            if guard in source.guards:
                source.guards.remove(guard)
        for guard in list(target.guards):
            target.guards.remove(guard)
        for guard in result.dead_attackers + result.dead_defenders:
            self.discard_or_return(guard)

        if result.success:
            old_owner = target.owner
            if old_owner is not None and target in self.owned[old_owner]:
                self.owned[old_owner].remove(target)
            target.owner = player
            target.protected = False
            target.guards = list(result.surviving_attackers)
            for guard in target.guards:
                guard.owner = player
            self.owned[player].append(target)
            self.successful_attacks += 1
            self.control_changed_this_turn = True
        else:
            target.guards = list(result.surviving_defenders)
            for guard in result.surviving_attackers:
                source.guards.append(guard)
            self.failed_attacks += 1

        self.return_empty_owned_territories()
        if result.success:
            self.mark_immediate_winner()
        return True

    def enforce_hand_limit(self, player: int) -> None:
        while len(self.hands[player]) > HAND_LIMIT:
            self.discard_lowest(player)

    def take_turn(self) -> Optional[GameResult]:
        player = self.turn_index % len(self.players)
        self.turn_index += 1
        self.turns += 1
        self.played_public_card_this_turn = False
        self.control_changed_this_turn = False
        self.immediate_winner = None

        self.draw(player)
        acted = False

        if self.ai == "aggressive":
            acted = self.try_attack(player)
            if not acted:
                for treasure in sorted(
                    self.legal_active_treasures(player),
                    key=lambda card: card_priority(card.name),
                    reverse=True,
                ):
                    if self.use_treasure(player, treasure):
                        acted = True
                        break
            if not acted:
                acted = self.recruit_best(player)
        else:
            if self.should_recruit_before_attack(player):
                acted = self.recruit_best(player)
            if not acted:
                acted = self.try_attack(player)
            if not acted:
                for treasure in sorted(
                    self.legal_active_treasures(player),
                    key=lambda card: card_priority(card.name),
                    reverse=True,
                ):
                    if self.use_treasure(player, treasure):
                        acted = True
                        break
            if not acted:
                acted = self.recruit_best(player)

        self.enforce_hand_limit(player)

        winner = (
            self.immediate_winner
            if self.immediate_winner is not None
            else self.check_winner()
        )
        if winner is not None:
            return GameResult(
                winner,
                "同妖域3地盘",
                self.turns,
                len(self.deck),
                self.deck_empty_once,
                self.territory_returns,
                self.successful_attacks,
                self.failed_attacks,
                False,
            )

        if not self.deck:
            if not self.played_public_card_this_turn and not self.control_changed_this_turn:
                self.no_progress_round += 1
            else:
                self.no_progress_round = 0
            if self.no_progress_round >= len(self.players):
                winner = self.settlement_winner()
                return GameResult(
                    winner,
                    "公共牌库耗尽结算" if winner is not None else "平局结算",
                    self.turns,
                    0,
                    True,
                    self.territory_returns,
                    self.successful_attacks,
                    self.failed_attacks,
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
                self.failed_attacks,
                False,
            )
        return None

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
    successful = [r.successful_attacks for r in results]
    failed = [r.failed_attacks for r in results]
    deck_left = [r.deck_left for r in results]
    settlement_wins = reasons.get("公共牌库耗尽结算", 0)
    settlement_draws = reasons.get("平局结算", 0)

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
        "direct_wins": reasons.get("同妖域3地盘", 0),
        "settlement_wins": settlement_wins,
        "settlement_draws": settlement_draws,
        "timeouts": reasons.get("超时", 0),
        "avg_turns": round(mean(turns), 2),
        "avg_rounds": round(mean(turns) / players_count, 2),
        "median_turns": median(turns),
        "p90_turns": sorted(turns)[max(0, int(games * 0.9) - 1)],
        "avg_deck_left": round(mean(deck_left), 2),
        "deck_empty_rate": round(
            sum(1 for result in results if result.deck_empty) / games,
            4,
        ),
        "settlement_rate": round(
            (settlement_wins + settlement_draws) / games,
            4,
        ),
        "avg_territory_returns": round(mean(returns), 2),
        "avg_successful_attacks": round(mean(successful), 2),
        "avg_failed_attacks": round(mean(failed), 2),
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
