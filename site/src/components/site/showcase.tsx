"use client";
import { useState } from "react";
import { href } from "@/lib/site";

/* The product shown in its own screens: pick a part on the left, see the real screen on the right. */
export type ShowItem = { title: string; text: string; shot: string; alt: string };
export function Showcase({ items, label }: { items: ShowItem[]; label: string }) {
  const [i, setI] = useState(0);
  const cur = items[i];
  const onKey = (e: React.KeyboardEvent) => {
    const d = e.key === "ArrowDown" || e.key === "ArrowRight" ? 1 : e.key === "ArrowUp" || e.key === "ArrowLeft" ? -1 : 0;
    if (!d) return; e.preventDefault(); const n = (i + d + items.length) % items.length; setI(n);
    (document.getElementById(`show-tab-${n}`) as HTMLElement | null)?.focus();
  };
  return (
    <div className="grid grid-cols-1 gap-8 [&>*]:min-w-0 lg:grid-cols-[22rem_1fr] lg:gap-12">
      <div role="tablist" aria-label={label} aria-orientation="vertical" className="grid content-start" onKeyDown={onKey}>
        {items.map((it, n) => (
          <button key={it.title} id={`show-tab-${n}`} type="button" role="tab" aria-selected={n === i} aria-controls="show-panel" tabIndex={n === i ? 0 : -1} onClick={() => setI(n)}
            className={`show-tab border-t py-5 text-left ${n === i ? "border-foreground" : "border-foreground/15 text-muted-foreground"}`}>
            <span className={`block text-xl font-semibold tracking-tight ${n === i ? "text-foreground" : ""}`}>{it.title}</span>
            {n === i && <span className="mt-2 block text-muted-foreground">{it.text}</span>}
          </button>
        ))}
      </div>
      <div id="show-panel" role="tabpanel" aria-labelledby={`show-tab-${i}`} className="show-frame">
        <picture key={cur.shot}>
          <source type="image/webp" srcSet={href(cur.shot.replace(/\.png$/, ".webp"))} />
          <img src={href(cur.shot)} alt={cur.alt} loading="lazy" decoding="async" className="show-img" />
        </picture>
      </div>
    </div>
  );
}
