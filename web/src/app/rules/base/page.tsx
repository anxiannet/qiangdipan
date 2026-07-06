import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function BaseRulesPage() {
  return (
    <StagePage
      title="抢地盘基础规则"
      eyebrow="RulesBasePage"
      parent={corePages.rules}
      status="当前页面用于承接基础规则正文，第一阶段先建立阅读结构和关联入口。"
      purpose="后续从当前规则源文件整理玩家可读版本，保持核心规则来源唯一。控制同一妖域 3 块地盘，立即获胜。"
      related={links("ruleHistory", "skills", "skillRating", "cards", "futureRules", "manual", "quickReference")}
      continueItems={links("play", "cards", "print")}
    />
  );
}
