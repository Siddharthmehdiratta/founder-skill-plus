import type { Metadata } from "next";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { PageShell } from "@/components/site/shell";
import { Icon } from "@/components/site/icon";
import { FAQS } from "@/lib/faqs";
import { SITE, href } from "@/lib/site";

export const metadata: Metadata = { title: "Help centre", description: "Every way to get help: beginner's guide, FAQ, ask a question, report a problem, give feedback." };

const CARDS = [
  ["/how-to-use.html", "BookOpen", "Beginner's guide", "Your first panel, step by step"], ["/faq/", "Search", "FAQ", "Quick answers, searchable"],
  [SITE.ask, "MessageCircleQuestion", "Ask a question", "Post it in our public Q&A"], ["/contact/#report", "Bug", "Report a problem", "Something broke or looks wrong"],
  ["/contact/#feedback", "MessageSquareHeart", "Give feedback", "Tell us what to keep or change"], ["/open-source/", "Github", "Open source", "Code, licence and how to help"],
  ["/example-report.html", "Globe", "Sample report", "See exactly what you'll get"], ["/how-it-works/", "Workflow", "How it works", "The panel, the score, the limits"],
];
const POPULAR = [FAQS[0][1][1], FAQS[1][1][0], FAQS[0][1][2], FAQS[3][1][0]];

export default function Page() {
  return (
    <PageShell group="Help" kicker="Help centre" title="How can we help?" lead="Pick what you need. Everything is free and answered in public, so the next person learns too.">
      <div className="mx-auto max-w-7xl px-5 py-16 lg:px-8">
        <form action={href("/faq/")} method="get" role="search" className="mx-auto flex max-w-2xl gap-2">
          <label htmlFor="hq" className="sr-only">Search the questions</label>
          <input id="hq" name="q" type="search" placeholder="Search answers, for example: price" className="h-14 min-w-0 flex-1 rounded-2xl border bg-background px-5 text-base shadow-sm outline-none focus:border-primary focus:ring-4 focus:ring-primary/10" />
          <button className="h-14 shrink-0 rounded-2xl bg-primary px-5 font-medium text-primary-foreground">Search</button>
        </form>
        <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {CARDS.map(([h, ic, t, d]) => (
            <a key={t} href={href(h)} className="rounded-3xl border p-6 transition-all hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5">
              <span className="grid size-10 place-items-center rounded-xl border text-primary"><Icon name={ic} className="size-5" /></span>
              <h2 className="mt-5 font-semibold tracking-tight">{t}</h2><p className="mt-1 text-sm text-muted-foreground">{d}</p>
            </a>
          ))}
        </div>
        <div className="mt-20 grid grid-cols-1 gap-12 [&>*]:min-w-0 lg:grid-cols-[1.4fr_1fr]">
          <div>
            <h2 className="text-2xl font-semibold tracking-tight">Popular questions</h2>
            <Accordion type="single" collapsible className="mt-4">{POPULAR.map(([q, a]) => <AccordionItem key={q} value={q}><AccordionTrigger className="py-5 text-base">{q}</AccordionTrigger><AccordionContent className="text-muted-foreground">{a}</AccordionContent></AccordionItem>)}</Accordion>
            <a href={href("/faq/")} className="mt-6 inline-block text-sm font-medium text-primary">See all questions</a>
          </div>
          <div className="h-fit rounded-3xl bg-[#F7FAF9] p-8 ring-1 ring-border">
            <h3 className="font-semibold tracking-tight">How replies work</h3>
            <ol className="mt-5 grid gap-4 text-sm">{[["You post", "a question, problem or idea on GitHub."], ["We reply there,", "in public, usually within a few days."], ["You get an email", "from GitHub when someone answers."]].map(([b, t], i) => <li key={b} className="flex gap-3"><span className="grid size-6 shrink-0 place-items-center rounded-full bg-primary text-xs text-primary-foreground">{i + 1}</span><span><b className="font-medium">{b}</b> <span className="text-muted-foreground">{t}</span></span></li>)}</ol>
            <p className="mt-6 text-xs text-muted-foreground">A free GitHub account is needed to post.</p>
          </div>
        </div>
      </div>
    </PageShell>
  );
}
