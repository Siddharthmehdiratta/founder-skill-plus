"use client";
import { useState } from "react";
import { CopyIcon, SparklesIcon } from "lucide-react";

/* Opens Claude with the request already written. Also copies it, in case the link can't prefill. */
export function ClaudeButton({ prompt, label = "Improve it with Claude", className = "" }: { prompt: string; label?: string; className?: string }) {
  const [copied, setCopied] = useState(false);
  const url = "https://claude.ai/new?q=" + encodeURIComponent(prompt);
  return (
    <div className={`flex flex-wrap items-center gap-2 ${className}`}>
      <a href={url} target="_blank" rel="noopener" onClick={() => { navigator.clipboard?.writeText(prompt).then(() => setCopied(true)).catch(() => {}); }}
        className="inline-flex h-11 items-center gap-2 rounded-xl bg-[#081C21] px-4 text-sm font-medium text-white hover:bg-[#081C21]/90"><SparklesIcon className="size-4" />{label}</a>
      <button type="button" onClick={() => navigator.clipboard?.writeText(prompt).then(() => { setCopied(true); setTimeout(() => setCopied(false), 2500); })}
        className="inline-flex h-11 items-center gap-2 rounded-xl border px-4 text-sm font-medium hover:bg-muted"><CopyIcon className="size-4" />{copied ? "Copied" : "Copy the request"}</button>
    </div>
  );
}
