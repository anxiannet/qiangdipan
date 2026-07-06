import { StagePage } from "@/components/site/SiteChrome";
import { corePages, links } from "@/lib/source-data";

export default function FutureRulesPage() {
  return (
    <StagePage
      title="未来扩展与双人对战计划"
      eyebrow="FutureRulesEntry"
      parent={corePages.rules}
      status="当前页面用于承接未来扩展与双人对战计划，第一阶段先建立入口。"
      purpose="后续展示双人对战测试方向、扩展牌池边界和阶段目标。"
      related={links("baseRules", "ruleHistory", "skills", "cards")}
      continueItems={links("play", "devlog", "crowdfunding")}
    />
  );
}
