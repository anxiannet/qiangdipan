import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function RuleHistoryPage() {
  return (
    <StagePage
      title="规则变化历史"
      eyebrow="RuleHistoryEntry"
      parent={corePages.rules}
      status="当前页面用于展示规则变化历史，第一阶段先建立页面结构，后续随试玩反馈补充内容。"
      purpose="记录基础规则、技能解释和未来扩展之间的调整脉络。"
      related={links("baseRules", "skills", "skillRating", "futureRules")}
      continueItems={links("cards", "play", "devlog")}
    />
  );
}
