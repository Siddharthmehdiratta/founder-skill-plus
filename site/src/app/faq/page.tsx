import type { Metadata } from "next";
import { Button } from "@/components/ui/button";
import { PageShell } from "@/components/site/shell";
import { FaqSearch } from "@/components/site/faq-search";
import { SITE, href } from "@/lib/site";

export const metadata: Metadata = { title: "FAQ", description: "Answers about getting started, the results, markets and privacy." };

export default function Page() {
  return (
    <PageShell group="Learn" kicker="FAQ" title="Frequently asked questions" lead="Quick answers about getting started, the results, customers and markets, and privacy. Type a word to search.">
      <div className="mx-auto max-w-3xl px-5 py-16">
        <FaqSearch />
        <div className="mt-16 rounded-3xl border bg-[#F7FAF9] p-8">
          <h2 className="text-xl font-semibold tracking-tight">Still have a question?</h2>
          <p className="mt-2 text-muted-foreground">Ask in our public Q&amp;A on GitHub. Answers stay there for the next person.</p>
          <div className="mt-6 flex flex-wrap gap-3"><Button className="rounded-xl" asChild><a href={SITE.ask}>Ask a question</a></Button><Button variant="outline" className="rounded-xl" asChild><a href={href("/contact/")}>Other ways to reach us</a></Button></div>
        </div>
      </div>
    </PageShell>
  );
}
