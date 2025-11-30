import type { Metadata, Viewport } from "next";
import { Suspense } from "react";
import { Providers } from "./providers";
import { ScrollRestoration } from "../components/ScrollRestoration";
import { NavTabs } from "../components/NavTabs";
import "./globals.css";

export const metadata: Metadata = {
  title: "뉴스토스",
  description: "뉴스토스: 글로벌/로컬 이슈를 빠르게 훑는 모바일 웹",
  manifest: "/manifest.json",
  icons: {
    icon: [
      { url: "/icons/icon-192.svg", sizes: "192x192", type: "image/svg+xml" },
      { url: "/icons/icon-512.svg", sizes: "512x512", type: "image/svg+xml" }
    ],
    apple: { url: "/icons/icon-192.svg" }
  }
};

export const viewport: Viewport = {
  themeColor: "#ffffff"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="bg-white text-neutral-900 antialiased">
        <Providers>
          <Suspense fallback={null}>
            <ScrollRestoration />
          </Suspense>
          <div style={{ maxWidth: 480, margin: "0 auto", padding: "12px 16px 0", position: "sticky", top: 0, zIndex: 30, background: "#f8fafc" }}>
            <NavTabs />
          </div>
          {children}
        </Providers>
      </body>
    </html>
  );
}
