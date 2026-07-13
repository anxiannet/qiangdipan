from __future__ import annotations

from statistics import mean, median
from typing import Dict, List

from .models import GameResult
from .tuned_game import TunedGame


def run_batch(
    ai: str,
    players_count: int,
    domain_count: int,
    center_size: int,
    games: int,
    seed: int,
) -> Dict[str, object]:
    if games <= 0:
        raise ValueError("games必须大于0")

    results: List[GameResult] = []
    for index in range(games):
        game = TunedGame(ai, players_count, domain_count, center_size, seed + index)
        result = None
        while result is None:
            result = game.take_turn()
        results.append(result)

    reasons: Dict[str, int] = {}
    for result in results:
        reasons[result.reason] = reasons.get(result.reason, 0) + 1

    turns = [result.turns for result in results]
    returns = [result.territory_returns for result in results]
    successful = [result.successful_attacks for result in results]
    failed = [result.failed_attacks for result in results]
    deck_left = [result.deck_left for result in results]
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
