import type { Metadata } from "next";
import { PageShell } from "@/components/site/shell";
import { IdeaChecker } from "@/components/site/idea-checker";

export const metadata: Metadata = { title: "Idea Checker", description: "Six questions founders skip, a score, and the cheapest test for each gap. Two minutes, free." };

export default function Page() {
  return (
    <PageShell group="Product" kicker="Idea Checker" title="Check your idea in two minutes" lead="Six questions founders often skip. Each weak answer comes with the cheapest way to fix it. Then test the pitch on an AI panel. Nothing you type leaves your browser.">
      <div className="mx-auto max-w-7xl px-5 py-12 lg:px-8"><IdeaChecker /></div>
    </PageShell>
  );
}
