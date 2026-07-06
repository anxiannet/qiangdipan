import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function CardFinalReviewFlowPage() {
  return <StagePage title="成品卡审核流程" eyebrow="FinalReviewEntry" parent={corePages.art} status="当前页面用于承接成品卡审核流程，第一阶段先建立入口。" purpose="后续展示卡面、文字、印刷边界和最终检查流程。" related={links("visualSpec", "illustrationReviewFlow", "illustrationHistory", "cards")} continueItems={links("art", "print", "devlog")} />;
}
