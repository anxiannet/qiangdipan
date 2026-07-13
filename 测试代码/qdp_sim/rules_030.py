from __future__ import annotations

from .expansion import TunedExpansionGame
from .models import Card
from .tuned_game import TunedGame


class CardTable030Mixin:
    """修正V1.3-卡表-030中换牌类技能的结算顺序。"""

    def resolve_enter_skill(self, player: int, card: Card) -> None:
        if self.immediate_winner is not None:
            return

        if card.name == "精细鬼":
            # 换1张：先抽1张，再从自己的手牌弃1张。
            if not self.deck:
                return
            self.draw(player)
            self.discard_lowest(player)
            return

        if card.name == "急如火":
            # 对方答应后，双方分别先抽1张，再各自弃1张。
            if not self.deck or self.rng.random() >= self.answer_probability():
                return
            targets = [other for other in self.players if other != player]
            if not targets:
                return
            target = self.rng.choice(targets)

            self.draw(player)
            self.discard_lowest(player)
            if self.deck:
                self.draw(target)
                self.discard_lowest(target)
            return

        super().resolve_enter_skill(player, card)


class Standard030Game(CardTable030Mixin, TunedGame):
    """V1.3-卡表-030标准版测试环境。"""

    pass


class FireCloud030Game(CardTable030Mixin, TunedExpansionGame):
    """V1.3-卡表-030标准版加《火云再起》测试环境。"""

    pass
