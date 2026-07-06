import Link from "next/link";
import { corePages } from "@/lib/source-data";

export default function PlayPage() {
  return (
    <main className="game-shell">
      <header className="game-header">
        <Link href="/" className="game-brand">夕妖：抢地盘</Link>
        <span>游戏大厅</span>
      </header>
      <section className="game-stage">
        <div className="mode-select-panel">
          <p className="eyebrow">ModeSelectPanel</p>
          <h1>选择试玩模式</h1>
          <button>规则教学</button>
          <button>人机练习</button>
          <button>本地热座</button>
          <button>好友房</button>
        </div>
        <aside className="game-status-panel">
          <p>当前状态</p>
          <strong>第一阶段先建立游戏大厅入口</strong>
          <span>后续接入 PixiJS 游戏桌面、规则教学和本地试玩。</span>
        </aside>
      </section>
      <nav className="game-footer-bar" aria-label="游戏层导航">
        <Link href={corePages.cards.href}>卡册</Link>
        <Link href={corePages.baseRules.href}>规则</Link>
        <Link href={corePages.crowdfunding.href}>预热</Link>
        <Link href="/">返回官网</Link>
      </nav>
      <div className="loading-overlay" aria-hidden="true">妖王大厅就绪中</div>
    </main>
  );
}
