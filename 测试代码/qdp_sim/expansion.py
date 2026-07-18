from __future__ import annotations

import random
from typing import Dict, List, Optional

from .data import DOMAINS, MAX_GUARDS, build_public_deck, build_territory_deck, card_priority, domain_need_score
from .game import Game
from .models import Card, Territory
from .tuned_game import TunedGame

EXPANSION_NAME = "火云再起"
EXPANSION_CARD_TABLE_VERSION = "V1.3-卡表-030"


def build_fire_cloud_deck() -> List[Card]:
    deck = build_public_deck()
    uid = max(card.uid for card in deck) + 1
    additions = {
        "云里雾": ("妖怪", 1, 1),
        "雾里云": ("妖怪", 1, 1),
        "兴烘掀": ("妖怪", 2, 1),
        "掀烘兴": ("妖怪", 2, 1),
        "玉面狐狸": ("妖怪", 3, 2),
        "铁扇公主": ("妖怪", 4, 2),
        "红孩儿": ("妖怪", 5, 1),
        "芭蕉扇": ("法宝", 0, 1),
    }
    for name, (kind, star, count) in additions.items():
        for _ in range(count):
            deck.append(Card(name, kind, star, uid=uid))
            uid += 1
    if len(deck) != 50:
        raise AssertionError(f"标准版+火云再起应为50张，当前为{len(deck)}张")
    return deck


class ExpansionGame(Game):
    """标准版加《火云再起》扩展包的游戏流程。"""

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
        self.deck = build_fire_cloud_deck()
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

    def resolve_enter_skill(self, player: int, card: Card) -> None:
        super().resolve_enter_skill(player, card)
        if self.immediate_winner is not None:
            return

        if card.name in ("云里雾", "雾里云"):
            self.draw(player)

        elif card.name in ("兴烘掀", "掀烘兴"):
            targets = [other for other in self.players if other != player and self.hands[other]]
            if targets:
                target = max(targets, key=lambda other: len(self.hands[other]))
                self.discard_lowest(target)

        elif card.name == "玉面狐狸":
            bull_in_play = any(
                guard.name == "牛魔王"
                for owner in self.players
                for territory in self.owned[owner]
                for guard in territory.guards
            )
            if bull_in_play:
                self.draw(player, 2)

        elif card.name == "铁扇公主":
            if not self.hands[player]:
                return
            targets = [
                (territory, guard)
                for owner in self.players
                for territory in self.owned[owner]
                if not territory.protected
                for guard in territory.guards
                if guard.uid != card.uid
            ]
            if not targets:
                return
            self.discard_lowest(player)
            territory, guard = max(
                targets,
                key=lambda pair: (
                    pair[0].owner != player,
                    pair[1].star,
                    card_priority(pair[1].name),
                ),
            )
            territory.guards.remove(guard)
            if guard.owner is not None:
                self.hands[guard.owner].append(guard)
            self.return_empty_owned_territories()

        elif card.name == "红孩儿":
            targets = [
                territory
                for owner in self.players
                for territory in self.owned[owner]
                if not territory.protected
                and any(guard.star in (1, 2) for guard in territory.guards)
            ]
            if not targets:
                return
            target = max(
                targets,
                key=lambda territory: (
                    territory.owner != player,
                    sum(guard.star for guard in territory.guards if guard.star in (1, 2)),
                    sum(1 for guard in territory.guards if guard.star in (1, 2)),
                ),
            )
            for guard in list(target.guards):
                if guard.star in (1, 2):
                    target.guards.remove(guard)
                    self.discard_or_return(guard)
            self.return_empty_owned_territories()

    def legal_active_treasures(self, player: int) -> List[Card]:
        result = super().legal_active_treasures(player)
        if any(card.name == "芭蕉扇" for card in self.hands[player]):
            if any(
                territory.guards and not territory.protected
                for owner in self.players
                for territory in self.owned[owner]
            ):
                result.extend(card for card in self.hands[player] if card.name == "芭蕉扇")
        return result

    def use_treasure(self, player: int, card: Card) -> bool:
        if card.name != "芭蕉扇":
            return super().use_treasure(player, card)

        targets = [
            territory
            for owner in self.players
            for territory in self.owned[owner]
            if territory.guards and not territory.protected
        ]
        if not targets:
            return False

        self.hands[player].remove(card)
        card.owner = None
        self.discard.append(card)
        self.played_public_card_this_turn = True
        if self.consume_jingangzhuo(player):
            return True

        target = max(
            targets,
            key=lambda territory: (
                territory.owner != player,
                sum(guard.star for guard in territory.guards),
                len(territory.guards),
            ),
        )
        for guard in list(target.guards):
            target.guards.remove(guard)
            if guard.owner is not None:
                self.hands[guard.owner].append(guard)
        self.return_empty_owned_territories()
        return True


class TunedExpansionGame(TunedGame, ExpansionGame):
    """使用正式AI评价的《火云再起》扩展环境。"""

    pass
