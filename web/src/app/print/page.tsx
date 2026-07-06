import Image from "next/image";
import { Breadcrumbs, ContinueReadingBlock, EntryGrid, InfoSection, PageHero, PageMain, RelatedPagesBlock, SiteFooter, SiteHeader } from "@/components/site/SiteChrome";
import { corePages, getPrintFiles, getPrintStats, links } from "@/lib/source-data";

export default function PrintPage() {
  const files = getPrintFiles();
  const stats = getPrintStats();
  const gallery = files.filter((file) => file.type === "card").slice(0, 10);
  const boxes = files.filter((file) => file.type === "box");

  return (
    <>
      <SiteHeader />
      <PageMain>
        <Breadcrumbs items={[corePages.print]} />
        <PageHero eyebrow="PrintHero" title="印刷成果展示" actions={links("printAssets", "printBox", "productionNote")}>
          <p>第一版印刷展示资源来自网站展示副本，只用于呈现实物进度，不作为规则、卡牌数据或官网文案来源。</p>
        </PageHero>
        <InfoSection title="资源统计" eyebrow="PrintStatsPanel">
          <div className="stat-grid">
            <strong>{stats.cards}<span>张卡牌资源</span></strong>
            <strong>{stats.boxes}<span>个包装面</span></strong>
            <strong>{stats.docs}<span>份说明副本</span></strong>
          </div>
        </InfoSection>
        <InfoSection title="卡牌展示" eyebrow="PrintGallery">
          <div className="print-showcase">
            {gallery.map((file) => <Image key={file.public_path} src={file.public_path} width={180} height={252} alt={file.name} />)}
          </div>
        </InfoSection>
        <InfoSection title="包装展示" eyebrow="PrintBoxGallery">
          <div className="box-gallery">
            {boxes.map((file) => <Image key={file.public_path} src={file.public_path} width={360} height={250} alt={file.name} />)}
          </div>
        </InfoSection>
        <InfoSection title="印刷资源" eyebrow="PrintResourceList">
          <EntryGrid items={links("printAssets", "printBox", "productionNote")} />
        </InfoSection>
        <RelatedPagesBlock items={links("printAssets", "printBox", "productionNote")} />
        <ContinueReadingBlock items={links("cards", "art", "crowdfunding")} />
      </PageMain>
      <SiteFooter />
    </>
  );
}
