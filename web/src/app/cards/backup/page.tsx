import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function BackupCardsPage() {
  return (
    <StagePage
      title="备选卡表"
      eyebrow="BackupCardsEntry"
      parent={corePages.cards}
      status="当前页面用于承接备选卡牌展示，第一阶段先建立入口。"
      purpose="后续在明确读取备选方案时，展示候选卡与基础版关系。"
      related={links("cards", "cardHistory", "futureRules")}
      continueItems={links("rules", "devlog", "crowdfunding")}
    />
  );
}
