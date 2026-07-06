import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function RoadmapPage() {
  return <StagePage title="开发路线图" eyebrow="RoadmapEntry" parent={corePages.devlog} status="当前页面用于展示开发路线图，第一阶段先建立入口。" purpose="后续记录实体测试、官网、试玩和众筹预热的阶段推进。" related={links("devlog", "websiteDevlog", "print", "play")} continueItems={links("cards", "rules", "crowdfunding")} />;
}
