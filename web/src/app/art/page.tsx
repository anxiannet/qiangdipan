import { Breadcrumbs, ContinueReadingBlock, EntryGrid, InfoSection, PageHero, PageMain, RelatedPagesBlock, SiteFooter, SiteHeader } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function ArtPage() {
  return (
    <>
      <SiteHeader />
      <PageMain>
        <Breadcrumbs items={[corePages.art]} />
        <PageHero eyebrow="ArtHero" title="美术档案" actions={links("visualSpec", "illustrationHistory")}>
          <p>美术档案用于承接蓝金西游妖怪桌游风、非 Q 版东方神话动画电影感和插画迭代记录。</p>
        </PageHero>
        <InfoSection title="视觉与流程" eyebrow="VisualSpecEntry / UiSpecEntry / IllustrationFlowEntry / FinalReviewEntry">
          <EntryGrid items={links("visualSpec", "uiSpec", "illustrationReviewFlow", "cardFinalReviewFlow", "illustrationHistory")} />
        </InfoSection>
        <InfoSection title="关联卡牌" eyebrow="RelatedCardsEntry">
          <EntryGrid items={links("cards", "cardHistory", "print")} />
        </InfoSection>
        <RelatedPagesBlock items={links("visualSpec", "illustrationReviewFlow", "illustrationHistory", "cardFinalReviewFlow", "cards")} />
        <ContinueReadingBlock items={links("cards", "print", "devlog")} />
      </PageMain>
      <SiteFooter />
    </>
  );
}
