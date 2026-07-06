import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function ProductionNotePage() {
  return <StagePage title="生产说明" eyebrow="ProductionNoteEntry" parent={corePages.print} status="当前页面用于承接生产说明展示，第一阶段先建立入口。" purpose="生产说明只用于展示印刷进度和交付状态，不作为规则、卡牌数据或官网核心文案来源。" related={links("print", "printAssets", "printBox")} continueItems={links("cards", "crowdfunding", "devlog")} />;
}
