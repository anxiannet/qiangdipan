#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《夕妖：抢地盘》基础版 AI 自动模拟器

用途：
- 验证基础版2~4人规则是否闭环。
- 对比不同公共牌库复制数方案。
- 对比不同AI行为模型对游戏收束、地盘回流、空库结算的影响。

内置牌库 preset：
1. current_58：当前V1.2基础公共牌库，58张。
2. reduced_42：1星、2星每种改为2张，公共牌库42张。

内置AI：
1. aggressive：压力测试AI。能抢就抢，用于放大互抢、回流、空库风险。
2. human_like：真人近似AI。目标导向，避免无意义互抢，避免轻易掏空自己的地盘。

玩家人数：
--players 支持 2、3、4。

运行：
python3 测试代码/4人基础版AI模拟器.py --players 2 --preset current_58 --ai human_like --games 3000 --seed 20260705
python3 测试代码/4人基础版AI模拟器.py --players 3 --preset current_58 --ai human_like --games 3000 --seed 20260705
python3 测试代码/4人基础版AI模拟器.py --players 4 --preset current_58 --ai human_like --games 3000 --seed 20260705
python3 测试代码/4人基础版AI模拟器.py --players 4 --preset reduced_42 --ai aggressive --games 3000 --seed 20260705

注意：
本代码是规则验证型AI，不是强竞技AI。
AI策略用于发现规则闭环、节奏、牌库耗尽、地盘回流等问题，不能替代真人试玩。
"""

from __future__ import annotations

import argparse
import itertools
import random
from dataclasses import dataclass, field
from statistics import mean, median
from typing import Dict, List, Optional, Tuple


DOMAINS = {
    "白骨": ["白骨岭", "埋骨坡", "乱葬岗"],
    "火云": ["火焰山", "翠云山", "芭蕉洞"],
    "狮驼": ["狮驼岭", "狮驼洞", "狮驼国"],
    "盘丝": ["盘丝洞", "黄花观", "濯垢泉"],
}


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


@dataclass
class GameResult:
    winner: Optional[int]
    reason: str
    turns: int
    deck_left: int
    deck_empty: bool
    territory_returns: int
    successful_attacks: int
    draw_settlement: bool


class Game:
    def __init__(self, preset: str, ai: str, players_count: int, seed: int):
        if ai not in ("aggressive", "human_like"):
            raise ValueError(f"未知AI: {ai}")
        if players_count not in (2, 3, 4):
            raise ValueError(f"基础版仅支持2~4人测试，当前players={players_count}")
        self.ai = ai
        self.players = list(range(players_count))
        self.rng = random.Random(seed)
        self.turn_index = 0
        self.turns = 0
        self.hands: Dict[int, List[Card]] = {p: [] for p in self.players}
        self.discard: List[Card] = []
        self.deck: List[Card] = build_public_deck(preset)
        self.rng.shuffle(self.deck)
        self.territory_deck: List[Territory] = build_territory_deck()
        self.rng.shuffle(self.territory_deck)
        self.center: List[Territory] = []
        self.owned: Dict[int, List[Territory]] = {p: [] for p in self.players}
        self.territory_returns = 0
        self.successful_attacks = 0
        self.no_progress_round = 0
        self.deck_empty_once = False

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
        while len(self.center) < 3 and self.territory_deck:
            t = self.territory_deck.pop(0)
            t.owner = None
            t.guards = []
            self.center.append(t)

    def all_territories(self) -> List[Territory]:
        out = list(self.center)
        for ts in self.owned.values():
            out.extend(ts)
        return out

    def check_winner(self) -> Optional[int]:
        for p in self.players:
            domains: Dict[str, int] = {}
            for t in self.owned[p]:
                domains[t.domain] = domains.get(t.domain, 0) + 1
            if any(v >= 3 for v in domains.values()):
                return p
        return None

    def return_empty_owned_territories(self) -> None:
        changed = True
        while changed:
            changed = False
            for p in self.players:
                for t in list(self.owned[p]):
                    if not t.guards:
                        self.owned[p].remove(t)
                        t.owner = None
                        t.guards = []
                        self.territory_deck.append(t)
                        self.rng.shuffle(self.territory_deck)
                        self.territory_returns += 1
                        changed = True
            self.refill_center()

    def place_guard(self, player: int, territory: Territory, card: Card) -> None:
        if territory.owner is None:
            if territory in self.center:
                self.center.remove(territory)
            territory.owner = player
            self.owned[player].append(territory)
            self.refill_center()
        territory.guards.append(card)
        self.resolve_enter_skill(player, card)
        self.return_empty_owned_territories()

    def resolve_enter_skill(self, player: int, card: Card) -> None:
        enemies = [p for p in self.players if p != player]
        enemy_territories = [t for p in enemies for t in self.owned[p]]
        own_territories = self.owned[player]

        if card.name == "有来有去":
            self.draw(player, 1)
            self.discard_lowest(player)
        elif card.name == "急如火":
            if enemies and self.rng.random() < 0.5:
                target = self.rng.choice(enemies)
                self.draw(player, 1)
                self.draw(target, 1)
        elif card.name in ("云里雾", "雾里云"):
            self.rng.shuffle(self.deck)
        elif card.name == "银角大王":
            top = self.deck[:3]
            self.deck = self.deck[3:]
            top.sort(key=lambda c: (c.star, card_priority(c.name)), reverse=True)
            self.deck = top + self.deck
        elif card.name == "白骨精":
            pass
        elif card.name == "玉面狐狸":
            bulls = [g for t in self.all_territories() for g in t.guards if g.name == "牛魔王"]
            if bulls and own_territories:
                target_t = max(own_territories, key=lambda t: domain_need_score(player, t, self.owned))
                if len(target_t.guards) < 3:
                    bull = bulls[0]
                    for t in self.all_territories():
                        if bull in t.guards:
                            t.guards.remove(bull)
                            break
                    target_t.guards.append(bull)
        elif card.name == "金鼻白毛老鼠精":
            candidates = [(t, g) for t in enemy_territories for g in t.guards if g.star == 1]
            if candidates and own_territories:
                src, g = self.rng.choice(candidates)
                target_t = max(own_territories, key=lambda t: domain_need_score(player, t, self.owned))
                if len(target_t.guards) < 3:
                    src.guards.remove(g)
                    g.owner = player
                    target_t.guards.append(g)
        elif card.name == "黄袍怪":
            candidates = [(t, g) for t in enemy_territories for g in t.guards if g.star == 1]
            if candidates:
                src, g = self.rng.choice(candidates)
                src.guards.remove(g)
                g.owner = player
                self.hands[player].append(g)
        elif card.name == "铁扇公主":
            candidates = [(t, g) for t in enemy_territories for g in t.guards]
            if candidates:
                src, g = max(candidates, key=lambda x: x[1].star)
                src.guards.remove(g)
                self.hands[g.owner if g.owner is not None else player].append(g)
        elif card.name == "红孩儿":
            if enemy_territories:
                t = max(enemy_territories, key=lambda x: sum(1 for g in x.guards if g.star == 1))
                for g in list(t.guards):
                    if g.star == 1:
                        t.guards.remove(g)
                        self.discard_or_return(g)
        elif card.name == "黄风怪":
            if enemy_territories:
                t = max(enemy_territories, key=lambda x: sum(1 for g in x.guards if g.star < 3))
                targets = sorted([g for g in t.guards if g.star < 3], key=lambda g: g.star, reverse=True)[:2]
                for g in targets:
                    t.guards.remove(g)
                    self.hands[g.owner if g.owner is not None else player].append(g)
        elif card.name == "青狮精":
            candidates = [(t, g) for t in enemy_territories for g in t.guards if g.star <= 4]
            if candidates:
                src, g = max(candidates, key=lambda x: x[1].star)
                src.guards.remove(g)
                self.discard_or_return(g)
        elif card.name == "牛魔王":
            c = self.best_monster_in_hand(player)
            if c:
                target = self.best_place_for_guard(player)
                if target:
                    self.hands[player].remove(c)
                    self.place_guard(player, target, c)
        elif card.name == "大鹏精":
            self.try_attack(player)

    def discard_lowest(self, player: int) -> None:
        if not self.hands[player]:
            return
        c = min(self.hands[player], key=lambda x: (x.star, card_priority(x.name)))
        self.hands[player].remove(c)
        self.discard.append(c)

    def discard_or_return(self, card: Card) -> None:
        if card.name == "白骨精":
            card.owner = None
            self.deck.append(card)
            self.rng.shuffle(self.deck)
        else:
            self.discard.append(card)

    def best_monster_in_hand(self, player: int) -> Optional[Card]:
        cards = [c for c in self.hands[player] if c.kind == "妖怪"]
        if not cards:
            return None
        return max(cards, key=lambda c: (c.star, card_priority(c.name)))

    def best_treasure_in_hand(self, player: int) -> Optional[Card]:
        cards = [c for c in self.hands[player] if c.kind == "法宝"]
        if not cards:
            return None
        return max(cards, key=lambda c: card_priority(c.name))

    def best_place_for_guard(self, player: int) -> Optional[Territory]:
        candidates: List[Territory] = [t for t in self.owned[player] if len(t.guards) < 3]
        candidates += list(self.center)
        if not candidates:
            return None
        return max(candidates, key=lambda t: domain_need_score(player, t, self.owned))

    def use_treasure(self, player: int, card: Card) -> bool:
        enemies = [p for p in self.players if p != player]
        enemy_territories = [t for p in enemies for t in self.owned[p]]
        if card.name == "芭蕉扇" and enemy_territories:
            t = max(enemy_territories, key=lambda x: len(x.guards))
            for g in list(t.guards):
                t.guards.remove(g)
                if g.owner is not None:
                    self.hands[g.owner].append(g)
            self.hands[player].remove(card)
            self.discard.append(card)
            self.return_empty_owned_territories()
            return True
        if card.name in ("幌金绳", "紫金红葫芦") and enemy_territories:
            candidates = [(t, g) for t in enemy_territories for g in t.guards]
            if candidates:
                src, g = max(candidates, key=lambda x: x[1].star)
                src.guards.remove(g)
                g.owner = player
                self.hands[player].append(g)
                self.hands[player].remove(card)
                self.discard.append(card)
                self.return_empty_owned_territories()
                return True
        return False

    def recruit_best(self, player: int) -> bool:
        monster = self.best_monster_in_hand(player)
        target = self.best_place_for_guard(player)
        if monster and target:
            self.hands[player].remove(monster)
            self.place_guard(player, target, monster)
            return True
        return False

    def should_recruit_before_attack(self, player: int) -> bool:
        territories = self.owned[player]
        if not territories:
            return True
        guard_count = sum(len(t.guards) for t in territories)
        if guard_count <= len(territories):
            return True
        domains: Dict[str, int] = {}
        for t in territories:
            domains[t.domain] = domains.get(t.domain, 0) + 1
        has_two_domain = any(v >= 2 for v in domains.values())
        if has_two_domain and any(len(t.guards) < 2 for t in territories):
            return True
        return False

    def attack_score(self, player: int, src: Territory, dst: Territory, attackers: List[Card], survivors: List[Card]) -> int:
        own_same_before = sum(1 for t in self.owned[player] if t.domain == dst.domain)
        direct_win = own_same_before >= 2
        old_owner = dst.owner
        block_threat = False
        if old_owner is not None and old_owner != player:
            enemy_same = sum(1 for t in self.owned[old_owner] if t.domain == dst.domain)
            block_threat = enemy_same >= 2

        source_empty = len(src.guards) == len(attackers)
        attacker_stars = sum(g.star for g in attackers)
        defender_stars = sum(g.star for g in dst.guards)
        score = 0
        score += own_same_before * 30
        score += defender_stars * 3
        score += len(survivors) * 6
        score -= attacker_stars * 2

        if direct_win:
            score += 120
        if block_threat:
            score += 80
        if source_empty:
            score -= 45
        if source_empty and (direct_win or block_threat):
            score += 35
        if dst.domain not in [t.domain for t in self.owned[player]]:
            score -= 12
        return score

    def try_attack(self, player: int) -> bool:
        own = [t for t in self.owned[player] if t.guards]
        targets = [t for p in self.players if p != player for t in self.owned[p] if t.guards]
        if not own or not targets:
            return False

        best: Optional[Tuple[int, Territory, Territory, List[Card], List[Card], List[Card]]] = None
        for src in own:
            guards = list(src.guards)
            for r in range(1, min(3, len(guards)) + 1):
                for attackers in itertools.combinations(guards, r):
                    for dst in targets:
                        ok, survivors, dead_attackers = battle_outcome(list(attackers), list(dst.guards))
                        if ok and survivors:
                            if self.ai == "aggressive":
                                score = domain_need_score(player, dst, self.owned) * 10 + sum(g.star for g in dst.guards) - sum(g.star for g in attackers)
                            else:
                                score = self.attack_score(player, src, dst, list(attackers), survivors)
                            if best is None or score > best[0]:
                                best = (score, src, dst, list(attackers), survivors, dead_attackers)
        if best is None:
            return False

        score, src, dst, attackers, survivors, dead_attackers = best
        if self.ai == "human_like" and score < 30:
            return False

        for g in attackers:
            if g in src.guards:
                src.guards.remove(g)
        for g in list(dst.guards):
            dst.guards.remove(g)
            self.discard_or_return(g)
        for g in dead_attackers:
            if g in survivors:
                survivors.remove(g)
            self.discard_or_return(g)
        old_owner = dst.owner
        if old_owner is not None and dst in self.owned[old_owner]:
            self.owned[old_owner].remove(dst)
        dst.owner = player
        dst.guards = survivors[:3]
        for g in dst.guards:
            g.owner = player
        self.owned[player].append(dst)
        self.successful_attacks += 1
        self.return_empty_owned_territories()
        return True

    def take_turn(self) -> Optional[GameResult]:
        player = self.turn_index % len(self.players)
        self.turn_index += 1
        self.turns += 1
        progress_before = self.snapshot_progress()

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

        winner = self.check_winner()
        if winner is not None:
            return GameResult(winner, "同妖域3地盘", self.turns, len(self.deck), self.deck_empty_once, self.territory_returns, self.successful_attacks, False)

        if not self.deck:
            after = self.snapshot_progress()
            if after == progress_before:
                self.no_progress_round += 1
            else:
                self.no_progress_round = 0
            if self.no_progress_round >= len(self.players):
                winner = self.settlement_winner()
                reason = "公共牌库耗尽结算" if winner is not None else "平局结算"
                return GameResult(winner, reason, self.turns, len(self.deck), True, self.territory_returns, self.successful_attacks, True)

        if self.turns >= 200:
            return GameResult(None, "超时", self.turns, len(self.deck), self.deck_empty_once, self.territory_returns, self.successful_attacks, False)
        return None

    def snapshot_progress(self) -> Tuple:
        return tuple((p, tuple(sorted((t.name, tuple(g.name for g in t.guards)) for t in self.owned[p]))) for p in self.players)

    def settlement_winner(self) -> Optional[int]:
        scores = []
        for p in self.players:
            territories = self.owned[p]
            domain_max = max([sum(1 for t in territories if t.domain == d) for d in DOMAINS] or [0])
            guard_stars = sum(g.star for t in territories for g in t.guards)
            guard_count = sum(len(t.guards) for t in territories)
            scores.append((len(territories), guard_stars, domain_max, guard_count, p))
        scores.sort(reverse=True)
        if len(scores) > 1 and scores[0][:4] == scores[1][:4]:
            return None
        return scores[0][4]


def battle_outcome(attackers: List[Card], defenders: List[Card]) -> Tuple[bool, List[Card], List[Card]]:
    defenders_hp = {id(g): g.star for g in defenders}
    live_def = list(defenders)
    live_atk = list(attackers)
    dead_atk: List[Card] = []

    attack_order = sorted(attackers, key=lambda g: (g.star, card_priority(g.name)))
    for atk in attack_order:
        if not live_def:
            break
        target = max(live_def, key=lambda g: g.star)
        defenders_hp[id(target)] -= atk.star
        if atk.star <= target.star:
            if atk in live_atk:
                live_atk.remove(atk)
            dead_atk.append(atk)
        if defenders_hp[id(target)] <= 0:
            live_def.remove(target)
    success = len(live_def) == 0 and len(live_atk) > 0
    return success, live_atk, dead_atk


def build_public_deck(preset: str) -> List[Card]:
    counts_current = {
        "小钻风": ("妖怪", 1, 4), "有来有去": ("妖怪", 1, 4), "精细鬼": ("妖怪", 1, 4),
        "伶俐虫": ("妖怪", 1, 4), "急如火": ("妖怪", 1, 4), "快如风": ("妖怪", 1, 4),
        "云里雾": ("妖怪", 2, 4), "雾里云": ("妖怪", 2, 4),
        "金角大王": ("妖怪", 3, 2), "银角大王": ("妖怪", 3, 2), "白骨精": ("妖怪", 3, 2),
        "玉面狐狸": ("妖怪", 3, 2), "金鼻白毛老鼠精": ("妖怪", 3, 2), "黄袍怪": ("妖怪", 3, 2),
        "铁扇公主": ("妖怪", 3, 2),
        "红孩儿": ("妖怪", 4, 2), "黄风怪": ("妖怪", 4, 2), "青狮精": ("妖怪", 4, 2),
        "牛魔王": ("妖怪", 5, 1), "大鹏精": ("妖怪", 5, 1),
        "紫金红葫芦": ("法宝", 0, 1), "金刚琢": ("法宝", 0, 1), "幌金绳": ("法宝", 0, 1), "芭蕉扇": ("法宝", 0, 1),
    }
    if preset == "current_58":
        counts = counts_current
    elif preset == "reduced_42":
        counts = dict(counts_current)
        for name, (kind, star, count) in list(counts.items()):
            if kind == "妖怪" and star in (1, 2):
                counts[name] = (kind, star, 2)
    else:
        raise ValueError(f"未知preset: {preset}")

    deck: List[Card] = []
    uid = 0
    for name, (kind, star, count) in counts.items():
        for _ in range(count):
            deck.append(Card(name=name, kind=kind, star=star, uid=uid))
            uid += 1
    return deck


def build_territory_deck() -> List[Territory]:
    return [Territory(domain=d, name=n) for d, names in DOMAINS.items() for n in names]


def card_priority(name: str) -> int:
    return {
        "芭蕉扇": 100, "幌金绳": 92, "金刚琢": 88, "大鹏精": 86, "青狮精": 78, "黄风怪": 76,
        "红孩儿": 74, "牛魔王": 68, "铁扇公主": 64, "金角大王": 60, "金鼻白毛老鼠精": 60,
        "黄袍怪": 55, "紫金红葫芦": 45, "银角大王": 42, "玉面狐狸": 42,
        "云里雾": 38, "雾里云": 36, "小钻风": 30, "有来有去": 28, "精细鬼": 28,
        "伶俐虫": 26, "快如风": 26, "急如火": 18,
    }.get(name, 0)


def domain_need_score(player: int, territory: Territory, owned: Dict[int, List[Territory]]) -> int:
    have = sum(1 for t in owned[player] if t.domain == territory.domain)
    return have * 10 + (3 - len(territory.guards))


def run_batch(preset: str, ai: str, players_count: int, games: int, seed: int) -> Dict[str, object]:
    results: List[GameResult] = []
    for i in range(games):
        g = Game(preset, ai, players_count, seed + i)
        result = None
        while result is None:
            result = g.take_turn()
        results.append(result)

    winners = {p: sum(1 for r in results if r.winner == p) for p in range(players_count)}
    draws = sum(1 for r in results if r.winner is None)
    reasons: Dict[str, int] = {}
    for r in results:
        reasons[r.reason] = reasons.get(r.reason, 0) + 1
    turns = [r.turns for r in results]
    deck_left = [r.deck_left for r in results]
    returns = [r.territory_returns for r in results]
    attacks = [r.successful_attacks for r in results]

    return {
        "preset": preset,
        "ai": ai,
        "players": players_count,
        "games": games,
        "seed": seed,
        "winners": winners,
        "draws": draws,
        "reasons": reasons,
        "avg_turns": round(mean(turns), 2),
        "median_turns": median(turns),
        "p90_turns": sorted(turns)[int(games * 0.9) - 1],
        "avg_deck_left": round(mean(deck_left), 2),
        "deck_empty_games": sum(1 for r in results if r.deck_empty),
        "avg_territory_returns": round(mean(returns), 2),
        "avg_successful_attacks": round(mean(attacks), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--players", type=int, choices=[2, 3, 4], default=4)
    parser.add_argument("--preset", choices=["current_58", "reduced_42"], default="reduced_42")
    parser.add_argument("--ai", choices=["aggressive", "human_like"], default="aggressive")
    parser.add_argument("--games", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=20260705)
    args = parser.parse_args()

    summary = run_batch(args.preset, args.ai, args.players, args.games, args.seed)
    print("=== 基础版AI模拟结果 ===")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
