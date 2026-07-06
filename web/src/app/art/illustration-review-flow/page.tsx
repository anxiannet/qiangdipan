import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function IllustrationReviewFlowPage() {
  return <StagePage title="插画审核流程" eyebrow="IllustrationFlowEntry" parent={corePages.art} status="当前页面用于承接插画审核流程，第一阶段先建立入口。" purpose="后续展示从草图、角色气质到最终插画审核的流程。" related={links("visualSpec", "illustrationHistory", "cardFinalReviewFlow", "cards")} continueItems={links("art", "print", "devlog")} />;
}
