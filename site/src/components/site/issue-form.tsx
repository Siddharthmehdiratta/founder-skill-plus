"use client";
import { useState } from "react";
import { SITE } from "@/lib/site";

type F = { name: string; label: string; kind?: "text" | "area" | "select"; opts?: string[]; req?: boolean; hint?: string };
/* Opens a GitHub issue with the answers filled in. Nothing is sent until the person presses Create on GitHub. */
export function IssueForm({ kind, fields, button }: { kind: string; fields: F[]; button: string }) {
  const [sent, setSent] = useState(false);
  const field = "w-full rounded-xl border bg-background px-3.5 py-3 text-base outline-none focus:border-primary focus:ring-4 focus:ring-primary/10";
  return (
    <form className="grid gap-5" onSubmit={(e) => {
      e.preventDefault();
      const d = new FormData(e.currentTarget);
      const body = fields.filter((f) => f.name !== "title" && String(d.get(f.name) || "").trim()).map((f) => `**${f.label}**\n${d.get(f.name)}`).join("\n\n") + `\n\n_Sent from the website on ${new Date().toDateString()}_`;
      const url = `${SITE.issue}?` + new URLSearchParams({ title: `${kind}: ${String(d.get("title") || "").trim()}`, body }).toString();
      const w = window.open(url, "_blank", "noopener"); if (!w) location.href = url; setSent(true);
    }}>
      {fields.map((f) => (
        <div key={f.name} className="grid gap-1.5">
          <label htmlFor={`${kind}-${f.name}`} className="text-sm font-medium">{f.label}{f.req && <span className="text-primary"> *</span>}</label>
          {f.hint && <p className="text-xs text-muted-foreground">{f.hint}</p>}
          {f.kind === "area" ? <textarea id={`${kind}-${f.name}`} name={f.name} rows={4} required={f.req} className={field} />
            : f.kind === "select" ? <select id={`${kind}-${f.name}`} name={f.name} className={field}><option value="">Choose one</option>{f.opts!.map((o) => <option key={o}>{o}</option>)}</select>
            : <input id={`${kind}-${f.name}`} name={f.name} required={f.req} className={field} />}
        </div>
      ))}
      <button type="submit" className="inline-flex h-12 items-center justify-center rounded-xl bg-primary px-6 font-medium text-primary-foreground shadow-lg shadow-primary/20 hover:bg-primary/90">{button}</button>
      <p className="text-xs text-muted-foreground">This opens GitHub in a new tab with your words filled in. Press Create there to send it. A free GitHub account is needed. Nothing is sent until you press it.</p>
      {sent && <p role="status" className="rounded-xl bg-[#ECF8F3] p-3 text-sm text-[#0B7A5F]">GitHub is open in a new tab. Press Create there to send. Thank you.</p>}
    </form>
  );
}
