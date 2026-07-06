import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function SkillHistoryPage() {
  return (
    <StagePage
      title="技能变化历史"
      eyebrow="SkillHistoryEntry"
      parent={corePages.rules}
      status="当前页面用于记录技能调整，第一阶段先建立入口。"
      purpose="后续随试玩反馈补充技能改动原因、影响范围和关联卡牌。"
      related={links("skills", "skillRating", "cards", "futureRules")}
      continueItems={links("ruleHistory", "baseRules", "devlog")}
    />
  );
}
