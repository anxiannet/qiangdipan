import {
  Breadcrumbs,
  ContinueReadingBlock,
  InfoSection,
  PageHero,
  PageMain,
  RelatedPagesBlock,
  SiteFooter,
  SiteHeader
} from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

const modes = [
  {
    title: "双人快速局",
    setup: "2个妖域 · 6块地盘 · 中央2块",
    use: "新手教学、展会试玩、10分钟左右快速体验",
    note: "收束最快，但路线选择和技能展开较少。"
  },
  {
    title: "双人标准局",
    setup: "3个妖域 · 9块地盘 · 中央2块",
    use: "常规双人对战、正式试玩、完整技能体验",
    note: "当前默认推荐，在局时、互动和长尾风险之间最均衡。"
  },
  {
    title: "双人完整局",
    setup: "4个妖域 · 12块地盘 · 中央3块",
    use: "完整基础规则体验、偏长双人局",
    note: "争夺最多，但牌库耗尽率和长尾回合也最高。"
  }
];

const rows = [
  { deck: "标准版40张", territories: "6", center: "2", direct: "100.00%", timeout: "0.00%", turns: "9.36", p90: "18", empty: "0.80%", attacks: "1.31" },
  { deck: "标准版40张", territories: "9", center: "2", direct: "98.37%", timeout: "0.73%", turns: "20.94", p90: "38", empty: "18.13%", attacks: "4.23" },
  { deck: "标准版40张", territories: "12", center: "3", direct: "96.17%", timeout: "1.43%", turns: "26.57", p90: "50", empty: "29.70%", attacks: "5.85" },
  { deck: "火云再起50张", territories: "6", center: "2", direct: "99.90%", timeout: "0.10%", turns: "10.70", p90: "20", empty: "0.67%", attacks: "1.29" },
  { deck: "火云再起50张", territories: "9", center: "2", direct: "97.37%", timeout: "1.00%", turns: "23.30", p90: "44", empty: "12.83%", attacks: "4.48" },
  { deck: "火云再起50张", territories: "12", center: "3", direct: "94.90%", timeout: "1.83%", turns: "29.77", p90: "55", empty: "23.53%", attacks: "6.18" }
];

const cellStyle = {
  padding: "12px 14px",
  borderBottom: "1px solid rgba(216, 166, 64, 0.28)",
  textAlign: "left" as const,
  whiteSpace: "nowrap" as const
};

const headStyle = {
  ...cellStyle,
  color: "var(--qdp-gold-300)",
  background: "rgba(58, 36, 20, 0.42)",
  fontWeight: 900
};

export default function DuelRulesPage() {
  return (
    <>
      <SiteHeader />
      <PageMain>
        <Breadcrumbs items={[corePages.rules, corePages.duelRules]} />
        <PageHero eyebrow="Duel Territory Rules" title="双人局地盘设置" actions={links("baseRules", "simulationResults")}>
          <p>
            双人局只调整使用的妖域数量、地盘总数和中央地盘数量。公共牌库、卡牌技能、战斗规则和胜利条件保持不变。
          </p>
        </PageHero>

        <InfoSection title="三种双人模式" eyebrow="Duel Modes">
          <div className="entry-grid">
            {modes.map((mode) => (
              <article key={mode.title} className="entry-card">
                <strong>{mode.title}</strong>
                <span>{mode.setup}</span>
                <span>{mode.use}</span>
                <span>{mode.note}</span>
              </article>
            ))}
          </div>
        </InfoSection>

        <InfoSection title="统一规则" eyebrow="Shared Rules">
          <div className="steps">
            <p>从4个妖域中随机选出本局使用的妖域，每个被选妖域使用全部3块地盘。</p>
            <p>中央地盘被占领后立即补充，尽量维持该模式规定的中央地盘数量。</p>
            <p>地盘牌库为空时不再补充。</p>
            <p>控制同一妖域全部3块地盘，立即获胜。</p>
          </div>
        </InfoSection>

        <InfoSection title="AI测试对比" eyebrow="Simulation Comparison">
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 900 }}>
              <thead>
                <tr>
                  <th style={headStyle}>牌库</th>
                  <th style={headStyle}>地盘</th>
                  <th style={headStyle}>中央</th>
                  <th style={headStyle}>直接胜利率</th>
                  <th style={headStyle}>超时率</th>
                  <th style={headStyle}>平均回合</th>
                  <th style={headStyle}>P90</th>
                  <th style={headStyle}>牌库耗尽率</th>
                  <th style={headStyle}>成功攻击</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={`${row.deck}-${row.territories}`}>
                    <td style={cellStyle}>{row.deck}</td>
                    <td style={cellStyle}>{row.territories}</td>
                    <td style={cellStyle}>{row.center}</td>
                    <td style={cellStyle}>{row.direct}</td>
                    <td style={cellStyle}>{row.timeout}</td>
                    <td style={cellStyle}>{row.turns}</td>
                    <td style={cellStyle}>{row.p90}</td>
                    <td style={cellStyle}>{row.empty}</td>
                    <td style={cellStyle}>{row.attacks}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </InfoSection>

        <InfoSection title="当前推荐" eyebrow="Recommendation">
          <p>
            默认双人规则推荐9块地盘。6块地盘保留为快速教学模式；12块地盘保留为完整长局模式。
            从6块增加到9块时，策略互动显著增加；从9块增加到12块时，主要增加的是局时、牌库耗尽和拉锯。
          </p>
        </InfoSection>

        <RelatedPagesBlock items={links("baseRules", "simulationResults", "playtestFeedback", "ruleHistory")} />
        <ContinueReadingBlock items={links("skills", "manual", "quickReference")} />
      </PageMain>
      <SiteFooter />
    </>
  );
}
