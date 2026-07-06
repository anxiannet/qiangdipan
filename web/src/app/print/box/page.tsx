import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function PrintBoxPage() {
  return <StagePage title="包装展示" eyebrow="PrintBoxGallery" parent={corePages.print} status="当前页面用于展示包装盒第一版进度，第一阶段先建立入口。" purpose="后续展示天地盖硬盒尺寸、正背面和侧面效果。" related={links("print", "printAssets", "productionNote")} continueItems={links("crowdfunding", "art", "devlog")} />;
}
