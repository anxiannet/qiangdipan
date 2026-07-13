from __future__ import annotations

import argparse
import json

from .runner import run_batch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="《夕妖：抢地盘》V1.3 AI模拟器")
    parser.add_argument("--players", type=int, choices=[2, 3, 4], default=4)
    parser.add_argument("--domain-count", type=int, choices=[2, 3, 4], default=4)
    parser.add_argument("--center-size", type=int, choices=[2, 3], default=3)
    parser.add_argument(
        "--ai",
        choices=["human_like", "stress_attack", "aggressive"],
        default="human_like",
        help=(
            "human_like用于正式平衡测试；stress_attack用于高频抢地盘压力测试；"
            "aggressive为旧参数兼容别名。"
        ),
    )
    parser.add_argument(
        "--deck",
        choices=["standard", "fire_cloud"],
        default="standard",
        help="standard为40张标准版；fire_cloud为标准版+火云再起50张牌库。",
    )
    parser.add_argument("--games", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=20260713)
    parser.add_argument("--json", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = run_batch(
        args.ai,
        args.players,
        args.domain_count,
        args.center_size,
        args.games,
        args.seed,
        args.deck,
    )
    print(
        json.dumps(summary, ensure_ascii=False, indent=2)
        if args.json
        else "\n".join(f"{key}: {value}" for key, value in summary.items())
    )
