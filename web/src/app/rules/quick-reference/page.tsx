import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function QuickReferencePage() {
  return (
    <StagePage
      title="指南卡，玩家版"
      eyebrow="QuickReferenceEntry"
      parent={corePages.rules}
      status="当前页面用于承接玩家版指南卡，第一阶段先建立入口。"
      purpose="后续在明确读取指南卡时，展示适合桌面快速查阅的版本。"
      related={links("baseRules", "manual", "skills")}
      continueItems={links("cards", "play", "print")}
    />
  );
}
