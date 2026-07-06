import Image from "next/image";
import { notFound } from "next/navigation";
import { Breadcrumbs, ContinueReadingBlock, InfoSection, PageHero, PageMain, RelatedPagesBlock, StatusPanel, SiteFooter, SiteHeader } from "@/components/site/SiteChrome";
import { corePages, getCardById, getCards, getRelatedCards, links } from "@/lib/source-data";

export function generateStaticParams() {
  return getCards().map((card) => ({ id: card.id }));
}

export default async function CardCodexPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const card = getCardById(id);
  if (!card) {
    notFound();
  }

  return (
    <>
      <SiteHeader />
      <PageMain>
        <Breadcrumbs items={[corePages.cards, { href: `/cards/${card.id}`, label: card.name }]} />
        <PageHero eyebrow="CardCodexHero" title={card.name}>
          <p>单卡卡志第一阶段先建立页面结构。基础身份来自 V1.2 基础卡表，扩展背景后续只从对应妖怪志或法宝志读取。</p>
        </PageHero>
        <section className="codex-layout">
          <InfoSection title="卡牌身份" eyebrow="CardIdentityPanel">
            <dl className="identity-list">
              <div><dt>类型</dt><dd>{card.type}</dd></div>
              <div><dt>星级</dt><dd>{card.stars}</dd></div>
              <div><dt>基础版数量</dt><dd>{card.count}</dd></div>
              <div><dt>技能评级</dt><dd>{card.rating ?? "随源文件补充"}</dd></div>
            </dl>
          </InfoSection>
          <InfoSection title="卡图" eyebrow="CardImagePanel">
            {card.image ? <Image src={card.image} alt={card.name} width={300} height={420} /> : <div className="card-image-empty large">{card.name}</div>}
          </InfoSection>
        </section>
        <StatusPanel
          parent={corePages.cards}
          status="当前页面用于承接单卡卡志，第一阶段先展示基础身份、印刷卡图和关系入口。"
          purpose="后续在对应单卡志存在时，补充来源背景、形象设计、技能设计和玩法定位。"
        />
        <InfoSection title="来源背景" eyebrow="SourceBackgroundSection"><p>扩展背景将在对应单卡志存在时读取，不在页面中临时编写。</p></InfoSection>
        <InfoSection title="形象设计" eyebrow="ImageDesignSection"><p>插画与定稿说明后续从单卡志和美术迭代记录进入。</p></InfoSection>
        <InfoSection title="技能设计" eyebrow="SkillDesignSection"><p>{card.skill}</p></InfoSection>
        <InfoSection title="玩法定位" eyebrow="GameplayRoleSection"><p>当前仅建立玩法定位区，后续随试玩反馈补充。</p></InfoSection>
        <RelatedPagesBlock items={[...links("cardHistory", "skills", "skillRating", "illustrationHistory"), ...getRelatedCards(card)]} />
        <ContinueReadingBlock items={links("cards", "baseRules", "print")} />
      </PageMain>
      <SiteFooter />
    </>
  );
}
