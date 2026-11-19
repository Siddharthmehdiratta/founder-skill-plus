import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Founder Plus: test your business idea on AI customers", template: "%s · Founder Plus" },
  description: "Free. Pick who you want to sell to, and a panel of AI customers reacts to your offer in their own words. Claude gives you a score, what to fix and what to say.",
  icons: { icon: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='9' fill='%230E9A74'/%3E%3Ccircle cx='16' cy='16' r='6' fill='none' stroke='%23fff' stroke-width='3'/%3E%3C/svg%3E" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={GeistSans.variable}>
      <body className="min-h-screen bg-background font-sans text-foreground antialiased" style={{ fontFamily: "var(--font-geist-sans), ui-sans-serif, system-ui, sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
