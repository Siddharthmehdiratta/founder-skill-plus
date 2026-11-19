import type { Metadata } from "next";
import { PageShell } from "@/components/site/shell";

export const metadata: Metadata = { title: "Changelog", description: "What's new in Founder Plus, and when." };

const LOG = [
  ["19 Nov 2026", "A new website", ["A proper home page with real screenshots of the report", "Separate pages for pricing, help, contact, about and privacy", "Report a problem and give feedback straight from the contact page"]],
  ["18 Nov 2026", "City and income tiers", ["India by city tier and income tier, with an India sample report", "After-purchase reviews and NPS from every AI customer", "A simpler builder with dropdowns instead of typed fields"]],
  ["18 Nov 2026", "Product Improvement Manager", ["Turn real customer reviews into a ranked fix list"]],
  ["17 Nov 2026", "Run it in Claude", ["One message to paste into the Claude app, no install needed", "A content tester, an audit score and a sales answer kit"]],
  ["17 Nov 2026", "Businesses too", ["B2B panels with decision-makers by role", "11 ready setups by industry"]],
] as const;

export default function Page() {
  return (
    <PageShell group="Learn" kicker="Changelog" title="What's new" lead="Every change to Founder Plus, newest first. The full history is on GitHub.">
      <div className="mx-auto max-w-3xl px-5 py-16">
        <ol className="relative grid gap-12 border-l pl-8">
          {LOG.map(([d, t, items]) => (
            <li key={t} className="relative">
              <span aria-hidden className="absolute top-1.5 -left-[2.3rem] size-3 rounded-full border-2 border-background bg-primary ring-4 ring-primary/15" />
              <p className="text-sm text-muted-foreground">{d}</p>
              <h2 className="mt-1 text-xl font-semibold tracking-tight">{t}</h2>
              <ul className="mt-3 grid list-disc gap-1.5 pl-5 text-muted-foreground">{items.map((x) => <li key={x}>{x}</li>)}</ul>
            </li>
          ))}
        </ol>
      </div>
    </PageShell>
  );
}
