import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function PresalePlanPage() {
  return <StagePage title="预售计划" eyebrow="PresalePlanEntry" parent={corePages.crowdfunding} status="当前页面用于承接小批量预售计划，第一阶段先建立入口。" purpose="后续根据试玩反馈和实体样品状态补充测试版预售方案。" related={links("crowdfunding", "print", "playtestFeedback")} continueItems={links("cards", "rules", "devlog")} />;
}
