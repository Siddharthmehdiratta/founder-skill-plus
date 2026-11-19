import type { Metadata } from "next";
import { PageShell } from "@/components/site/shell";
import { ClaudeStudio } from "@/components/site/claude-studio";
import { href } from "@/lib/site";

export const metadata: Metadata = { title: "Claude helpers", description: "One click opens Claude with the request already written: pitch, objections, price test, landing page, interviews, competitors, a 30-day plan and review analysis." };

export default function Page() {
  return (
    <PageShell group="Product" kicker="Claude helpers" title="Let Claude do the founder homework" lead="Fill in your idea once. Each button opens Claude with the request already written, so you just press send. Works on Claude's free plan.">
      <div className="mx-auto max-w-7xl px-5 py-12 lg:px-8">
        <ClaudeStudio />
        <div className="mt-10 rounded-3xl bg-[#081C21] p-8 text-white">
          <h2 className="text-2xl font-semibold tracking-tight">Want customers to react to your idea?</h2>
          <p className="mt-2 max-w-2xl text-white/70">The panel builder creates AI customers from real market facts, and Claude plays every one of them. You get a score, what to fix and what to say.</p>
          <a href={href("/builder.html")} className="mt-6 inline-flex h-11 items-center rounded-xl bg-white px-5 font-medium text-[#081C21]">Build my panel</a>
        </div>
        <p className="mt-6 text-xs text-muted-foreground">If Claude opens without your request, press Copy the request and paste it. Claude is made by Anthropic; this site isn't affiliated with Anthropic.</p>
      </div>
    </PageShell>
  );
}
