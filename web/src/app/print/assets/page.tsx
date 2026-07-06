import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function PrintAssetsPage() {
  return <StagePage title="印刷资源清单" eyebrow="PrintResourceList" parent={corePages.print} status="当前页面用于展示印刷资源清单，第一阶段先建立入口。" purpose="后续继续从 manifest 读取资源分类，不把生产文件当成规则来源。" related={links("print", "printBox", "productionNote")} continueItems={links("cards", "art", "devlog")} />;
}
