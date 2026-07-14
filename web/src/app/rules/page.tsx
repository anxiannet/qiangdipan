import { Breadcrumbs, ContinueReadingBlock, EntryGrid, InfoSection, PageHero, PageMain, RelatedPagesBlock, SiteFooter, SiteHeader } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function RulesPage() {
  return (
    <>
      <SiteHeader />
      <PageMain>
        <Breadcrumbs items={[corePages.rules]} />
        <PageHero eyebrow="RulesHero" title="规则入口" actions={links("baseRules", "duelRules", "manual", "quickReference")}>
          <p>第一阶段建立规则阅读路径。核心胜利条件固定为：控制同一妖域 3 块地盘，立即获胜。</p>
        </PageHero>
        <InfoSection title="规则模块" eyebrow="RulesModeCards">
          <EntryGrid items={links("baseRules", "duelRules", "skills", "skillRating", "ruleHistory", "futureRules", "manual", "quickReference")} />
        </InfoSection>
        <InfoSection title="双人局推荐" eyebrow="DuelRecommendation">
          <div className="entry-grid">
            <div className="entry-card"><strong>快速局</strong><span>2个妖域，6块地盘，中央2块。</span></div>
            <div className="entry-card"><strong>标准局</strong><span>3个妖域，9块地盘，中央2块。当前默认推荐。</span></div>
            <div className="entry-card"><strong>完整局</strong><span>4个妖域，12块地盘，中央3块。</span></div>
          </div>
        </InfoSection>
        <InfoSection title="快速开始" eyebrow="RulesQuickStart">
          <div className="steps">
            <p>准备公共牌库、地盘牌库和玩家初始手牌。</p>
            <p>轮到你时打出妖怪或法宝，并选择是否发动抢地盘。</p>
            <p>抢地盘成功后，存活妖怪移动到目标地盘驻守。</p>
            <p>控制同一妖域 3 块地盘，立即获胜。</p>
          </div>
        </InfoSection>
        <InfoSection title="规则变化" eyebrow="RuleHistoryEntry">
          <EntryGrid items={links("ruleHistory", "futureRules", "simulationResults")} />
        </InfoSection>
        <RelatedPagesBlock items={links("cards", "play", "print", "devlog")} />
        <ContinueReadingBlock items={links("baseRules", "duelRules", "skills", "skillRating")} />
      </PageMain>
      <SiteFooter />
    </>
  );
}
