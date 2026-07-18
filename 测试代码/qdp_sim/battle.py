from __future__ import annotations

import itertools
from typing import Dict, List, Sequence, Tuple

from .models import BattleResult, Card


def generate_battle_results(
    attackers: Sequence[Card],
    defenders: Sequence[Card],
) -> List[BattleResult]:
    """枚举攻方顺序与每次守方目标，返回所有不同战斗结果。"""
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
