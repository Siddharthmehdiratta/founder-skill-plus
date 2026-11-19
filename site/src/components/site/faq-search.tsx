"use client";
import { useEffect, useMemo, useState } from "react";
import { SearchIcon } from "lucide-react";
import { FAQS } from "@/lib/faqs";

const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9 ]/g, " ");

export function FaqSearch() {
  const [q, setQ] = useState("");
  useEffect(() => { const p = new URLSearchParams(location.search).get("q"); if (p) setQ(p); }, []);
  const words = norm(q).split(/\s+/).filter(Boolean);
  const groups = useMemo(() => FAQS.map(([g, items]) => [g, items.filter(([a, b]) => words.every((w) => norm(a + " " + b).includes(w)))] as const).filter(([, i]) => i.length), [q]);
  return (
    <div>
      <label className="relative block">
        <span className="sr-only">Search the questions</span>
        <SearchIcon aria-hidden className="absolute top-1/2 left-4 size-5 -translate-y-1/2 text-muted-foreground" />
        <input id="q" type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search, for example: price" className="h-14 w-full rounded-2xl border bg-background pr-4 pl-12 text-base shadow-sm outline-none focus:border-primary focus:ring-4 focus:ring-primary/10" />
      </label>
      {!q && <nav aria-label="Topics" className="mt-5 flex flex-wrap gap-2">{FAQS.map(([g], i) => <a key={g} href={`#g${i}`} className="rounded-full border px-3 py-1.5 text-sm hover:bg-muted">{g}</a>)}</nav>}
      {groups.length === 0 && <p className="mt-8 text-muted-foreground">No question matches that. Try another word, or ask us below.</p>}
      <div className="mt-10 grid gap-12">
        {groups.map(([g, items]) => (
          <section key={g} className="faq-group">
            <h2 id={`g${FAQS.findIndex(([n]) => n === g)}`} className="scroll-mt-24 text-xl font-semibold tracking-tight">{g}</h2>
            <div className="mt-4 divide-y rounded-2xl border">
              {items.map(([qq, a]) => (
                <details key={qq} open={words.length > 0} className="group p-5">
                  <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-medium">{qq}<span aria-hidden className="text-muted-foreground transition-transform group-open:rotate-45">+</span></summary>
                  <p className="mt-3 text-muted-foreground">{a}</p>
                </details>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
