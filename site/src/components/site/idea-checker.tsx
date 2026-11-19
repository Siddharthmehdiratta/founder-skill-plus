"use client";
import { useMemo, useState } from "react";
import { CheckCircle2Icon, CircleAlertIcon, PencilLineIcon } from "lucide-react";
import { href } from "@/lib/site";
import { ClaudeButton } from "./claude-button";
import { IDEA_QS, scoreIdea, type IdeaAnswers } from "@/lib/idea";

const pill = (on: boolean) => `inline-flex min-h-11 items-center rounded-full border px-4 py-2 text-left text-sm transition-colors ${on ? "border-primary bg-primary text-primary-foreground" : "bg-background hover:border-primary/40"}`;
const input = "h-12 w-full rounded-xl border bg-background px-3 text-base outline-none focus:border-primary";

export function IdeaChecker() {
  const [a, setA] = useState<IdeaAnswers>({});
  const [own, setOwn] = useState<Record<string, string>>({});
  const [idea, setIdea] = useState("");
  const [picked, setPicked] = useState<Record<string, number>>({});
  const r = useMemo(() => scoreIdea(a), [a]);
  const said = (id: string) => { const q = IDEA_QS.find((x) => x.id === id)!; return a[id] === "other" ? `(my own words) ${own[id] || ""}` : picked[id] !== undefined ? q.opts[picked[id]][0] : "not answered"; };
  const prompt = `You are a blunt but kind startup advisor. Never invent numbers.
My idea: ${idea || "[describe your idea]"}.
My answers:
${IDEA_QS.map((q) => `- ${q.q} ${said(q.id)}`).join("\n")}
Give me: 1) the single biggest risk, 2) the cheapest test I can run this week to check it, with exact steps, 3) what result would mean go or stop, 4) anything in my own words that changes your view. Keep it under 220 words.`;
  return (
    <div className="grid grid-cols-1 gap-6 [&>*]:min-w-0 lg:grid-cols-[1.2fr_1fr]">
      <form className="grid gap-7 rounded-3xl border bg-[#F7FAF9] p-6 sm:p-8" onSubmit={(e) => e.preventDefault()}>
        <label className="grid gap-2 text-base font-semibold tracking-tight">Your idea in one line
          <input value={idea} onChange={(e) => setIdea(e.target.value)} placeholder="Home-style thalis delivered for lunch, ₹149" className={`${input} font-normal`} autoComplete="off" /></label>
        {IDEA_QS.map((q, i) => (
          <fieldset key={q.id} className="grid gap-3">
            <legend className="text-base font-semibold tracking-tight"><span className="text-muted-foreground tabular-nums">{i + 1}.</span> {q.q}</legend>
            <div role="radiogroup" aria-label={q.q} className="flex flex-wrap gap-1.5">
              {q.opts.map(([l, v], n) => { const on = a[q.id] === v && picked[q.id] === n; return (
                <button key={l} type="button" role="radio" aria-checked={on} onClick={() => { setA((x) => ({ ...x, [q.id]: v })); setPicked((x) => ({ ...x, [q.id]: n })); }} className={pill(on)}>{l}</button>); })}
              <button type="button" role="radio" aria-checked={a[q.id] === "other"} onClick={() => setA((x) => ({ ...x, [q.id]: "other" }))} className={pill(a[q.id] === "other")}>Other</button>
            </div>
            {a[q.id] === "other" && <label className="grid gap-1.5 text-sm text-muted-foreground">Write your own answer<input className={input} value={own[q.id] || ""} onChange={(e) => setOwn((x) => ({ ...x, [q.id]: e.target.value }))} autoFocus /></label>}
          </fieldset>
        ))}
      </form>
      <div className="lg:sticky lg:top-24 lg:self-start">
        <div className="rounded-3xl border bg-background p-6 sm:p-8" aria-live="polite">
          <p className="text-sm text-muted-foreground">{r.answered} of {IDEA_QS.length} answered{r.own.length ? `, ${r.own.length} in your own words` : ""}</p>
          <div className="mt-2 flex items-end gap-3"><span className="font-display text-7xl leading-none font-bold tracking-tight tabular-nums text-primary">{r.score ?? "–"}</span><span className="pb-1 text-muted-foreground">/ 100</span></div>
          <p className="mt-2 text-lg font-medium">{r.label}</p>
          <div className="mt-6 grid gap-4">
            {IDEA_QS.filter((q) => a[q.id] !== undefined).map((q) => {
              const mine = a[q.id] === "other"; const ok = !mine && (a[q.id] as number) >= 2;
              return (
                <div key={q.id} className="flex gap-3 text-sm">
                  {mine ? <PencilLineIcon aria-hidden className="mt-0.5 size-5 shrink-0 text-muted-foreground" /> : ok ? <CheckCircle2Icon aria-hidden className="mt-0.5 size-5 shrink-0 text-primary" /> : <CircleAlertIcon aria-hidden className="mt-0.5 size-5 shrink-0 text-[#B4232F]" />}
                  <div><p className="font-medium">{q.q}</p><p className="text-muted-foreground">{mine ? (own[q.id] ? `You wrote: "${own[q.id]}". Not scored. Claude will read it.` : "Write your answer on the left.") : ok ? q.why : q.weak}</p></div>
                </div>
              );
            })}
          </div>
          {r.answered > 0 && (
            <div className="mt-7 grid gap-3 border-t pt-6">
              <p className="text-sm text-muted-foreground">{r.weak.length ? `Fix ${r.weak.length === 1 ? "this gap" : `these ${r.weak.length} gaps`} first, then test the idea on an AI panel.` : "No weak answers so far. Now test the pitch and price on an AI panel."}</p>
              <a href={href("/builder.html")} data-slot="button" className="inline-flex h-12 w-fit items-center rounded-xl bg-primary px-5 font-medium text-primary-foreground">Build my panel</a>
              <ClaudeButton prompt={prompt} label="Ask Claude for the cheapest test" />
            </div>
          )}
          <p className="mt-6 text-xs text-muted-foreground">This scores the answers you pick, not the market. Answers in your own words are not scored; Claude reads them. It is a checklist to find gaps, not a prediction.</p>
        </div>
      </div>
    </div>
  );
}
