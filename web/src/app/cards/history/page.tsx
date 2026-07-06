import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function CardHistoryPage() {
  return (
    <StagePage
      title="卡牌调整历史"
      eyebrow="CardHistoryEntry"
      parent={corePages.cards}
      status="当前页面用于展示卡牌随测试发生的调整，第一阶段先建立页面结构。"
      purpose="后续记录卡牌进入、移出、文案调整和测试反馈对应关系。"
      related={links("cards", "skills", "skillRating", "illustrationHistory")}
      continueItems={links("backupCards", "rules", "print")}
    />
  );
}
