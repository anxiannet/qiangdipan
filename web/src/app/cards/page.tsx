import Image from "next/image";
import Link from "next/link";
import { Breadcrumbs, ContinueReadingBlock, EntryGrid, InfoSection, PageHero, PageMain, RelatedPagesBlock, SiteFooter, SiteHeader } from "@/components/site/SiteChrome";
import { corePages, getCards, links } from "@/lib/source-data";

export default function CardsPage() {
  const cards = getCards();

  return (
    <>
      <SiteHeader />
      <PageMain>
        <Breadcrumbs items={[corePages.cards]} />
        <PageHero eyebrow="CardsHero" title="卡牌图鉴" actions={links("cardHistory", "backupCards")}>
          <p>第一阶段建立卡册入口与筛选骨架，卡牌基础信息从 V1.2 基础卡表读取，卡图优先展示第一版印刷资源。</p>
        </PageHero>
        <InfoSection title="筛选" eyebrow="CardsFilterBar">
          <div className="filter-bar">
            <span>妖怪</span>
            <span>法宝</span>
            <span>地盘</span>
            <span>星级</span>
            <span>妖域</span>
          </div>
        </InfoSection>
        <InfoSection title="分类" eyebrow="CardsCategoryTabs">
          <div className="feature-strip">
            <span>妖怪卡</span>
            <span>法宝卡</span>
            <span>地盘卡</span>
            <span>指南卡</span>
          </div>
        </InfoSection>
        <InfoSection title="基础版卡册" eyebrow="CardsGrid">
          <div className="cards-grid">
            {cards.map((card) => (
              <Link key={card.name} href={`/cards/${card.id}`} className="codex-card">
                {card.image ? <Image src={card.image} alt={card.name} width={210} height={294} /> : <div className="card-image-empty">{card.name}</div>}
                <strong>{card.name}</strong>
                <span>{card.type} · {card.stars}星 · {card.count}张</span>
              </Link>
            ))}
          </div>
        </InfoSection>
        <InfoSection title="卡牌变化与备选" eyebrow="CardHistoryEntry / BackupCardsEntry">
          <EntryGrid items={links("cardHistory", "backupCards")} />
        </InfoSection>
        <RelatedPagesBlock items={links("baseRules", "skills", "skillRating", "print")} />
        <ContinueReadingBlock items={links("rules", "art", "play")} />
      </PageMain>
      <SiteFooter />
    </>
  );
}
