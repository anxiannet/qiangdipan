import { Breadcrumbs, ContinueReadingBlock, EntryGrid, InfoSection, PageHero, PageMain, RelatedPagesBlock, SiteFooter, SiteHeader } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function DevlogPage() {
  return (
    <>
      <SiteHeader />
      <PageMain>
        <Breadcrumbs items={[corePages.devlog]} />
        <PageHero eyebrow="DevlogHero" title="开发记录" actions={links("simulationResults", "roadmap", "websiteDevlog")}>
          <p>开发记录用于呈现规则、美术、印刷、测试和网站进展，不做文件浏览器，也不作为集中资料入口。</p>
        </PageHero>
        <InfoSection title="筛选" eyebrow="DevlogFilterBar">
          <div className="filter-bar">
            <span>测试</span>
            <span>规则</span>
            <span>美术</span>
            <span>印刷</span>
            <span>网站</span>
          </div>
        </InfoSection>
        <InfoSection title="记录列表" eyebrow="DevlogList">
          <EntryGrid items={links("simulationResults", "roadmap", "websiteDevlog", "ruleHistory", "illustrationHistory", "print")} />
        </InfoSection>
        <RelatedPagesBlock items={links("simulationResults", "roadmap", "websiteDevlog", "print", "art")} />
        <ContinueReadingBlock items={links("cards", "rules", "crowdfunding")} />
      </PageMain>
      <SiteFooter />
    </>
  );
}
