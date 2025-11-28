import type { Metadata } from "next";
import { Geist, Geist_Mono, Lora } from "next/font/google";
import { Providers } from "@/components/Providers";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
  preload: true,
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

const lora = Lora({
  variable: "--font-lora",
  subsets: ["latin"],
  display: "swap",
  preload: true,
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: {
    default: "News Spectrum - Global Intelligence Platform",
    template: "%s | News Spectrum",
  },
  description: "Understand global issues not as a single headline, but as a spectrum of perspectives across countries, blocs, and media outlets. Analyze thousands of articles from G10+ countries daily.",
  keywords: ["global news", "news analysis", "international perspectives", "media stance", "geopolitics", "news spectrum", "global intelligence"],
  authors: [{ name: "News Spectrum Team" }],
  creator: "News Spectrum",
  publisher: "News Spectrum",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
  openGraph: {
    type: "website",
    locale: "en_US",
    alternateLocale: ["ko_KR"],
    url: "/",
    title: "News Spectrum - Global Intelligence Platform",
    description: "Understand global issues as a spectrum of perspectives across countries, blocs, and media outlets.",
    siteName: "News Spectrum",
  },
  twitter: {
    card: "summary_large_image",
    title: "News Spectrum - Global Intelligence Platform",
    description: "Understand global issues as a spectrum of perspectives across countries, blocs, and media outlets.",
    creator: "@newsspectrum",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    // Add verification codes when available
    // google: 'google-site-verification-code',
    // yandex: 'yandex-verification-code',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${lora.variable} antialiased font-sans`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
