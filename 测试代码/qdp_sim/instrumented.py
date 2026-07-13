from __future__ import annotations

from typing import Dict, Set

from .models import Card
from .rules_030 import FireCloud030Game

EXPANSION_CARDS = (
    "云里雾",
    "雾里云",
    "兴烘掀",
    "掀烘兴",
    "玉面狐狸",
    "铁扇公主",
    "红孩儿",
    "芭蕉扇",
)


class InstrumentedFireCloudGame(FireCloud030Game):
    """记录扩展卡出场、触发与资源影响，不改变规则结算。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expansion_stats: Dict[str, Dict[str, int]] = {
            name: {
                "plays": 0,
                "triggers": 0,
                "cards_drawn": 0,
                "cards_discarded": 0,
                "guards_removed": 0,
            }
            for name in EXPANSION_CARDS
        }
        self.expansion_played_by_player: Dict[str, Set[int]] = {
            name: set() for name in EXPANSION_CARDS
        }

    def _guard_count(self) -> int:
        return sum(
            len(territory.guards)
            for player in self.players
            for territory in self.owned[player]
        )

    def _hand_count(self) -> int:
        return sum(len(self.hands[player]) for player in self.players)

    def resolve_enter_skill(self, player: int, card: Card) -> None:
        if card.name not in self.expansion_stats:
            super().resolve_enter_skill(player, card)
            return

        stat = self.expansion_stats[card.name]
        stat["plays"] += 1
        self.expansion_played_by_player[card.name].add(player)

        before_player_hand = len(self.hands[player])
        before_all_hands = self._hand_count()
        before_discard = len(self.discard)
        before_guards = self._guard_count()

        super().resolve_enter_skill(player, card)

        player_hand_delta = len(self.hands[player]) - before_player_hand
        all_hand_delta = self._hand_count() - before_all_hands
        discard_delta = len(self.discard) - before_discard
        guard_delta = before_guards - self._guard_count()

        stat["cards_drawn"] += max(0, player_hand_delta)
        stat["cards_discarded"] += max(0, discard_delta)
        stat["guards_removed"] += max(0, guard_delta)
        if player_hand_delta or all_hand_delta or discard_delta or guard_delta:
            stat["triggers"] += 1

    def use_treasure(self, player: int, card: Card) -> bool:
        if card.name != "芭蕉扇":
            return super().use_treasure(player, card)

        stat = self.expansion_stats[card.name]
        before_discard = len(self.discard)
        before_guards = self._guard_count()
        used = super().use_treasure(player, card)
        if not used:
            return False

        stat["plays"] += 1
        self.expansion_played_by_player[card.name].add(player)
        discard_delta = len(self.discard) - before_discard
        guard_delta = before_guards - self._guard_count()
        stat["cards_discarded"] += max(0, discard_delta - 1)
        stat["guards_removed"] += max(0, guard_delta)
        if guard_delta > 0:
            stat["triggers"] += 1
        return True
