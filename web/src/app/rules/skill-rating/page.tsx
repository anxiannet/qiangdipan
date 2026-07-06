import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function SkillRatingPage() {
  return (
    <StagePage
      title="技能评分标准"
      eyebrow="SkillRatingPage"
      parent={corePages.rules}
      status="当前页面用于展示技能评分标准，第一阶段先建立评分说明结构。"
      purpose="后续从 V1.2 技能评分标准读取评分规则，用于解释技能风险、评级和测试重点。"
      related={links("skills", "skillHistory", "cards", "futureRules")}
      continueItems={links("baseRules", "ruleHistory", "cardHistory")}
    />
  );
}
