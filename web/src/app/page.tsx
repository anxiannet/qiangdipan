import Image from "next/image";
import { ContinueReadingBlock, EntryGrid, InfoSection, LinkRow, PageMain, SiteFooter, SiteHeader } from "@/components/site/SiteChrome";
import { corePages, getCards, getPrintFiles, links } from "@/lib/source-data";

export default function HomePage() {
  const cards = getCards();
  const showcase = getPrintFiles().filter((file) => file.type === "box" || file.category === "monster").slice(0, 5);

  return (
    <>
      <SiteHeader />
      <PageMain className="home-page">
        <section className="home-hero">
          <div className="hero-text">
            <p className="eyebrow">西游妖怪题材欢乐聚会卡牌游戏</p>
            <h1>夕妖：抢地盘</h1>
            <p>
              孙悟空被压五指山后，各路妖王争山头、占洞府。派妖怪、放法宝、抢地盘，控制同一妖域 3 块地盘，立即获胜。
            </p>
            <LinkRow items={links("cards", "baseRules", "play", "crowdfunding")} />
          </div>
          <div className="hero-card-fan" aria-label="第一版印刷卡牌展示">
            {showcase.slice(1, 4).map((file) => (
              <Image key={file.public_path} src={file.public_path} width={260} height={364} alt={file.name} />
            ))}
          </div>
        </section>

        <InfoSection title="为什么这局好玩" eyebrow="ValuePropsSection" className="home-value-section">
          <div className="feature-strip">
            <span>2~4 人</span>
            <span>15~30 分钟</span>
            <span>轻策略</span>
            <span>轻 TRPG 代入</span>
          </div>
        </InfoSection>

        <InfoSection title="印刷成果" eyebrow="PrintShowcaseSection" className="home-print-section">
          <div className="print-showcase">
            {showcase.map((file) => (
              <Image key={file.public_path} src={file.public_path} width={220} height={308} alt={file.name} />
            ))}
          </div>
        </InfoSection>

        <InfoSection title="怎么玩" eyebrow="HowToPlaySection" className="home-play-section">
          <div className="steps">
            <p>抽牌，打出妖怪或法宝。</p>
            <p>派妖怪向地盘发动抢地盘。</p>
            <p>守军被清空后占领地盘。</p>
            <p>控制同一妖域 3 块地盘，立即获胜。</p>
          </div>
        </InfoSection>

        <InfoSection title="基础盒内容" eyebrow="BoxContentsSection" className="home-box-section">
          <div className="stat-grid">
            <strong>{cards.filter((card) => card.category === "monster").length}<span>种妖怪</span></strong>
            <strong>{cards.filter((card) => card.category === "treasure").length}<span>件法宝</span></strong>
            <strong>{cards.filter((card) => card.category === "territory").length}<span>块地盘</span></strong>
          </div>
        </InfoSection>

        <InfoSection title="当前进度" eyebrow="ProgressSection" className="home-progress-section">
          <EntryGrid
            items={[
              { href: "/print", label: "第一版印刷资源已同步", description: "用于展示实体卡牌与包装样品。" },
              { href: "/devlog/roadmap", label: "实体测试版准备中", description: "先做小批量样品，再收集试玩反馈。" },
              { href: "/crowdfunding", label: "众筹预热", description: "当前只做意向收集与项目预热。" }
            ]}
          />
        </InfoSection>

        <InfoSection title="卡牌与规则入口" eyebrow="CardAndRuleEntrySection" className="home-card-rule-section">
          <EntryGrid items={links("cards", "cardHistory", "rules", "baseRules", "skills", "skillRating")} />
        </InfoSection>

        <InfoSection title="美术与开发记录" eyebrow="ArtAndDevlogEntrySection" className="home-art-devlog-section">
          <EntryGrid items={links("art", "illustrationHistory", "print", "devlog", "roadmap")} />
        </InfoSection>

        <InfoSection title="加入试玩关注" eyebrow="PlaytestCtaSection" className="home-playtest-section">
          <p>第一阶段先建立官网结构、印刷展示和试玩入口，后续随实物反馈补充玩家招募与测试记录。</p>
          <LinkRow items={links("play", "crowdfunding")} />
        </InfoSection>

        <InfoSection title="下一步去哪" eyebrow="FooterCtaSection" className="home-footer-cta-section">
          <ContinueReadingBlock items={[corePages.cards, corePages.baseRules, corePages.print]} />
        </InfoSection>
      </PageMain>
      <SiteFooter />
    </>
  );
}
