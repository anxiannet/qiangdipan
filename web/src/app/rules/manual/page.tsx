import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function ManualPage() {
  return (
    <StagePage
      title="游戏手册，玩家版"
      eyebrow="PlayerManualEntry"
      parent={corePages.rules}
      status="当前页面用于承接玩家版游戏手册，第一阶段先建立入口。"
      purpose="后续在明确读取玩家手册时，整理成适合手机阅读的玩家说明。"
      related={links("baseRules", "quickReference", "skills")}
      continueItems={links("cards", "play", "print")}
    />
  );
}
