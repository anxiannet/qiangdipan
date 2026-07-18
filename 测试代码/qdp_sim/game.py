from __future__ import annotations

import itertools
import random
from typing import Dict, List, Optional, Sequence, Tuple

from .battle import generate_battle_results
from .data import (
    DOMAINS,
    HAND_LIMIT,
    MAX_GUARDS,
    MAX_TURNS,
    build_public_deck,
    build_territory_deck,
    card_priority,
    domain_need_score,
)
from .models import BattlePlan, BattleResult, Card, GameResult, Territory


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
        self.hands: Dict[int, List[Card]] = {player: [] for player in self.players}
        self.discard: List[Card] = []
        self.deck = build_public_deck()
        self.rng.shuffle(self.deck)
        self.available_domains = self.rng.sample(list(DOMAINS), domain_count)
        self.territory_deck = build_territory_deck(self.available_domains)
        self.rng.shuffle(self.territory_deck)
        self.center: List[Territory] = []
        self.owned: Dict[int, List[Territory]] = {player: [] for player in self.players}
        self.center_size = center_size
        self.territory_returns = 0
        self.successful_attacks = 0
        self.failed_attacks = 0
        self.no_progress_round = 0
        self.deck_empty_once = False
        self.played_public_card_this_turn = False
        self.control_changed_this_turn = False
        self.immediate_winner: Optional[int] = None

        for player in self.players:
            self.draw(player, 5)
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
        enemies = [other for other in self.players if other != player]
        enemy_territories = self.unprotected_enemy_territories(player)

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
            valid = [other for other in enemies if self.hands[other]]
            if valid and self.hands[player] and self.rng.random() < self.answer_probability():
                target = self.rng.choice(valid)
                own_card = min(self.hands[player], key=lambda item: (item.star, card_priority(item.name)))
                target_card = min(self.hands[target], key=lambda item: (item.star, card_priority(item.name)))
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
            candidates = [item for item in self.discard if item.kind == "妖怪" and item.star == 1]
            if candidates:
                chosen = max(candidates, key=lambda item: card_priority(item.name))
                self.discard.remove(chosen)
                chosen.owner = player
                self.hands[player].append(chosen)

        elif card.name == "虎先锋":
            self.remove_one_guard(enemy_territories, star_eq=1)

        elif card.name == "倚海龙":
            self.remove_one_guard(enemy_territories, star_eq=1, to_hand=True)

        elif card.name == "有来有去":
            self.resolve_you_lai_you_qu(player)

        elif card.name == "金角大王":
            valid = [other for other in enemies if self.hands[other]]
            if valid:
                target = self.rng.choice(valid)
                stolen = self.rng.choice(self.hands[target])
                self.hands[target].remove(stolen)
                stolen.owner = player
                self.hands[player].append(stolen)

        elif card.name == "银角大王":
            valid = [other for other in enemies if self.hands[other]]
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
            self.remove_one_guard(enemy_territories, star_eq=1, to_hand=True, new_owner=player)

        elif card.name == "金鼻白毛老鼠精":
            candidates = [
                (territory, guard)
                for territory in enemy_territories
                for guard in territory.guards
                if guard.star == 1
            ]
            destinations = [territory for territory in self.owned[player] if len(territory.guards) < MAX_GUARDS]
            if candidates and destinations:
                source, guard = self.rng.choice(candidates)
                destination = max(
                    destinations,
                    key=lambda territory: domain_need_score(player, territory, self.owned),
                )
                source.guards.remove(guard)
                guard.owner = player
                destination.guards.append(guard)

        elif card.name == "黄风怪":
            candidates = [
                (territory, guard)
                for territory in enemy_territories
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
            self.remove_one_guard(enemy_territories, star_le=3, pick_high=True)

        elif card.name == "白象精":
            self.remove_one_guard(enemy_territories, star_le=4, to_hand=True, pick_high=True)

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
        chosen = max(top, key=lambda item: (item.star, card_priority(item.name)))
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
        card = min(self.hands[player], key=lambda item: (item.star, card_priority(item.name)))
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
        monsters = [card for card in self.hands[player] if card.kind == "妖怪"]
        return max(monsters, key=lambda item: (item.star, card_priority(item.name))) if monsters else None

    def best_place_for_guard(self, player: int) -> Optional[Territory]:
        candidates = [territory for territory in self.owned[player] if len(territory.guards) < MAX_GUARDS] + list(self.center)
        return max(candidates, key=lambda territory: domain_need_score(player, territory, self.owned)) if candidates else None

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
            if card.name == "辟火罩" and any(not territory.protected for territory in self.owned[player]):
                result.append(card)
            elif card.name in ("幌金绳", "紫金红葫芦") and self.unprotected_enemy_territories(player):
                result.append(card)
        return result

    def use_treasure(self, player: int, card: Card) -> bool:
        enemy_territories = self.unprotected_enemy_territories(player)

        if card.name == "辟火罩":
            candidates = [territory for territory in self.owned[player] if not territory.protected]
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
                key=lambda territory: (
                    sum(1 for item in self.owned[player] if item.domain == territory.domain),
                    sum(guard.star for guard in territory.guards),
                ),
            )
            target.protected = True
            return True

        if card.name == "幌金绳":
            candidates = [(territory, guard) for territory in enemy_territories for guard in territory.guards]
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
                and any(territory.guards and not territory.protected for territory in self.owned[target])
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
        if not territories or sum(len(territory.guards) for territory in territories) <= len(territories):
            return True
        domains: Dict[str, int] = {}
        for territory in territories:
            domains[territory.domain] = domains.get(territory.domain, 0) + 1
        return any(value >= 2 for value in domains.values()) and any(
            len(territory.guards) < 2 for territory in territories
        )

    def battle_score(
        self,
        player: int,
        source: Territory,
        target: Territory,
        result: BattleResult,
    ) -> float:
        own_same = sum(1 for territory in self.owned[player] if territory.domain == target.domain)
        target_threat = 0
        if target.owner is not None:
            target_threat = sum(
                1 for territory in self.owned[target.owner] if territory.domain == target.domain
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
        sources = [territory for territory in self.owned[player] if territory.guards]
        targets = self.unprotected_enemy_territories(player)

        for source in sources:
            for target in targets:
                for count in range(1, min(MAX_GUARDS, len(source.guards)) + 1):
                    for group in itertools.combinations(source.guards, count):
                        for result in generate_battle_results(group, target.guards):
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

        winner = self.immediate_winner if self.immediate_winner is not None else self.check_winner()
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
                    sum(1 for territory in territories if territory.domain == domain)
                    for domain in self.available_domains
                ]
                or [0]
            )
            scores.append(
                (
                    len(territories),
                    sum(guard.star for territory in territories for guard in territory.guards),
                    domain_max,
                    sum(len(territory.guards) for territory in territories),
                    player,
                )
            )
        scores.sort(reverse=True)
        if len(scores) > 1 and scores[0][:4] == scores[1][:4]:
            return None
        return scores[0][4]
