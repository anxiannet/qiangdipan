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

const comparisonRows = [
  { players: "2人", deck: "标准版", direct: "2885", settlement: "53", draws: "19", timeouts: "43", turns: "26.57" },
  { players: "2人", deck: "标准版 + 火云再起", direct: "2847", settlement: "87", draws: "11", timeouts: "55", turns: "29.77" },
  { players: "3人", deck: "标准版", direct: "2916", settlement: "26", draws: "29", timeouts: "29", turns: "23.91" },
  { players: "3人", deck: "标准版 + 火云再起", direct: "2943", settlement: "27", draws: "13", timeouts: "17", turns: "24.45" },
  { players: "4人", deck: "标准版", direct: "2906", settlement: "47", draws: "33", timeouts: "14", turns: "24.51" },
  { players: "4人", deck: "标准版 + 火云再起", direct: "2939", settlement: "22", draws: "21", timeouts: "18", turns: "25.49" }
];

const duelRows = [
  { deck: "标准版40张", territories: "6", center: "2", direct: "100.00%", timeout: "0.00%", turns: "9.36", median: "7", p90: "18", empty: "0.80%", attacks: "1.31", returns: "1.50" },
  { deck: "标准版40张", territories: "9", center: "2", direct: "98.37%", timeout: "0.73%", turns: "20.94", median: "17", p90: "38", empty: "18.13%", attacks: "4.23", returns: "3.74" },
  { deck: "标准版40张", territories: "12", center: "3", direct: "96.17%", timeout: "1.43%", turns: "26.57", median: "21", p90: "50", empty: "29.70%", attacks: "5.85", returns: "4.94" },
  { deck: "火云再起50张", territories: "6", center: "2", direct: "99.90%", timeout: "0.10%", turns: "10.70", median: "8", p90: "20", empty: "0.67%", attacks: "1.29", returns: "2.82" },
  { deck: "火云再起50张", territories: "9", center: "2", direct: "97.37%", timeout: "1.00%", turns: "23.30", median: "18", p90: "44", empty: "12.83%", attacks: "4.48", returns: "5.74" },
  { deck: "火云再起50张", territories: "12", center: "3", direct: "94.90%", timeout: "1.83%", turns: "29.77", median: "23", p90: "55", empty: "23.53%", attacks: "6.18", returns: "7.17" }
];

const deckRows = [
  { players: "2人", standard: "29.70%", expansion: "23.53%", returns: "4.94 → 7.17" },
  { players: "3人", standard: "30.97%", expansion: "20.57%", returns: "4.94 → 6.28" },
  { players: "4人", standard: "41.67%", expansion: "28.40%", returns: "5.49 → 6.84" }
];

const cardRows = [
  { name: "云里雾 / 雾里云", result: "抽牌触发率随人数增加而下降", detail: "2人约24%~26%，3人约15%，4人约11%" },
  { name: "兴烘掀 / 掀烘兴", result: "多人局几乎稳定触发", detail: "2人约91%~94%，3人约98%，4人约99%" },
  { name: "玉面狐狸", result: "人数越多，牛魔王在场条件越容易满足", detail: "触发率30.07% / 34.87% / 41.20%" },
  { name: "铁扇公主", result: "触发稳定，未出现明显超模", detail: "触发率约92%~93%，每次约吹回0.92个守军" },
  { name: "红孩儿", result: "存在轻微正向胜率关联，仍需实体试玩验证", detail: "触发率15.49% / 18.84% / 22.17%" },
  { name: "芭蕉扇", result: "单次桌面影响最大，但没有出现抽到即赢", detail: "每次平均吹回2.04 / 1.66 / 1.41个守军" }
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

export default function SimulationResultsPage() {
  return (
    <>
      <SiteHeader />
      <PageMain>
        <Breadcrumbs items={[corePages.devlog, corePages.simulationResults]} />
        <PageHero eyebrow="AI Simulation Report" title="AI模拟测试结果" actions={links("baseRules", "duelRules", "cards")}>
          <p>
            当前公开结果包括标准版与“标准版 + 火云再起”2至4人正式测试18000局，以及双人6块、9块地盘专项测试12000局。
            AI模拟用于发现规则收束、局时与互动风险，不替代真人实体试玩。
          </p>
        </PageHero>

        <InfoSection title="测试口径" eyebrow="Test Scope">
          <div className="entry-grid">
            <div className="entry-card"><strong>规则版本</strong><span>V1.3</span></div>
            <div className="entry-card"><strong>卡表版本</strong><span>V1.3-卡表-030</span></div>
            <div className="entry-card"><strong>公开正式样本</strong><span>30000局</span></div>
            <div className="entry-card"><strong>AI模型</strong><span>human_like</span></div>
          </div>
        </InfoSection>

        <InfoSection title="2至4人牌组对比：18000局" eyebrow="Main Comparison">
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 760 }}>
              <thead>
                <tr>
                  <th style={headStyle}>人数</th>
                  <th style={headStyle}>牌组</th>
                  <th style={headStyle}>直接胜利</th>
                  <th style={headStyle}>结算胜利</th>
                  <th style={headStyle}>平局</th>
                  <th style={headStyle}>超时</th>
                  <th style={headStyle}>平均回合</th>
                </tr>
              </thead>
              <tbody>
                {comparisonRows.map((row) => (
                  <tr key={`${row.players}-${row.deck}`}>
                    <td style={cellStyle}>{row.players}</td>
                    <td style={cellStyle}>{row.deck}</td>
                    <td style={cellStyle}>{row.direct}</td>
                    <td style={cellStyle}>{row.settlement}</td>
                    <td style={cellStyle}>{row.draws}</td>
                    <td style={cellStyle}>{row.timeouts}</td>
                    <td style={cellStyle}>{row.turns}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </InfoSection>

        <InfoSection title="双人6块、9块、12块地盘对比" eyebrow="Duel Territory Comparison">
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 1120 }}>
              <thead>
                <tr>
                  <th style={headStyle}>牌库</th>
                  <th style={headStyle}>地盘</th>
                  <th style={headStyle}>中央</th>
                  <th style={headStyle}>直接胜利率</th>
                  <th style={headStyle}>超时率</th>
                  <th style={headStyle}>平均回合</th>
                  <th style={headStyle}>中位回合</th>
                  <th style={headStyle}>P90</th>
                  <th style={headStyle}>牌库耗尽率</th>
                  <th style={headStyle}>成功攻击</th>
                  <th style={headStyle}>地盘回流</th>
                </tr>
              </thead>
              <tbody>
                {duelRows.map((row) => (
                  <tr key={`${row.deck}-${row.territories}`}>
                    <td style={cellStyle}>{row.deck}</td>
                    <td style={cellStyle}>{row.territories}</td>
                    <td style={cellStyle}>{row.center}</td>
                    <td style={cellStyle}>{row.direct}</td>
                    <td style={cellStyle}>{row.timeout}</td>
                    <td style={cellStyle}>{row.turns}</td>
                    <td style={cellStyle}>{row.median}</td>
                    <td style={cellStyle}>{row.p90}</td>
                    <td style={cellStyle}>{row.empty}</td>
                    <td style={cellStyle}>{row.attacks}</td>
                    <td style={cellStyle}>{row.returns}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p>
            双人默认推荐9块地盘、中央2块。6块适合快速教学；12块可作为完整长局。6块增加到9块带来显著更多互动，9块增加到12块则主要增加局时与牌库耗尽。
          </p>
        </InfoSection>

        <InfoSection title="牌库耗尽与地盘回流" eyebrow="Deck And Territory">
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 620 }}>
              <thead>
                <tr>
                  <th style={headStyle}>人数</th>
                  <th style={headStyle}>标准版牌库耗尽率</th>
                  <th style={headStyle}>火云再起牌库耗尽率</th>
                  <th style={headStyle}>平均地盘回流</th>
                </tr>
              </thead>
              <tbody>
                {deckRows.map((row) => (
                  <tr key={row.players}>
                    <td style={cellStyle}>{row.players}</td>
                    <td style={cellStyle}>{row.standard}</td>
                    <td style={cellStyle}>{row.expansion}</td>
                    <td style={cellStyle}>{row.returns}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p>扩展包将公共牌库从40张增加到50张，牌库耗尽率下降，但铁扇公主、红孩儿和芭蕉扇使地盘回流次数上升。</p>
        </InfoSection>

        <InfoSection title="扩展卡观察" eyebrow="Expansion Card Notes">
          <div className="entry-grid">
            {cardRows.map((card) => (
              <article key={card.name} className="entry-card">
                <strong>{card.name}</strong>
                <span>{card.result}</span>
                <span>{card.detail}</span>
              </article>
            ))}
          </div>
        </InfoSection>

        <InfoSection title="压力测试" eyebrow="Stress Attack">
          <p>
            4人《火云再起》stress_attack 100局中，62局达到200回合上限，平均回合158.81，平均地盘回流53.74次。
            该模型只用于检查高频抢地盘造成的极端震荡，不用于正常平衡结论。
          </p>
        </InfoSection>

        <InfoSection title="当前审核结论" eyebrow="Review Conclusion">
          <p>
            《火云再起》通过当前AI模拟层面的初步平衡审核。双人局默认推荐3个妖域、9块地盘、中央2块；6块保留为快速局，12块保留为完整长局。
          </p>
          <p>AI模拟结果只作为风险筛查和回归依据，不能替代真人的策略、沟通、喊名互动和主观体验。</p>
        </InfoSection>

        <RelatedPagesBlock items={links("duelRules", "devlog", "playtestFeedback", "ruleHistory", "cards")} />
        <ContinueReadingBlock items={links("baseRules", "skills", "crowdfunding")} />
      </PageMain>
      <SiteFooter />
    </>
  );
}
