import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function VisualSpecPage() {
  return <StagePage title="视觉规范" eyebrow="VisualSpecEntry" parent={corePages.art} status="当前页面用于承接视觉规范，第一阶段先建立入口。" purpose="后续从视觉总规范读取蓝金西游桌游风、妖怪角色和实体卡牌展示要求。" related={links("illustrationReviewFlow", "illustrationHistory", "cardFinalReviewFlow", "cards")} continueItems={links("uiSpec", "print", "devlog")} />;
}
