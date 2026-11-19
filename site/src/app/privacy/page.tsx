import type { Metadata } from "next";
import { PageShell } from "@/components/site/shell";
import { href } from "@/lib/site";

export const metadata: Metadata = { title: "Privacy", description: "What happens to your business idea: nothing is stored, nothing is sold." };

export default function Page() {
  return (
    <PageShell group="Company" kicker="Privacy" title="What happens to your idea" lead="Short version: the builder runs on your own device, nothing is stored, and your pitch goes only where you paste it. Updated 19 November 2026.">
      <article className="mx-auto max-w-3xl px-5 py-16 text-[1.04rem] leading-[1.75] text-[#26363B]">
        {[["The panel builder", "Everything you type is kept in your browser. Nothing is sent to us."],
          ["Running the panel", "You copy one message and paste it into your own Claude app. What you paste there is covered by Anthropic's privacy policy, not ours."],
          ["Saved setups", "Download customer.json to keep a setup. It's a file on your device; we never see it."],
          ["Review analysis", "Reviews you paste are analysed in your Claude chat. Remove customer names and contact details before pasting."],
          ["No accounts, no tracking", "There is no sign-up, no database and no advertising tracker. GitHub Pages, which hosts this site, may keep standard server logs under GitHub's own privacy policy."],
          ["Fonts", "The typefaces load from Fontshare, a free font service by Indian Type Foundry. Like any website request, your browser shares its IP address with Fontshare to fetch them. No cookies are set by this site."],
          ["Questions", "Ask anything about privacy on our contact page."]].map(([t, d]) => (
          <section key={t} className="border-b py-7 first:pt-0 last:border-b-0"><h2 className="text-xl font-semibold tracking-tight">{t}</h2><p className="mt-2 text-muted-foreground">{d}</p></section>
        ))}
        <a href={href("/contact/")} className="mt-4 inline-block font-medium text-primary">Contact us</a>
      </article>
    </PageShell>
  );
}
