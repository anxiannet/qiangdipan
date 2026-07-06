import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function PlaytestFeedbackPage() {
  return <StagePage title="试玩反馈" eyebrow="PlaytestFeedbackEntry" parent={corePages.crowdfunding} status="当前页面用于承接试玩反馈，第一阶段先建立入口。" purpose="后续展示玩家试玩后的规则、节奏、卡牌和实体手感反馈。" related={links("crowdfunding", "play", "ruleHistory")} continueItems={links("cards", "rules", "devlog")} />;
}
