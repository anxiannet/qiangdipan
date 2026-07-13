import Image from "next/image";
import { PageMain, SiteFooter, SiteHeader } from "@/components/site/SiteChrome";
import { getPrintFiles } from "@/lib/source-data";

const heroBadges = ["2~4人", "15~30分钟", "轻策略", "欢乐互动"];

const playSteps = [
  {
    title: "派妖怪",
    copy: "从手牌中打出妖怪，让小妖、头目和妖王加入你的势力。"
  },
  {
    title: "抢地盘",
    copy: "选择目标地盘，派妖怪挑战守军。战斗后，胜出的妖怪将为你驻守地盘。"
  },
  {
    title: "成妖王",
    copy: "控制同一妖域 3 块地盘，立即成为新的万妖之王。"
  }
];

const boxContents = [
  { title: "妖怪牌", count: "54张", kind: "monster" },
  { title: "法宝牌", count: "4张", kind: "treasure" },
  { title: "地盘牌", count: "12张", kind: "territory" },
  { title: "指南卡", count: "2张", kind: "guide" }
];

const progressItems = [
  { title: "规则 V1.3 已整理", status: "已完成", tone: "done" },
  { title: "标准版与火云再起18000局模拟", status: "已完成", tone: "done" },
  { title: "第一版印刷文件已准备", status: "已完成", tone: "done" },
  { title: "包装盒测试推进中", status: "进行中", tone: "doing" },
  { title: "网站已部署", status: "已完成", tone: "done" },
  { title: "实体试玩准备中", status: "进行中", tone: "doing" }
];

export default function HomePage() {
  const printFiles = getPrintFiles();
  const boxFront = printFiles.find((file) => file.type === "box" && file.name.includes("正面")) ?? printFiles.find((file) => file.type === "box");
  const boxSide = printFiles.find((file) => file.type === "box" && file.name.includes("右侧")) ?? printFiles.find((file) => file.type === "box" && file.public_path !== boxFront?.public_path);
  const monsterCards = printFiles.filter((file) => file.type === "card" && file.category === "monster").slice(0, 5);
  const territoryCard = printFiles.find((file) => file.type === "card" && file.category === "territory");
  const treasureCard = printFiles.find((file) => file.type === "card" && file.category === "treasure");
  const cardBack = printFiles.find((file) => file.type === "card" && file.category === "back");
  const heroCards = monsterCards.slice(0, 4);
  const printCards = [...monsterCards.slice(0, 4), territoryCard].filter(Boolean);
  const thumbAssets = [boxFront, boxSide, cardBack, territoryCard].filter(Boolean);

  const imageForKind = (kind: string) => {
    if (kind === "monster") return monsterCards[0];
    if (kind === "treasure") return treasureCard;
    if (kind === "territory") return territoryCard;
    return cardBack;
  };

  return (
    <>
      <SiteHeader />
      <PageMain className="home-page">
        <section className="home-hero qdp-frame" aria-labelledby="home-hero-title">
          <div className="hero-scenery" aria-hidden="true">
            <span className="hero-flag hero-flag-a" />
            <span className="hero-flag hero-flag-b" />
            <span className="hero-gate" />
          </div>
          <div className="hero-text">
            <p className="hero-kicker">实体印刷优先 · 2~4人 · 15~30分钟</p>
            <h1 id="home-hero-title">妖怪集结，开抢地盘</h1>
            <p>西游妖怪题材欢乐聚会卡牌游戏。派妖怪、放法宝、抢地盘，控制同一妖域 3 块地盘，立即获胜。</p>
            <div className="hero-badges" aria-label="游戏卖点">
              {heroBadges.map((badge) => (
                <span key={badge}>{badge}</span>
              ))}
            </div>
            <div className="hero-actions">
              <a className="qdp-button qdp-button-primary" href="#print">
                查看印刷成果
              </a>
              <a className="qdp-button qdp-button-secondary" href="#how-to-play">
                了解怎么玩
              </a>
            </div>
          </div>
          <div className="hero-card-fan" aria-label="第一版印刷卡牌展示">
            {heroCards.map((file) => (
              <Image key={file.public_path} src={file.public_path} width={260} height={364} alt={file.name} priority />
            ))}
          </div>
        </section>

        <section id="print" className="home-print-section qdp-frame home-section" aria-labelledby="print-title">
          <h2 id="print-title" className="qdp-section-title">
            第一版印刷成果
          </h2>
          <div className="print-product-stage">
            <div className="print-box-display">
              {boxSide ? <Image className="print-box-side" src={boxSide.public_path} width={220} height={308} alt={boxSide.name} /> : null}
              {boxFront ? <Image className="print-box-main" src={boxFront.public_path} width={360} height={504} alt={boxFront.name} /> : null}
            </div>
            <div className="print-feature-list" aria-label="印刷展示重点">
              <span>色彩鲜明，细节清晰</span>
              <span>卡牌手感扎实，耐玩耐用</span>
              <span>美术统一，角色灵动可爱</span>
            </div>
            <div className="print-card-fan" aria-label="卡牌扇形展示">
              {printCards.map((file) => (
                <Image key={file!.public_path} src={file!.public_path} width={180} height={252} alt={file!.name} />
              ))}
            </div>
          </div>
          <div className="print-thumbs" aria-label="印刷资源缩略图">
            {thumbAssets.map((file) => (
              <Image key={file!.public_path} src={file!.public_path} width={180} height={126} alt={file!.name} />
            ))}
          </div>
        </section>

        <section id="how-to-play" className="home-play-section qdp-frame home-section" aria-labelledby="play-title">
          <h2 id="play-title" className="qdp-section-title">
            怎么玩
          </h2>
          <div className="play-step-grid">
            {playSteps.map((step, index) => (
              <article key={step.title} className="play-step-card">
                <span className="step-number">{index + 1}</span>
                <div>
                  <h3>{step.title}</h3>
                  <p>{step.copy}</p>
                </div>
                {index < playSteps.length - 1 ? <span className="step-arrow" aria-hidden="true" /> : null}
              </article>
            ))}
          </div>
        </section>

        <section className="home-box-section qdp-frame home-section" aria-labelledby="box-title">
          <h2 id="box-title" className="qdp-section-title">
            一盒里有什么
          </h2>
          <div className="box-content-grid">
            {boxContents.map((item) => {
              const asset = imageForKind(item.kind);
              return (
                <article key={item.title} className={`box-content-card box-content-${item.kind}`}>
                  {asset ? <Image src={asset.public_path} width={118} height={165} alt={asset.name} /> : <span className="box-card-back" />}
                  <div>
                    <strong>{item.title}</strong>
                    <span>{item.count}</span>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <section className="home-progress-section qdp-frame home-section" aria-labelledby="progress-title">
          <h2 id="progress-title" className="qdp-section-title">
            当前进度
          </h2>
          <div className="progress-layout">
            <div className="progress-list">
              {progressItems.map((item, index) => (
                <div key={item.title} className="progress-row">
                  <span className={`progress-icon progress-${item.tone}`}>{index + 1}</span>
                  <strong>{item.title}</strong>
                  <span className={`progress-status progress-${item.tone}`}>{item.status}</span>
                </div>
              ))}
            </div>
            <div className="progress-visual" aria-hidden="true">
              <span className="progress-mountain" />
              <span className="progress-banner">妖</span>
            </div>
          </div>
        </section>

        <section id="playtest" className="home-playtest-section qdp-frame home-section" aria-labelledby="playtest-title">
          <span className="cta-creature cta-creature-left" aria-hidden="true" />
          <span className="cta-creature cta-creature-right" aria-hidden="true" />
          <h2 id="playtest-title" className="qdp-section-title">
            想先看看测试结果？
          </h2>
          <div className="playtest-actions">
            <a className="qdp-button qdp-button-primary" href="/devlog/simulation-results">
              查看18000局模拟结果
            </a>
            <a className="qdp-button qdp-button-secondary" href="/crowdfunding/playtest-feedback">
              关注实体试玩反馈
            </a>
          </div>
        </section>
      </PageMain>
      <SiteFooter />
    </>
  );
}
