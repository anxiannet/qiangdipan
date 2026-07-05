export default function Home() {
  return (
    <main className="site-shell">
      <section className="intro">
        <p className="eyebrow">正式网站工程</p>
        <h1>《夕妖：抢地盘》</h1>
        <div className="status-list" aria-label="工程状态">
          <p>正式网站工程已建立</p>
          <p>游戏渲染层将采用 PixiJS 8</p>
          <p>官网层采用 Next.js + React + TypeScript</p>
        </div>
      </section>
    </main>
  );
}
