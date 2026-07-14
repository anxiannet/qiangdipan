import fs from "node:fs";
import path from "node:path";
import printManifest from "../../public/assets/print/v1/manifest.json";

export type LinkItem = {
  href: string;
  label: string;
  description?: string;
};

export type CardRecord = {
  id: string;
  name: string;
  count: string;
  stars: string;
  type: string;
  category: "monster" | "treasure" | "territory";
  skill: string;
  rating?: string;
  image?: string;
};

type ManifestFile = {
  type: string;
  name: string;
  public_path: string;
  category: string;
  note: string;
};

const repoRoot = path.join(process.cwd(), "..");
const cardTablePath = path.join(repoRoot, "规则", "V1.2-基础卡表.md");

export const topNav: LinkItem[] = [
  { href: "/", label: "首页" },
  { href: "/cards", label: "卡牌" },
  { href: "/rules", label: "规则" },
  { href: "/play", label: "试玩" },
  { href: "/print", label: "印刷成果" },
  { href: "/art", label: "美术档案" },
  { href: "/crowdfunding", label: "众筹预热" },
  { href: "/devlog", label: "开发记录" }
];

export const corePages: Record<string, LinkItem> = {
  home: { href: "/", label: "首页", description: "了解实体卡牌、玩法和当前进度。" },
  cards: { href: "/cards", label: "卡牌图鉴", description: "查看基础版卡牌的卡册入口。" },
  cardHistory: { href: "/cards/history", label: "卡牌调整历史", description: "记录卡牌进入测试后的变化。" },
  backupCards: { href: "/cards/backup", label: "备选卡表", description: "后续扩展和候选卡牌的展示入口。" },
  rules: { href: "/rules", label: "规则入口", description: "从基础规则、双人规则、技能和玩家版说明进入。" },
  baseRules: { href: "/rules/base", label: "抢地盘基础规则", description: "控制同一妖域 3 块地盘，立即获胜。" },
  duelRules: { href: "/rules/duel", label: "双人局地盘设置", description: "6块快速局、9块标准局与12块完整局。" },
  skills: { href: "/rules/skills", label: "技能汇总", description: "基础版技能的集中阅读入口。" },
  skillRating: { href: "/rules/skill-rating", label: "技能评分标准", description: "说明技能强度和评级的判断方式。" },
  skillHistory: { href: "/rules/skill-history", label: "技能变化历史", description: "记录技能随测试反馈的变化。" },
  ruleHistory: { href: "/rules/history", label: "规则变化历史", description: "记录规则随试玩反馈的调整。" },
  futureRules: { href: "/rules/future", label: "未来扩展与双人对战计划", description: "预留双人对战和扩展玩法入口。" },
  manual: { href: "/rules/manual", label: "游戏手册，玩家版", description: "面向玩家的完整手册入口。" },
  quickReference: { href: "/rules/quick-reference", label: "指南卡，玩家版", description: "桌面快速查阅的指南入口。" },
  play: { href: "/play", label: "试玩入口", description: "进入游戏大厅和后续试玩模式。" },
  print: { href: "/print", label: "印刷成果展示", description: "查看第一版实体卡牌和包装资源。" },
  printAssets: { href: "/print/assets", label: "印刷资源清单", description: "查看网站展示用印刷资源副本。" },
  printBox: { href: "/print/box", label: "包装展示", description: "查看第一版包装盒展示入口。" },
  productionNote: { href: "/print/production-note", label: "生产说明", description: "记录印刷生产展示说明入口。" },
  art: { href: "/art", label: "美术档案", description: "查看视觉规范、插画流程和迭代入口。" },
  visualSpec: { href: "/art/visual-spec", label: "视觉规范", description: "承接官网和卡牌美术视觉规范。" },
  uiSpec: { href: "/art/ui-spec", label: "UI 规范", description: "承接官网与游戏界面组件规范。" },
  illustrationReviewFlow: { href: "/art/illustration-review-flow", label: "插画审核流程", description: "承接插画从草稿到审核的流程。" },
  cardFinalReviewFlow: { href: "/art/card-final-review-flow", label: "成品卡审核流程", description: "承接成品卡最终检查流程。" },
  illustrationHistory: { href: "/art/illustration-history", label: "插画迭代历史", description: "记录插画从草稿到定稿的变化。" },
  crowdfunding: { href: "/crowdfunding", label: "众筹预热", description: "查看预热状态和意向收集入口。" },
  presalePlan: { href: "/crowdfunding/presale-plan", label: "预售计划", description: "承接后续小批量预售计划。" },
  playtestFeedback: { href: "/crowdfunding/playtest-feedback", label: "试玩反馈", description: "承接玩家测试反馈展示。" },
  devlog: { href: "/devlog", label: "开发记录", description: "记录规则、美术、印刷和网站进展。" },
  simulationResults: {
    href: "/devlog/simulation-results",
    label: "AI模拟测试结果",
    description: "查看正式牌组18000局与双人地盘12000局测试。"
  },
  roadmap: { href: "/devlog/roadmap", label: "开发路线图", description: "查看后续阶段推进顺序。" },
  websiteDevlog: { href: "/devlog/website", label: "网站开发记录", description: "记录官网结构与部署进展。" }
};

function slugifyCardName(name: string) {
  return encodeURIComponent(name.trim());
}

function imageByCardName(name: string, category: CardRecord["category"]) {
  const files = (printManifest.files as ManifestFile[]).filter((file) => file.type === "card");
  const match = files.find((file) => file.category === category && file.name.endsWith(`_${name}`));
  return match?.public_path;
}

function parseMarkdownCards(): CardRecord[] {
  const markdown = fs.readFileSync(cardTablePath, "utf8");
  const cards: CardRecord[] = [];

  for (const line of markdown.split("\n")) {
    if (!line.startsWith("|") || line.includes("---") || line.includes("名称")) {
      continue;
    }

    const cells = line
      .split("|")
      .slice(1, -1)
      .map((cell) => cell.trim());

    if (cells.length === 11 && /^\d+$/.test(cells[1]) && /^\d+$/.test(cells[3])) {
      const [name, count, , stars, type, , skill, , , rating] = cells;
      cards.push({
        id: slugifyCardName(name),
        name,
        count,
        stars,
        type,
        category: "monster",
        skill,
        rating,
        image: imageByCardName(name, "monster")
      });
    }

    if (cells.length === 10 && /^\d+$/.test(cells[1]) && cells[2] === "法宝") {
      const [name, count, type, , , skill, , , rating] = cells;
      cards.push({
        id: slugifyCardName(name),
        name,
        count,
        stars: "无",
        type,
        category: "treasure",
        skill,
        rating,
        image: imageByCardName(name, "treasure")
      });
    }

    if (cells.length === 7 && /^\d+$/.test(cells[2]) && cells[3] === "地盘") {
      const [domain, name, count, type, stars, skill] = cells;
      cards.push({
        id: slugifyCardName(name),
        name,
        count,
        stars,
        type: `${domain}妖域${type}`,
        category: "territory",
        skill,
        image: imageByCardName(name, "territory")
      });
    }
  }

  return cards;
}

export function getCards() {
  return parseMarkdownCards();
}

export function getCardById(id: string) {
  const decoded = decodeURIComponent(id);
  return getCards().find((card) => card.name === decoded || card.id === id);
}

export function getRelatedCards(card: CardRecord) {
  return getCards()
    .filter((item) => item.name !== card.name && (item.category === card.category || item.type === card.type))
    .slice(0, 4)
    .map((item) => ({
      href: `/cards/${item.id}`,
      label: item.name,
      description: `${item.type}，${item.stars}星，${item.count}张。`
    }));
}

export function getPrintFiles() {
  return printManifest.files as ManifestFile[];
}

export function getPrintStats() {
  const files = getPrintFiles();
  return {
    cards: files.filter((file) => file.type === "card").length,
    boxes: files.filter((file) => file.type === "box").length,
    docs: files.filter((file) => file.type === "doc").length
  };
}

export function links(...keys: Array<keyof typeof corePages>) {
  return keys.map((key) => corePages[key]);
}
