import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Agent Hunt — AI Agent 岗位市场分析",
  description:
    "跨市场分析 AI Agent 工程师岗位需求，覆盖国内外主流招聘平台",
};

const NAV_ITEMS = [
  { href: "/", label: "总览" },
  { href: "/skills", label: "技能图谱" },
  { href: "/salary", label: "薪资分析" },
  { href: "/gaps", label: "市场差异" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="zh"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-gray-50">
        <header className="border-b bg-white sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 h-14 flex items-center gap-8">
            <Link href="/" className="font-bold text-lg">
              Agent Hunt
            </Link>
            <nav className="flex gap-6 text-sm">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
          {children}
        </main>
        <footer className="border-t bg-white py-4 text-center text-xs text-gray-400">
          Agent Hunt — 用数据洞察 AI Agent 工程师市场
        </footer>
      </body>
    </html>
  );
}
