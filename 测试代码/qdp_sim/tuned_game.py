from __future__ import annotations

from .data import card_priority
from .game import Game
from .models import BattleResult, Territory


class TunedGame(Game):
    """在不改变规则流程的前提下，收紧AI的低收益攻击决策。"""

    def battle_score(
        self,
        player: int,
        source: Territory,
        target: Territory,
        result: BattleResult,
    ) -> float:
        own_same = sum(
            1 for territory in self.owned[player] if territory.domain == target.domain
        )
        target_threat = 0
        if target.owner is not None:
            target_threat = sum(
                1
                for territory in self.owned[target.owner]
                if territory.domain == target.domain
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
            score += 60 + own_same * 40
            if own_same >= 2:
                score += 220
            if target_threat >= 2:
                score += 100
        else:
            # 失败攻击必须产生明确交换价值，否则大幅扣分。
            score -= 22
            if not result.dead_defenders:
                score -= 24
            if not result.surviving_attackers:
                score -= 18
            if result.dead_defenders and value_killed > value_lost:
                score += 8
            # 双方全灭会令目标地盘回流，保留少量战术价值。
            if not result.surviving_defenders and not result.surviving_attackers:
                score += 12

        # 全部出兵且未能占领时，额外惩罚出兵地被清空的风险。
        if len(source.guards) == len(result.attack_order) and not result.success:
            score -= 20
        return score

    def try_attack(self, player: int, force: bool = False) -> bool:
        plan = self.choose_battle_plan(player)
        if plan is None:
            return False

        # 大鹏精等强制攻击仍必须执行；普通AI只执行正收益攻击。
        threshold = -999 if force else (8 if self.ai == "aggressive" else 14)
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
