import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function IllustrationHistoryPage() {
  return <StagePage title="插画迭代历史" eyebrow="IllustrationHistoryEntry" parent={corePages.art} status="当前页面用于记录插画迭代，第一阶段先建立入口。" purpose="后续从美术历史资料进入具体卡牌插画变化，不临时编写单卡背景。" related={links("visualSpec", "illustrationReviewFlow", "cardFinalReviewFlow", "cards")} continueItems={links("art", "cards", "print")} />;
}
