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
        <PageHero eyebrow="AI Simulation Report" title="标准版与《火云再起》正式模拟结果" actions={links("baseRules", "cards")}>
          <p>
            使用 human_like 正式平衡模型，对标准版与“标准版 + 火云再起”进行2人、3人、4人各3000局测试，共18000局。
            当前结果用于发现规则收束、局时与扩展牌互动风险，不替代真人实体试玩。
          </p>
        </PageHero>

        <InfoSection title="测试口径" eyebrow="Test Scope">
          <div className="entry-grid">
            <div className="entry-card"><strong>规则版本</strong><span>V1.3</span></div>
            <div className="entry-card"><strong>卡表版本</strong><span>V1.3-卡表-030</span></div>
            <div className="entry-card"><strong>正式样本</strong><span>18000局</span></div>
            <div className="entry-card"><strong>随机种子</strong><span>20260713</span></div>
          </div>
        </InfoSection>

        <InfoSection title="总体对比" eyebrow="Main Comparison">
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
            《火云再起》通过当前AI模拟层面的初步平衡审核。暂不修改卡牌数量或核心技能，下一阶段重点通过实体试玩观察2人局震荡、芭蕉扇的挫败感，以及1星抽牌卡在后期牌库耗尽时的实际体验。
          </p>
          <p>AI模拟结果只作为风险筛查和回归依据，不能替代真人的策略、沟通、喊名互动和主观体验。</p>
        </InfoSection>

        <RelatedPagesBlock items={links("devlog", "playtestFeedback", "ruleHistory", "cards")} />
        <ContinueReadingBlock items={links("baseRules", "skills", "crowdfunding")} />
      </PageMain>
      <SiteFooter />
    </>
  );
}
