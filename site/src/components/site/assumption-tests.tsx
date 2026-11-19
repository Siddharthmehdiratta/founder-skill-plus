"use client";
import { useEffect, useMemo, useState } from "react";
import { ClaudeButton } from "./claude-button";
import { IDEA_QS, type IdeaAnswers } from "@/lib/idea";
import { planTests, nextStep, loadResults, saveResults, type Test, type Result, type Outcome } from "@/lib/tests";

const card = "rounded-2xl border bg-background p-5";
const OUTCOME: [Outcome, string][] = [["pass", "It held"], ["fail", "It did not"], ["unclear", "Still unclear"]];
const TONE: Record<Outcome, string> = { pass: "border-foreground", fail: "border-foreground bg-muted", unclear: "bg-muted" };

function Row({ t, r, n, onSet, onClear }: { t: Test; r?: Result; n: number; onSet: (o: Outcome) => void; onClear: () => void }) {
  return (
    <li className={`${card} ${r ? TONE[r.outcome] : ""}`}>
      <div className="flex items-baseline gap-3">
        <span className="text-sm tabular-nums text-muted-foreground">{n}</span>
        <h3 className="text-lg font-medium">{t.assume}</h3>
      </div>
      <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
        <div className="sm:col-span-2"><dt className="text-muted-foreground">How to find out this week</dt><dd className="mt-1">{t.how}</dd></div>
        <div><dt className="text-muted-foreground">Counts as a pass</dt><dd className="mt-1">{t.pass}</dd></div>
        <div><dt className="text-muted-foreground">Counts as a fail</dt><dd className="mt-1">{t.fail}</dd></div>
        <div className="sm:col-span-2"><dt className="text-muted-foreground">Cost</dt><dd className="mt-1">{t.cost}</dd></div>
      </dl>
      <div className="mt-4 flex flex-wrap items-center gap-2">
        {OUTCOME.map(([o, label]) => (
          <button key={o} type="button" onClick={() => onSet(o)}
            className={`inline-flex min-h-11 items-center rounded-full border px-4 text-sm transition-colors ${r?.outcome === o ? "border-foreground bg-foreground text-background" : "bg-background hover:border-foreground/40"}`}>
            {label}
          </button>
        ))}
        {r && <button type="button" onClick={onClear} className="min-h-11 px-3 text-sm text-muted-foreground underline underline-offset-4">Clear</button>}
      </div>
    </li>
  );
}

export function AssumptionTests() {
  const [answers, setAnswers] = useState<IdeaAnswers | null>(null);
  const [results, setResults] = useState<Record<string, Result>>({});
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try { const s = JSON.parse(localStorage.getItem("fp-idea") || "null"); if (s && s.a && typeof s.a === "object") setAnswers(s.a); } catch {}
    setResults(loadResults()); setReady(true);
  }, []);
  useEffect(() => { if (ready) saveResults(results); }, [results, ready]);

  const blank: IdeaAnswers = useMemo(() => Object.fromEntries(IDEA_QS.map((q) => [q.id, 0])), []);
  const tests = useMemo(() => planTests(answers || blank), [answers, blank]);
  const step = useMemo(() => nextStep(tests, results), [tests, results]);

  if (!ready) return <div className="h-40" aria-hidden />;

  const set = (id: string, outcome: Outcome) => setResults((r) => ({ ...r, [id]: { id, outcome, note: "" } }));
  const clear = (id: string) => setResults((r) => { const n = { ...r }; delete n[id]; return n; });

  return (
    <div className="mx-auto max-w-4xl">
      <div className={`${card} mb-8`}>
        <h2 className="text-lg font-medium">Why one at a time</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Start five tests at once and a good month tells you nothing about which assumption was the real one.
          Run the riskiest first, because the riskiest is what kills the idea, and finding that out in week one
          costs a week instead of a year. Decide what counts as a pass before you start, or you will read the
          result the way you want to.
        </p>
        {!answers && (
          <p className="mt-3 rounded-xl bg-muted px-4 py-3 text-sm">
            You have not filled in the Idea Checker in this browser yet, so every assumption below is listed as
            untested. Fill it in and this page drops the ones you already have evidence for.
          </p>
        )}
      </div>

      <div className={`${card} mb-8 border-foreground`}>
        <h2 className="text-sm uppercase tracking-wide text-muted-foreground">Do this next</h2>
        <p className="mt-2 text-lg">{step.line}</p>
        {step.test && <p className="mt-3 text-sm text-muted-foreground">{step.test.how}</p>}
      </div>

      {!!tests.length && (
        <>
          <h2 className="mb-4 text-xl font-medium">Riskiest first</h2>
          <ul className="grid gap-5">
            {tests.map((t, i) => <Row key={t.id} t={t} n={i + 1} r={results[t.id]} onSet={(o) => set(t.id, o)} onClear={() => clear(t.id)} />)}
          </ul>
        </>
      )}

      <div className={`${card} mt-10`}>
        <h2 className="text-lg font-medium">Run it with Claude</h2>
        <p className="mt-2 text-sm text-muted-foreground">Claude can write the messages, the landing page and the questions for whichever test is next.</p>
        <div className="mt-4"><ClaudeButton prompt={prompt(step)} label="Set up the next test" /></div>
      </div>
    </div>
  );
}

function prompt(step: ReturnType<typeof nextStep>) {
  if (!step.test) return "Every assumption behind my business idea has now been tested and held. Help me build the smallest version I can sell, and tell me what you would check first after launch.";
  const t = step.test;
  return `I am testing one assumption about my business idea before I build anything.\n\nAssumption: ${t.assume}\nHow I plan to test it: ${t.how}\nCounts as a pass: ${t.pass}\nCounts as a fail: ${t.fail}\n\nWrite exactly what I need to run this: the messages or the page copy, the questions to ask, and nothing else. Do not change the pass number to make it easier to hit, and tell me if you think the test does not actually measure the assumption.`;
}
