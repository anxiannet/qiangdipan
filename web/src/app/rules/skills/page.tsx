import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function SkillsPage() {
  return (
    <StagePage
      title="技能汇总"
      eyebrow="SkillSummaryEntry"
      parent={corePages.rules}
      status="当前页面用于展示基础版技能汇总，第一阶段先建立入口和关联。"
      purpose="后续从 V1.2 技能汇总表读取技能，不在页面中维护第二份技能表。"
      related={links("skillRating", "ruleHistory", "cards", "futureRules")}
      continueItems={links("baseRules", "manual", "quickReference")}
    />
  );
}
