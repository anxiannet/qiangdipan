from __future__ import annotations

from statistics import mean, median
from typing import Dict, List

from .expansion import EXPANSION_NAME
from .models import GameResult
from .rules_030 import FireCloud030Game, Standard030Game


def normalize_ai(ai: str) -> tuple[str, str]:
    if ai == "human_like":
        return "human_like", "human_like"
    if ai in ("stress_attack", "aggressive"):
        return "aggressive", "stress_attack"
    raise ValueError(f"未知AI: {ai}")


def normalize_deck(deck: str) -> tuple[type, str, str, int]:
    if deck == "standard":
        return Standard030Game, "标准版", "V1.3-卡表-030", 40
    if deck == "fire_cloud":
        return FireCloud030Game, f"标准版+{EXPANSION_NAME}", "V1.3-卡表-030", 50
    raise ValueError(f"未知牌组: {deck}")


def run_batch(
    ai: str,
    players_count: int,
    domain_count: int,
    center_size: int,
    games: int,
    seed: int,
    deck: str = "standard",
) -> Dict[str, object]:
    if games <= 0:
        raise ValueError("games必须大于0")

    internal_ai, report_ai = normalize_ai(ai)
    game_class, deck_name, card_table_version, deck_size = normalize_deck(deck)
    results: List[GameResult] = []
    for index in range(games):
        game = game_class(internal_ai, players_count, domain_count, center_size, seed + index)
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
        "card_table_version": card_table_version,
        "deck": deck,
        "deck_name": deck_name,
        "deck_size": deck_size,
        "ai": report_ai,
        "ai_role": (
            "正式平衡测试主模型"
            if report_ai == "human_like"
            else "高频抢地盘与拖局风险压力测试，不用于正常平衡结论"
        ),
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
