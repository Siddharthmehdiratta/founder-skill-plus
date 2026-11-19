"use client";
import { useMemo, useState } from "react";
import { CheckCircle2Icon, CircleAlertIcon } from "lucide-react";
import { href } from "@/lib/site";
import { ClaudeButton } from "./claude-button";

/* A quick, honest self-check before running a panel. Six questions founders skip, each with what to do about a weak answer.
   It scores your own answers, not the market: run the AI panel, then real people, for evidence. */
type Q = { id: string; q: string; opts: [string, number][]; weak: string; why: string };
const QS: Q[] = [
  { id: "pain", q: "How often does your customer feel the problem?", opts: [["Every day", 3], ["Every week", 2], ["Now and then", 1], ["I'm not sure", 0]], weak: "Talk to 5 target customers this week and ask when they last had the problem.", why: "Frequent problems are easier to sell solutions for." },
  { id: "now", q: "What do they use today?", opts: [["Nothing, they suffer", 2], ["A messy workaround", 3], ["A free tool", 1], ["A paid product they like", 0]], weak: "Name one thing you do clearly better than the free or paid option, and lead with it.", why: "Messy workarounds show demand; a good free option is the hardest competitor." },
  { id: "pay", q: "Have any customers paid or pre-paid yet?", opts: [["Yes, several", 3], ["One or two", 2], ["They said they would", 1], ["Not yet", 0]], weak: "Put a price on a page or take a small pre-order before building more.", why: "Saying yes is cheap. Paying is the real signal." },
  { id: "reach", q: "Can you reach 100 target customers this month?", opts: [["Yes, I know where they are", 3], ["Probably, through ads", 1], ["Through friends only", 1], ["I don't know how", 0]], weak: "Pick one channel (a community, a group, a marketplace) and list 100 names there.", why: "An idea you can't put in front of people can't be tested." },
  { id: "trust", q: "Why would a stranger trust you?", opts: [["Reviews or proof already", 3], ["A known name or partner", 2], ["A guarantee or free trial", 2], ["Nothing yet", 0]], weak: "Add one piece of proof: a guarantee, a free first try, or a named early customer.", why: "Trust is one of the three parts of the Founder Plus score." },
  { id: "margin", q: "After costs, do you keep money on each sale?", opts: [["Yes, most of the price", 3], ["Some", 2], ["Very little", 1], ["I haven't worked it out", 0]], weak: "Write down every cost per sale. If the margin is thin, test a higher price on the AI panel.", why: "Growth on a thin margin burns cash faster." },
];

export function IdeaChecker() {
  const [a, setA] = useState<Record<string, number>>({});
  const [idea, setIdea] = useState("");
  const answered = Object.keys(a).length;
  const score = useMemo(() => Math.round((QS.reduce((s, q) => s + (a[q.id] ?? 0), 0) / (QS.length * 3)) * 100), [a]);
  const weak = QS.filter((q) => a[q.id] !== undefined && a[q.id] <= 1);
  const label = score >= 75 ? "Strong start" : score >= 50 ? "Promising, test the gaps" : "Early: test before you spend";
  const prompt = `You are a blunt but kind startup advisor. My idea: ${idea || "[describe your idea]"}.
My answers: ${QS.map((q) => `${q.q} ${q.opts.find(([, v]) => v === a[q.id])?.[0] ?? "not answered"}`).join("; ")}.
Give me: the single biggest risk, the cheapest test I can run this week to check it (with the exact steps), and what result would mean go or stop. Keep it under 200 words.`;
  return (
    <div className="grid grid-cols-1 gap-6 [&>*]:min-w-0 lg:grid-cols-[1.2fr_1fr]">
      <div className="grid gap-6 rounded-3xl border bg-[#F7FAF9] p-6 sm:p-8">
        <label className="grid gap-2 text-sm font-medium">Your idea in one line (optional)
          <input value={idea} onChange={(e) => setIdea(e.target.value)} placeholder="Home-style thalis delivered for lunch, ₹149" className="h-11 rounded-xl border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-4 focus:ring-primary/10" /></label>
        {QS.map((q, i) => (
          <div key={q.id} className="grid gap-2">
            <p className="text-sm font-medium"><span className="text-muted-foreground">{i + 1}.</span> {q.q}</p>
            <div role="radiogroup" aria-label={q.q} className="flex flex-wrap gap-1.5">
              {q.opts.map(([l, v]) => (
                <button key={l} type="button" role="radio" aria-checked={a[q.id] === v} onClick={() => setA((x) => ({ ...x, [q.id]: v }))}
                  className={`rounded-full border px-3.5 py-2 text-sm transition-colors ${a[q.id] === v ? "border-primary bg-primary text-primary-foreground" : "bg-background hover:border-primary/40"}`}>{l}</button>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="lg:sticky lg:top-24 lg:self-start">
        <div className="rounded-3xl border bg-background p-6 shadow-xl shadow-primary/5 sm:p-8" aria-live="polite">
          <p className="text-sm text-muted-foreground">{answered} of {QS.length} answered</p>
          <div className="mt-2 flex items-end gap-3"><span className="text-6xl font-semibold tracking-tight tabular-nums text-primary">{answered ? score : "–"}</span><span className="pb-2 text-muted-foreground">/ 100</span></div>
          <p className="mt-1 text-lg font-medium">{answered ? label : "Answer the questions"}</p>
          <div className="mt-6 grid gap-3">
            {QS.filter((q) => a[q.id] !== undefined).map((q) => {
              const ok = a[q.id] >= 2;
              return (
                <div key={q.id} className="flex gap-3 text-sm">
                  {ok ? <CheckCircle2Icon className="mt-0.5 size-5 shrink-0 text-primary" /> : <CircleAlertIcon className="mt-0.5 size-5 shrink-0 text-[#D9384A]" />}
                  <div><p className="font-medium">{q.q}</p><p className="text-muted-foreground">{ok ? q.why : q.weak}</p></div>
                </div>
              );
            })}
          </div>
          {answered > 0 && (
            <div className="mt-7 grid gap-3 border-t pt-6">
              <p className="text-sm text-muted-foreground">{weak.length ? `Fix ${weak.length === 1 ? "this gap" : `these ${weak.length} gaps`} first, then test the idea on an AI panel.` : "Good answers. Now test the pitch and price on an AI panel."}</p>
              <a href={href("/builder.html")} className="inline-flex h-11 w-fit items-center rounded-xl bg-primary px-5 text-sm font-medium text-primary-foreground">Build my panel</a>
              <ClaudeButton prompt={prompt} label="Ask Claude for the cheapest test" />
            </div>
          )}
          <p className="mt-6 text-xs text-muted-foreground">This scores your own answers, not the market. It's a checklist to find gaps, not a prediction.</p>
        </div>
      </div>
    </div>
  );
}
