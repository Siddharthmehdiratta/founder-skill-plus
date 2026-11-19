import type { Metadata } from "next";
import { BugIcon, MessageCircleQuestionIcon, MessageSquareHeartIcon } from "lucide-react";
import { PageShell } from "@/components/site/shell";
import { IssueForm } from "@/components/site/issue-form";
import { GithubMark } from "@/components/site/brand-icons";
import { SITE } from "@/lib/site";

export const metadata: Metadata = { title: "Contact", description: "Ask a question, report a problem or give feedback." };
const PARTS = ["Home page", "Panel builder", "Running it in Claude", "The report", "Review analysis", "Beginner's guide", "Something else"];

export default function Page() {
  return (
    <PageShell group="" kicker="Contact" title="Talk to us" lead="Questions, problems and ideas all go through GitHub, in public, so the answer helps the next person too. You'll get an email from GitHub when someone replies.">
      <div className="mx-auto max-w-7xl px-5 py-16 lg:px-8">
        <div className="grid gap-4 md:grid-cols-3">
          {[[MessageCircleQuestionIcon, "Ask a question", "Post it in our public Q&A. Usually answered within a few days.", SITE.ask, "Ask on GitHub"],
            [BugIcon, "Report a problem", "Something broke or looks wrong? Tell us exactly what happened.", "#report", "Use the form"],
            [MessageSquareHeartIcon, "Give feedback", "What should we keep, and what should change? Be blunt.", "#feedback", "Use the form"]].map(([I, t, d, h, c]) => {
            const C = I as typeof BugIcon;
            return <a key={t as string} href={h as string} className="group rounded-3xl border p-7 transition-colors hover:border-primary/30 hover:bg-[#F3FAF7]"><C className="size-5 text-primary" /><h2 className="mt-4 text-lg font-semibold tracking-tight">{t as string}</h2><p className="mt-2 text-sm text-muted-foreground">{d as string}</p><p className="mt-5 text-sm font-medium text-primary">{c as string}</p></a>;
          })}
        </div>
        <div className="mt-16 grid grid-cols-1 gap-10 [&>*]:min-w-0 lg:grid-cols-2">
          <section id="report" className="scroll-mt-24 rounded-3xl border p-7 sm:p-9">
            <h2 className="text-2xl font-semibold tracking-tight">Report a problem</h2>
            <p className="mt-2 mb-7 text-sm text-muted-foreground">Please don't include passwords or private numbers.</p>
            <IssueForm kind="Problem" button="Send report on GitHub" fields={[
              { name: "title", label: "What went wrong, in one line?", req: true, hint: "For example: Copy the message for Claude does nothing" },
              { name: "part", label: "Which part?", kind: "select", opts: PARTS },
              { name: "steps", label: "What did you do?", kind: "area", hint: "The buttons you pressed, in order" },
              { name: "happened", label: "What happened, and what did you expect?", kind: "area" },
              { name: "device", label: "Device and browser", hint: "For example: Android phone, Chrome" },
            ]} />
          </section>
          <section id="feedback" className="scroll-mt-24 rounded-3xl border p-7 sm:p-9">
            <h2 className="text-2xl font-semibold tracking-tight">Give feedback</h2>
            <p className="mt-2 mb-7 text-sm text-muted-foreground">Two minutes. Every message is read.</p>
            <IssueForm kind="Feedback" button="Send feedback on GitHub" fields={[
              { name: "title", label: "Your feedback in one line", req: true },
              { name: "part", label: "Which part did you use?", kind: "select", opts: PARTS },
              { name: "ease", label: "How easy was it, from 1 to 5?", kind: "select", opts: ["1, very hard", "2", "3", "4", "5, very easy"] },
              { name: "good", label: "What worked well?", kind: "area" },
              { name: "change", label: "What should change?", kind: "area" },
            ]} />
          </section>
        </div>
        <p className="mt-12 flex items-center gap-2 text-sm text-muted-foreground"><GithubMark className="size-4" />Prefer to browse? See <a className="font-medium text-primary" href={`${SITE.repo}/discussions`}>all questions</a> and <a className="font-medium text-primary" href={`${SITE.repo}/issues`}>all reported problems</a>.</p>
      </div>
    </PageShell>
  );
}
