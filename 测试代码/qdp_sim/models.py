from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


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
