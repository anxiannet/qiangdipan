import Link from "next/link";
import { corePages, LinkItem, topNav } from "@/lib/source-data";

export function SiteHeader() {
  return (
    <header className="site-header">
      <Link href="/" className="brand-mark" aria-label="夕妖：抢地盘首页">
        <span className="brand-seal">夕</span>
        <span>
          <strong>夕妖：抢地盘</strong>
          <small>西游妖怪桌游</small>
        </span>
      </Link>
      <nav className="top-nav" aria-label="一级导航">
        {topNav.map((item) => (
          <Link key={item.href} href={item.href}>
            {item.label}
          </Link>
        ))}
      </nav>
      <span className="nav-menu-mark" aria-hidden="true">
        <span />
        <span />
        <span />
      </span>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <p>《夕妖：抢地盘》当前处于实体测试版准备与官网第一阶段搭建中。</p>
      <div>
        <Link href="/rules/base">基础规则</Link>
        <Link href="/cards">卡牌图鉴</Link>
        <Link href="/print">印刷成果</Link>
      </div>
    </footer>
  );
}

export function PageMain({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <main className={`page-main ${className}`}>{children}</main>;
}

export function Breadcrumbs({ items }: { items: LinkItem[] }) {
  return (
    <nav className="breadcrumbs" aria-label="面包屑">
      <Link href="/">首页</Link>
      {items.map((item) => (
        <Link key={item.href} href={item.href}>
          {item.label}
        </Link>
      ))}
    </nav>
  );
}

export function PageHero({
  eyebrow,
  title,
  children,
  actions
}: {
  eyebrow: string;
  title: string;
  children: React.ReactNode;
  actions?: LinkItem[];
}) {
  return (
    <section className="page-hero">
      <div className="page-hero-content">
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <div className="hero-copy">{children}</div>
        {actions ? <LinkRow items={actions} /> : null}
      </div>
    </section>
  );
}

export function InfoSection({
  title,
  eyebrow,
  children,
  className = ""
}: {
  title: string;
  eyebrow?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`info-section ${className}`}>
      {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
      <h2>{title}</h2>
      {children}
    </section>
  );
}

export function LinkRow({ items }: { items: LinkItem[] }) {
  return (
    <div className="link-row">
      {items.map((item) => (
        <Link key={item.href} className="action-link" href={item.href}>
          <span>{item.label}</span>
          {item.description ? <small>{item.description}</small> : null}
        </Link>
      ))}
    </div>
  );
}

export function EntryGrid({ items }: { items: LinkItem[] }) {
  return (
    <div className="entry-grid">
      {items.map((item) => (
        <Link key={item.href} href={item.href} className="entry-card">
          <strong>{item.label}</strong>
          {item.description ? <span>{item.description}</span> : null}
        </Link>
      ))}
    </div>
  );
}

export function RelatedPagesBlock({ items }: { items: LinkItem[] }) {
  return (
    <section className="relation-block" aria-labelledby="related-pages-title">
      <h2 id="related-pages-title">相关页面</h2>
      <EntryGrid items={items} />
    </section>
  );
}

export function ContinueReadingBlock({ items }: { items: LinkItem[] }) {
  return (
    <section className="relation-block continue-block" aria-labelledby="continue-reading-title">
      <h2 id="continue-reading-title">继续阅读</h2>
      <EntryGrid items={items} />
    </section>
  );
}

export function StatusPanel({
  status,
  purpose,
  parent
}: {
  status: string;
  purpose: string;
  parent: LinkItem;
}) {
  return (
    <section className="status-panel">
      <div>
        <span>当前状态</span>
        <p>{status}</p>
      </div>
      <div>
        <span>预计用途</span>
        <p>{purpose}</p>
      </div>
      <Link href={parent.href} className="parent-link">
        返回{parent.label}
      </Link>
    </section>
  );
}

export function StagePage({
  title,
  eyebrow,
  status,
  purpose,
  parent,
  related,
  continueItems
}: {
  title: string;
  eyebrow: string;
  status: string;
  purpose: string;
  parent: LinkItem;
  related: LinkItem[];
  continueItems: LinkItem[];
}) {
  return (
    <>
      <SiteHeader />
      <PageMain>
        <Breadcrumbs items={[parent, { href: "#", label: title }]} />
        <PageHero eyebrow={eyebrow} title={title}>
          <p>{purpose}</p>
        </PageHero>
        <StatusPanel status={status} purpose={purpose} parent={parent} />
        <RelatedPagesBlock items={related} />
        <ContinueReadingBlock items={continueItems} />
      </PageMain>
      <SiteFooter />
    </>
  );
}

export function DefaultContinue() {
  return <ContinueReadingBlock items={[corePages.cards, corePages.baseRules, corePages.play]} />;
}
