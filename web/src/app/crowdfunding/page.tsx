import { Breadcrumbs, ContinueReadingBlock, EntryGrid, InfoSection, PageHero, PageMain, RelatedPagesBlock, SiteFooter, SiteHeader } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function CrowdfundingPage() {
  return (
    <>
      <SiteHeader />
      <PageMain>
        <Breadcrumbs items={[corePages.crowdfunding]} />
        <PageHero eyebrow="CrowdfundingHero" title="众筹预热" actions={links("print", "play")}>
          <p>当前只做项目预热和意向收集，先展示实体证明、开发进度和试玩反馈入口。</p>
        </PageHero>
        <InfoSection title="产品证明" eyebrow="ProductProofSection">
          <EntryGrid items={links("print", "cards", "rules")} />
        </InfoSection>
        <InfoSection title="当前进度" eyebrow="ProgressSection">
          <div className="steps">
            <p>小批量实体测试版准备中。</p>
            <p>包装盒实物检查和拍摄将继续推进。</p>
            <p>首批测试版预售意向将根据试玩反馈调整。</p>
          </div>
        </InfoSection>
        <InfoSection title="预热入口" eyebrow="PresalePlanEntry / PlaytestFeedbackEntry">
          <EntryGrid items={links("presalePlan", "playtestFeedback", "play")} />
        </InfoSection>
        <InfoSection title="意向收集" eyebrow="InterestFormSection">
          <p>第一阶段保留意向收集区域，不接入正式交易、礼包、会员或充值。</p>
        </InfoSection>
        <RelatedPagesBlock items={links("print", "play", "presalePlan", "playtestFeedback")} />
        <ContinueReadingBlock items={links("cards", "rules", "devlog")} />
      </PageMain>
      <SiteFooter />
    </>
  );
}
