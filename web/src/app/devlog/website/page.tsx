import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function WebsiteDevlogPage() {
  return <StagePage title="网站开发记录" eyebrow="WebsiteDevelopmentEntry" parent={corePages.devlog} status="当前页面用于记录官网开发进展，第一阶段先建立入口。" purpose="后续记录页面结构、导航、部署状态和试玩技术接入进展。" related={links("devlog", "roadmap", "play", "print")} continueItems={links("cards", "rules", "art")} />;
}
