#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《夕妖：抢地盘》AI模拟器
适用规则版本：V1.3
当前同步卡表版本：V1.3-卡表-003

preset:
- v13_table_003_40：当前40张标准版
- current_58：历史58张
- reduced_42：历史42张

示例：
python3 测试代码/4人基础版AI模拟器.py --preset v13_table_003_40 --players 4 --ai human_like --games 3000 --seed 20260706 --json
"""
from __future__ import annotations
import argparse, itertools, json, random
from dataclasses import dataclass, field
from statistics import mean, median
from typing import Dict, List, Optional, Tuple

DOMAINS = {
    "白骨": ["白骨岭", "埋骨坡", "乱葬岗"],
    "火云": ["火焰山", "翠云山", "芭蕉洞"],
    "狮驼": ["狮驼岭", "狮驼洞", "狮驼国"],
    "盘丝": ["盘丝洞", "黄花观", "濯垢泉"],
}

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

@dataclass
class GameResult:
    winner: Optional[int]
    reason: str
    turns: int
    deck_left: int
    deck_empty: bool
    territory_returns: int
    successful_attacks: int
    settlement: bool

class Game:
    def __init__(self, preset: str, ai: str, players_count: int, domain_count: int, center_size: int, seed: int):
        if ai not in ("aggressive", "human_like"):
            raise ValueError(f"未知AI: {ai}")
        self.ai = ai
        self.players = list(range(players_count))
        self.rng = random.Random(seed)
        self.turn_index = 0
        self.turns = 0
        self.hands = {p: [] for p in self.players}
        self.discard = []
        self.deck = build_public_deck(preset)
        self.rng.shuffle(self.deck)
        self.available_domains = self.rng.sample(list(DOMAINS.keys()), domain_count)
        self.territory_deck = build_territory_deck(self.available_domains)
        self.rng.shuffle(self.territory_deck)
        self.center = []
        self.owned = {p: [] for p in self.players}
        self.territory_returns = 0
        self.successful_attacks = 0
        self.no_progress_round = 0
        self.deck_empty_once = False
        self.protected = {p: False for p in self.players}
        self.center_size = center_size
        for p in self.players:
            self.draw(p, 5)
        self.refill_center()
        self.turn_index = self.rng.randrange(len(self.players))

    def draw(self, player: int, count: int = 1) -> None:
        for _ in range(count):
            if not self.deck:
                self.deck_empty_once = True
                return
            c = self.deck.pop(0)
            c.owner = player
            self.hands[player].append(c)

    def refill_center(self) -> None:
        while len(self.center) < self.center_size and self.territory_deck:
            t = self.territory_deck.pop(0)
            t.owner = None
            t.guards = []
            self.center.append(t)

    def check_winner(self) -> Optional[int]:
        for p in self.players:
            d: Dict[str, int] = {}
            for t in self.owned[p]:
                d[t.domain] = d.get(t.domain, 0) + 1
            if any(v >= 3 for v in d.values()):
                return p
        return None

    def return_empty_owned_territories(self) -> None:
        changed = True
        while changed:
            changed = False
            for p in self.players:
                for t in list(self.owned[p]):
                    if not t.guards:
                        self.owned[p].remove(t)
                        t.owner = None
                        self.territory_deck.append(t)
                        self.rng.shuffle(self.territory_deck)
                        self.territory_returns += 1
                        changed = True
            self.refill_center()

    def place_guard(self, player: int, territory: Territory, card: Card) -> None:
        if territory.owner is None:
            if territory in self.center:
                self.center.remove(territory)
            territory.owner = player
            self.owned[player].append(territory)
            self.refill_center()
        territory.guards.append(card)
        card.owner = player
        self.resolve_enter_skill(player, card)
        self.return_empty_owned_territories()

    def resolve_enter_skill(self, player: int, card: Card) -> None:
        enemies = [p for p in self.players if p != player]
        enemy_ts = [t for p in enemies for t in self.owned[p]]
        if card.name == "有来有去":
            self.draw(player, 1); self.discard_lowest(player)
        elif card.name == "急如火":
            if enemies and self.rng.random() < 0.5:
                target = self.rng.choice(enemies); self.draw(player, 1); self.draw(target, 1)
        elif card.name == "快如风":
            if self.territory_deck: self.territory_deck.append(self.territory_deck.pop(0))
        elif card.name == "小钻风":
            if self.territory_deck and self.rng.random() < 0.5: self.territory_deck.append(self.territory_deck.pop(0))
        elif card.name == "精细鬼":
            if self.deck and self.rng.random() < 0.5: self.deck.append(self.deck.pop(0))
        elif card.name == "云里雾":
            self.rng.shuffle(self.territory_deck)
        elif card.name == "雾里云":
            self.rng.shuffle(self.deck)
        elif card.name == "兴烘掀":
            self.remove_one_guard(enemy_ts, star_eq=1, to_hand=False)
        elif card.name == "掀烘兴":
            self.remove_one_guard(enemy_ts, star_eq=1, to_hand=True)
        elif card.name == "银角大王":
            top = self.deck[:3]; self.deck = self.deck[3:]
            top.sort(key=lambda c: (c.star, card_priority(c.name)), reverse=True)
            self.deck = top + self.deck
        elif card.name == "金角大王":
            if self.territory_deck and self.rng.random() < 0.5: self.territory_deck.append(self.territory_deck.pop(0))
        elif card.name == "黄袍怪":
            self.remove_one_guard(enemy_ts, star_eq=1, to_hand=True, new_owner=player)
        elif card.name == "红孩儿":
            cands = [t for t in enemy_ts if any(g.star in (1, 2) for g in t.guards)]
            if cands:
                t = max(cands, key=lambda x: sum(1 for g in x.guards if g.star in (1, 2)))
                for g in list(t.guards):
                    if g.star in (1, 2):
                        t.guards.remove(g); self.discard_or_return(g)
        elif card.name == "黄风怪":
            cands = [t for t in enemy_ts if any(g.star <= 3 for g in t.guards)]
            if cands:
                t = max(cands, key=lambda x: sum(1 for g in x.guards if g.star <= 3))
                for g in sorted([g for g in t.guards if g.star <= 3], key=lambda x: x.star, reverse=True)[:2]:
                    t.guards.remove(g)
                    if g.owner is not None: self.hands[g.owner].append(g)
        elif card.name == "青狮精":
            self.remove_one_guard(enemy_ts, star_le=4, to_hand=False, pick_high=True)
        elif card.name == "白象精":
            self.remove_one_guard(enemy_ts, star_le=4, to_hand=True, pick_high=True)
        elif card.name == "大鹏精":
            self.try_attack(player)

    def remove_one_guard(self, territories, star_eq=None, star_le=None, to_hand=False, new_owner=None, pick_high=False):
        cands = []
        for t in territories:
            for g in t.guards:
                if (star_eq is None or g.star == star_eq) and (star_le is None or g.star <= star_le):
                    cands.append((t, g))
        if not cands: return
        src, g = max(cands, key=lambda x: x[1].star) if pick_high else self.rng.choice(cands)
        src.guards.remove(g)
        if new_owner is not None:
            g.owner = new_owner
        if to_hand:
            owner = g.owner
            if owner is not None:
                self.hands[owner].append(g)
        else:
            self.discard_or_return(g)

    def discard_lowest(self, player: int) -> None:
        if self.hands[player]:
            c = min(self.hands[player], key=lambda x: (x.star, card_priority(x.name)))
            self.hands[player].remove(c); self.discard.append(c)

    def discard_or_return(self, card: Card) -> None:
        if card.name == "白骨精":
            card.owner = None; self.deck.append(card); self.rng.shuffle(self.deck)
        else:
            self.discard.append(card)

    def best_monster_in_hand(self, p): 
        cs=[c for c in self.hands[p] if c.kind=="妖怪"]
        return max(cs, key=lambda c:(c.star, card_priority(c.name))) if cs else None

    def best_treasure_in_hand(self, p):
        cs=[c for c in self.hands[p] if c.kind=="法宝"]
        return max(cs, key=lambda c:card_priority(c.name)) if cs else None

    def best_place_for_guard(self, p):
        cands=[t for t in self.owned[p] if len(t.guards)<3] + list(self.center)
        return max(cands, key=lambda t:domain_need_score(p,t,self.owned)) if cands else None

    def use_treasure(self, p, c):
        enemy_ts=[t for q in self.players if q!=p for t in self.owned[q]]
        if c.name=="辟火罩" and self.owned[p]:
            self.protected[p]=True; self.hands[p].remove(c); self.discard.append(c); return True
        if c.name=="金刚琢":
            return False
        if c.name in ("幌金绳","紫金红葫芦") and enemy_ts:
            cands=[(t,g) for t in enemy_ts for g in t.guards]
            if cands:
                src,g=max(cands,key=lambda x:x[1].star)
                src.guards.remove(g); g.owner=p; self.hands[p].append(g)
                self.hands[p].remove(c); self.discard.append(c); self.return_empty_owned_territories(); return True
        return False

    def recruit_best(self, p):
        m=self.best_monster_in_hand(p); t=self.best_place_for_guard(p)
        if m and t:
            self.hands[p].remove(m); self.place_guard(p,t,m); return True
        return False

    def should_recruit_before_attack(self, p):
        ts=self.owned[p]
        if not ts: return True
        if sum(len(t.guards) for t in ts) <= len(ts): return True
        d={}
        for t in ts: d[t.domain]=d.get(t.domain,0)+1
        return any(v>=2 for v in d.values()) and any(len(t.guards)<2 for t in ts)

    def attack_score(self,p,src,dst,attackers,survivors):
        own_same=sum(1 for t in self.owned[p] if t.domain==dst.domain)
        block=False
        if dst.owner is not None and dst.owner != p:
            block=sum(1 for t in self.owned[dst.owner] if t.domain==dst.domain)>=2
        source_empty=len(src.guards)==len(attackers)
        score=own_same*30+sum(g.star for g in dst.guards)*3+len(survivors)*6-sum(g.star for g in attackers)*2
        if own_same>=2: score+=120
        if block: score+=80
        if source_empty: score-=45
        if source_empty and (own_same>=2 or block): score+=35
        if dst.domain not in [t.domain for t in self.owned[p]]: score-=12
        return score

    def try_attack(self,p):
        own=[t for t in self.owned[p] if t.guards]
        targets=[t for q in self.players if q!=p and not self.protected.get(q,False) for t in self.owned[q] if t.guards]
        best=None
        for src in own:
            for r in range(1,min(3,len(src.guards))+1):
                for atk in itertools.combinations(list(src.guards),r):
                    for dst in targets:
                        ok,surv,dead=battle_outcome(list(atk),list(dst.guards))
                        if ok and surv:
                            score=(domain_need_score(p,dst,self.owned)*10+sum(g.star for g in dst.guards)-sum(g.star for g in atk)) if self.ai=="aggressive" else self.attack_score(p,src,dst,list(atk),surv)
                            if best is None or score>best[0]: best=(score,src,dst,list(atk),surv,dead)
        if best is None: return False
        score,src,dst,atk,surv,dead=best
        if self.ai=="human_like" and score<30: return False
        for g in atk:
            if g in src.guards: src.guards.remove(g)
        for g in list(dst.guards): dst.guards.remove(g); self.discard_or_return(g)
        for g in dead:
            if g in surv: surv.remove(g)
            self.discard_or_return(g)
        old=dst.owner
        if old is not None and dst in self.owned[old]: self.owned[old].remove(dst)
        dst.owner=p; dst.guards=surv[:3]
        for g in dst.guards: g.owner=p
        self.owned[p].append(dst); self.successful_attacks+=1; self.return_empty_owned_territories(); return True

    def take_turn(self):
        p=self.turn_index % len(self.players); self.turn_index+=1; self.turns+=1
        self.protected[p]=False
        before=self.snapshot_progress()
        self.draw(p,1); acted=False
        if self.ai=="aggressive":
            acted=self.try_attack(p)
            if not acted:
                tr=self.best_treasure_in_hand(p)
                if tr and card_priority(tr.name)>=80: acted=self.use_treasure(p,tr)
            if not acted: acted=self.recruit_best(p)
        else:
            if self.should_recruit_before_attack(p): acted=self.recruit_best(p)
            if not acted: acted=self.try_attack(p)
            if not acted:
                tr=self.best_treasure_in_hand(p)
                if tr and card_priority(tr.name)>=80: acted=self.use_treasure(p,tr)
            if not acted: acted=self.recruit_best(p)
        w=self.check_winner()
        if w is not None: return GameResult(w,"同妖域3地盘",self.turns,len(self.deck),self.deck_empty_once,self.territory_returns,self.successful_attacks,False)
        if not self.deck:
            after=self.snapshot_progress()
            self.no_progress_round = self.no_progress_round+1 if after==before else 0
            if self.no_progress_round >= len(self.players):
                w=self.settlement_winner()
                return GameResult(w,"公共牌库耗尽结算" if w is not None else "平局结算",self.turns,len(self.deck),True,self.territory_returns,self.successful_attacks,True)
        if self.turns>=200: return GameResult(None,"超时",self.turns,len(self.deck),self.deck_empty_once,self.territory_returns,self.successful_attacks,False)
        return None

    def snapshot_progress(self):
        return tuple((p,tuple(sorted((t.name,tuple(g.name for g in t.guards)) for t in self.owned[p]))) for p in self.players)

    def settlement_winner(self):
        scores=[]
        for p in self.players:
            ts=self.owned[p]
            domain_max=max([sum(1 for t in ts if t.domain==d) for d in self.available_domains] or [0])
            scores.append((len(ts),sum(g.star for t in ts for g in t.guards),domain_max,sum(len(t.guards) for t in ts),p))
        scores.sort(reverse=True)
        return None if len(scores)>1 and scores[0][:4]==scores[1][:4] else scores[0][4]

def battle_outcome(attackers, defenders):
    hp={id(g):g.star for g in defenders}; live_def=list(defenders); live_atk=list(attackers); dead=[]
    for atk in sorted(attackers,key=lambda g:(g.star,card_priority(g.name))):
        if not live_def: break
        target=max(live_def,key=lambda g:g.star); hp[id(target)]-=atk.star
        if atk.star <= target.star:
            if atk in live_atk: live_atk.remove(atk)
            dead.append(atk)
        if hp[id(target)]<=0: live_def.remove(target)
    return len(live_def)==0 and len(live_atk)>0, live_atk, dead

def build_public_deck(preset):
    old={
        "小钻风":("妖怪",1,4),"有来有去":("妖怪",1,4),"精细鬼":("妖怪",1,4),"伶俐虫":("妖怪",1,4),"急如火":("妖怪",1,4),"快如风":("妖怪",1,4),
        "云里雾":("妖怪",2,4),"雾里云":("妖怪",2,4),
        "金角大王":("妖怪",3,2),"银角大王":("妖怪",3,2),"白骨精":("妖怪",3,2),"玉面狐狸":("妖怪",3,2),"金鼻白毛老鼠精":("妖怪",3,2),"黄袍怪":("妖怪",3,2),"铁扇公主":("妖怪",3,2),
        "红孩儿":("妖怪",4,2),"黄风怪":("妖怪",4,2),"青狮精":("妖怪",4,2),"牛魔王":("妖怪",5,1),"大鹏精":("妖怪",5,1),
        "紫金红葫芦":("法宝",0,1),"金刚琢":("法宝",0,1),"幌金绳":("法宝",0,1),"芭蕉扇":("法宝",0,1)}
    v13={
        "小钻风":("妖怪",1,2),"有来有去":("妖怪",1,2),"精细鬼":("妖怪",1,2),"伶俐虫":("妖怪",1,2),"急如火":("妖怪",1,2),"快如风":("妖怪",1,2),
        "云里雾":("妖怪",2,2),"雾里云":("妖怪",2,2),"兴烘掀":("妖怪",2,2),"掀烘兴":("妖怪",2,2),
        "金角大王":("妖怪",3,2),"银角大王":("妖怪",3,2),"白骨精":("妖怪",3,2),"黄袍怪":("妖怪",3,2),
        "黄风怪":("妖怪",4,2),"青狮精":("妖怪",4,2),"白象精":("妖怪",4,2),"红孩儿":("妖怪",5,1),"大鹏精":("妖怪",5,1),
        "紫金红葫芦":("法宝",0,1),"金刚琢":("法宝",0,1),"幌金绳":("法宝",0,1),"辟火罩":("法宝",0,1)}
    if preset=="current_58": counts=old
    elif preset=="reduced_42":
        counts=dict(old)
        for n,(k,s,c) in list(counts.items()):
            if k=="妖怪" and s in (1,2): counts[n]=(k,s,2)
    elif preset=="v13_table_003_40": counts=v13
    else: raise ValueError(f"未知preset: {preset}")
    deck=[]; uid=0
    for n,(k,s,c) in counts.items():
        for _ in range(c): deck.append(Card(n,k,s,uid=uid)); uid+=1
    return deck

def build_territory_deck(domains): return [Territory(d,n) for d in domains for n in DOMAINS[d]]

def card_priority(name):
    return {"幌金绳":92,"金刚琢":88,"大鹏精":86,"红孩儿":86,"辟火罩":82,"青狮精":78,"黄风怪":76,"白象精":70,"牛魔王":68,"铁扇公主":64,"金角大王":60,"金鼻白毛老鼠精":60,"黄袍怪":55,"紫金红葫芦":45,"银角大王":42,"玉面狐狸":42,"云里雾":38,"雾里云":36,"兴烘掀":34,"掀烘兴":32,"小钻风":30,"有来有去":28,"精细鬼":28,"伶俐虫":26,"快如风":26,"急如火":18,"芭蕉扇":100}.get(name,0)

def domain_need_score(player, territory, owned):
    return sum(1 for t in owned[player] if t.domain==territory.domain)*10 + (3-len(territory.guards))

def run_batch(preset, ai, players_count, domain_count, center_size, games, seed):
    rs=[]
    for i in range(games):
        g=Game(preset,ai,players_count,domain_count,center_size,seed+i); r=None
        while r is None: r=g.take_turn()
        rs.append(r)
    reasons={}
    for r in rs: reasons[r.reason]=reasons.get(r.reason,0)+1
    turns=[r.turns for r in rs]; returns=[r.territory_returns for r in rs]; attacks=[r.successful_attacks for r in rs]; deck_left=[r.deck_left for r in rs]
    direct=reasons.get("同妖域3地盘",0); settle=reasons.get("公共牌库耗尽结算",0); draw=reasons.get("平局结算",0); timeout=reasons.get("超时",0)
    return {"preset":preset,"ai":ai,"players":players_count,"domain_count":domain_count,"center_size":center_size,"games":games,"seed":seed,"reasons":reasons,"direct_wins":direct,"settlement_wins":settle,"settlement_draws":draw,"timeouts":timeout,"avg_turns":round(mean(turns),2),"avg_rounds":round(mean(turns)/players_count,2),"median_turns":median(turns),"p90_turns":sorted(turns)[int(games*0.9)-1],"avg_deck_left":round(mean(deck_left),2),"deck_empty_games":sum(1 for r in rs if r.deck_empty),"deck_empty_rate":round(sum(1 for r in rs if r.deck_empty)/games,4),"settlement_rate":round((settle+draw)/games,4),"avg_territory_returns":round(mean(returns),2),"avg_successful_attacks":round(mean(attacks),2)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--players",type=int,choices=[2,3,4],default=4)
    p.add_argument("--domain-count",type=int,choices=[2,3,4],default=4)
    p.add_argument("--center-size",type=int,choices=[2,3],default=3)
    p.add_argument("--preset",choices=["current_58","reduced_42","v13_table_003_40"],default="v13_table_003_40")
    p.add_argument("--ai",choices=["aggressive","human_like"],default="human_like")
    p.add_argument("--games",type=int,default=3000)
    p.add_argument("--seed",type=int,default=20260706)
    p.add_argument("--json",action="store_true")
    a=p.parse_args()
    s=run_batch(a.preset,a.ai,a.players,a.domain_count,a.center_size,a.games,a.seed)
    print(json.dumps(s,ensure_ascii=False,indent=2) if a.json else "\n".join(f"{k}: {v}" for k,v in s.items()))
if __name__=="__main__": main()
