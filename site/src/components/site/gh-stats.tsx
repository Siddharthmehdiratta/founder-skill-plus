"use client";
import { useEffect, useState } from "react";
/* Live numbers from GitHub's public API. Shows a dash if GitHub can't be reached. */
export function GhStats({ repo }: { repo: string }) {
  const [d, setD] = useState<Record<string, string>>({});
  useEffect(() => {
    fetch(`https://api.github.com/repos/${repo}`).then((r) => (r.ok ? r.json() : Promise.reject())).then((j) => setD({
      stars: j.stargazers_count.toLocaleString("en-IN"), forks: j.forks_count.toLocaleString("en-IN"), issues: j.open_issues_count.toLocaleString("en-IN"),
      updated: new Date(j.pushed_at).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }),
      license: j.license?.spdx_id && j.license.spdx_id !== "NOASSERTION" ? j.license.spdx_id : "MIT",
    })).catch(() => setD({ stars: "–", forks: "–", issues: "–", updated: "–", license: "MIT" }));
  }, [repo]);
  return (
    <div className="grid grid-cols-2 gap-px overflow-hidden rounded-3xl border bg-border sm:grid-cols-5">
      {[["stars", "Stars"], ["forks", "Copies (forks)"], ["issues", "Open issues"], ["updated", "Last update"], ["license", "Licence"]].map(([k, l]) => (
        <div key={k} className="bg-background p-6"><p className="text-2xl font-semibold tracking-tight tabular-nums">{d[k] ?? "…"}</p><p className="mt-1 text-sm text-muted-foreground">{l}</p></div>
      ))}
    </div>
  );
}
