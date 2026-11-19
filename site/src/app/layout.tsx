import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://siddharthmehdiratta.github.io"),
  openGraph: { type: "website", siteName: "Founder Plus", url: "https://siddharthmehdiratta.github.io/founder-skill-plus/", images: [{ url: "https://siddharthmehdiratta.github.io/founder-skill-plus/og.png", width: 1200, height: 630, alt: "Founder Plus: Test it before you build it." }] },
  twitter: { card: "summary_large_image", images: ["https://siddharthmehdiratta.github.io/founder-skill-plus/og.png"] },
  title: { default: "Founder Plus: test your business idea on AI customers", template: "%s · Founder Plus" },
  description: "Free. Pick who you want to sell to, and a panel of AI customers reacts to your offer in their own words. Claude gives you a score, what to fix and what to say.",
  icons: { icon: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='9' fill='%230E9A74'/%3E%3Ccircle cx='16' cy='16' r='6' fill='none' stroke='%23fff' stroke-width='3'/%3E%3C/svg%3E" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={GeistSans.variable}>
      <head>
        {/* Fonts load from Fontshare (Indian Type Foundry, free for commercial use; files may not be redistributed). */}
        <link rel="preconnect" href="https://api.fontshare.com" />
        {/* One link per font: the Fontshare API reads only the first font in a link. */}
        <link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=zodiak@400,700&display=swap" />
        <link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=switzer@400,500,600&display=swap" />
      </head>
      <body className="min-h-screen bg-background font-sans text-foreground antialiased" style={{ fontFamily: "'Switzer', var(--font-geist-sans), ui-sans-serif, system-ui, sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
