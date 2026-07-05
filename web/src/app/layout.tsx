import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "夕妖：抢地盘",
  description: "《夕妖：抢地盘》正式网站工程"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
