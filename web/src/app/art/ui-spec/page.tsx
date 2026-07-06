import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function UiSpecPage() {
  return <StagePage title="UI 规范" eyebrow="UiSpecEntry" parent={corePages.art} status="当前页面用于承接 UI 组件规范，第一阶段先建立入口。" purpose="后续从 UI 规范读取官网和游戏层组件边界。" related={links("visualSpec", "illustrationReviewFlow", "cards")} continueItems={links("art", "play", "devlog")} />;
}
