import type { Metadata } from "next";
import { PageShell } from "@/components/site/shell";
import { AssumptionTests } from "@/components/site/assumption-tests";

export const metadata: Metadata = {
  title: "Assumption tests",
  description: "Turn the gaps in your idea into tests you can run this week. One assumption each, a pass number set before you start, and the cost in money and days. Free.",
};

export default function Page() {
  return (
    <PageShell
      group="Product"
      kicker="Assumption tests"
      title="Find out you are wrong in week one, not year one."
      lead="A score tells you where the idea is thin. It does not tell you what to do on Monday. Each test below takes one thing you are assuming, says how to find out this week, and fixes what counts as a pass before you start. Riskiest first."
    >
      <div className="mx-auto max-w-7xl px-5 py-12 lg:px-8"><AssumptionTests /></div>
    </PageShell>
  );
}
