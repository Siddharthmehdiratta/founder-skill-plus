import { Showcase } from "@/components/site/showcase";
import { ArrowRightIcon, CheckIcon, ClipboardListIcon, GaugeIcon, GlobeIcon, MessageSquareTextIcon, ShieldCheckIcon, TargetIcon, UsersIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { SiteHeader } from "@/components/site/header";
import { SiteFooter } from "@/components/site/footer";
import { Shot } from "@/components/site/shell";
import { SITE, href } from "@/lib/site";
import { IdeaChecker } from "@/components/site/idea-checker";
import { Icon } from "@/components/site/icon";

const QUOTES = [
  ["Harleen, 38, India", "\"$8 a month is about ₹700. Free blockers already exist.\"", "Not yet"],
  ["Kavya, 18, India", "\"Agar ₹100-150 ho aur UPI se pay ho sake, toh use karungi.\"", "Not yet"],
  ["Amanda, 43, USA", "\"I'd need a friend to tell me it worked through a deadline.\"", "Maybe"],
];

const FAQ = [
  ["Is it really free?", "Yes. Founder Plus is open source under the MIT licence. The quick test runs in the Claude app you already use, including the free plan."],
  ["How accurate is it?", "It's research, not a forecast. AI customers lean agreeable, so read the buy rate as a ceiling. The value is in the reasons, doubts and questions, which you then check with real people."],
  ["Do I need to install anything?", "No. Build your panel on the website, press Copy the message for Claude, and paste it into the Claude app or claude.ai."],
  ["Where does my business idea go?", "Only where you paste it: your own Claude chat. The builder runs in your browser and stores nothing."],
];

export default function Home() {
  return (
    <>
      <SiteHeader />
      <main id="main" className="overflow-x-clip">
        {/* ---------------- hero ---------------- */}
        <section className="overflow-hidden border-b">
          <div className="mx-auto max-w-7xl px-5 pt-14 sm:pt-20 lg:px-8 lg:pt-24">
            <h1 className="hero-title rise">Test it before you build it.</h1>
            <div className="mt-8 flex flex-col gap-8 lg:mt-10 lg:flex-row lg:items-end lg:justify-between">
              <p className="rise max-w-xl text-lg leading-relaxed text-muted-foreground text-pretty sm:text-xl" style={{ "--i": 1 } as React.CSSProperties}>
                A panel of AI customers reacts to your business idea in their own words. You get a score, what to fix, and what to say.
              </p>
              <div className="rise shrink-0" style={{ "--i": 2 } as React.CSSProperties}>
                <div className="flex flex-col gap-3 sm:flex-row">
                  <Button size="lg" className="h-12 rounded-xl px-6 text-base" asChild>
                    <a href={href(SITE.app)}>Build my panel<ArrowRightIcon /></a>
                  </Button>
                  <Button size="lg" variant="outline" className="h-12 rounded-xl px-6 text-base" asChild>
                    <a href={href("/sample/")}>See a sample report</a>
                  </Button>
                </div>
                <ul className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-sm text-muted-foreground">
                  {["Free", "No sign-up", "Runs in Claude"].map((t) => <li key={t} className="flex items-center gap-1.5"><CheckIcon className="size-4 text-primary" />{t}</li>)}
                </ul>
              </div>
            </div>
          </div>
          <div className="mx-auto mt-14 max-w-7xl px-5 lg:mt-20 lg:px-8">
            <a href={href("/sample/")} className="hero-frame rise" style={{ "--i": 3 } as React.CSSProperties}>
              <span className="hero-frame-bar" aria-hidden><i /><i /><i /><b>Sample report</b></span>
              <picture>
                <source media="(max-width: 640px)" type="image/webp" srcSet={href("/shots/report-phone.webp")} width={780} height={1688} />
                <source type="image/webp" srcSet={href("/shots/report.webp")} width={2560} height={1600} />
                <img src={href("/shots/report.png")} width={2560} height={1600} alt="A sample report: 10 AI customers in four countries give a study app a score of 34 out of 100." loading="eager" fetchPriority="high" decoding="async" className="block h-auto w-full" />
              </picture>
            </a>
          </div>
        </section>

        {/* ---------------- free tools ---------------- */}
        <section className="mx-auto max-w-7xl px-5 py-20 sm:py-28 lg:px-8">
          <h2 className="text-3xl font-semibold tracking-[-0.03em] sm:text-5xl">Four free tools.</h2>
          <div className="mt-10 grid gap-x-10 sm:grid-cols-2 lg:grid-cols-4">
            {[["/builder.html", "Panel builder", "AI customers react to your offer.", "Users"], ["/idea-checker/", "Idea Checker", "Find the gaps in three minutes.", "ScanSearch"], ["/claude/", "Claude helpers", "Pitch, objections and pricing in one click.", "Sparkles"], ["/feedback.html#pim", "Review analysis", "Turn real reviews into a fix list.", "ClipboardList"]].map(([h, t, d]) => (
              <a key={t} href={href(h)} className="tool-row group">
                <span className="flex items-center justify-between text-xl font-semibold tracking-tight">{t}<ArrowRightIcon className="size-5 text-muted-foreground transition-transform duration-200 group-hover:translate-x-1 group-hover:text-foreground" /></span>
                <span className="mt-2 block text-muted-foreground">{d}</span>
              </a>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
          <div className="max-w-2xl">
            <h2 className="mt-3 text-3xl font-semibold tracking-[-0.03em] sm:text-5xl">Is your idea ready to test?</h2>
            <p className="mt-4 text-muted-foreground">Ten quick questions, or write your own answers. Each weak answer comes with the cheapest way to fix it.</p>
          </div>
          <div className="mt-12"><IdeaChecker /></div>
        </section>

        {/* ---------------- voices ---------------- */}
        <section className="border-y bg-[#F7FAF9]">
          <div className="mx-auto max-w-7xl px-5 py-16 lg:px-8">
            <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
              <div>
                <h2 className="text-3xl font-semibold tracking-[-0.03em] sm:text-4xl">Reactions in their own words</h2>
                <p className="mt-3 max-w-xl text-muted-foreground">From the sample report: AI customers in India and the USA react to an $8 a month study app.</p>
              </div>
              <a href={href(SITE.sample)} className="inline-flex items-center gap-1.5 text-sm font-medium text-primary">Read every answer<ArrowRightIcon className="size-4" /></a>
            </div>
            <div className="mt-10 grid gap-4 md:grid-cols-3">
              {QUOTES.map(([who, q, v]) => (
                <figure key={who} className="flex flex-col rounded-2xl border bg-background p-6 shadow-xs">
                  <blockquote className="flex-1 text-[1.05rem] leading-relaxed">{q}</blockquote>
                  <figcaption className="mt-5 flex items-center justify-between text-sm"><span className="text-muted-foreground">{who} <span className="text-xs">(AI customer)</span></span><span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${v === "Maybe" ? "bg-[#FFF6E0] text-[#8A5A00]" : "bg-[#FDECEE] text-[#B42336]"}`}>{v}</span></figcaption>
                </figure>
              ))}
            </div>
          </div>
        </section>

        {/* ---------------- inside the product ---------------- */}
        <section className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
          <h2 className="max-w-3xl text-3xl font-semibold tracking-[-0.03em] sm:text-5xl">Customer research in an afternoon, not a month.</h2>
          <div className="mt-12">
            <Showcase label="Parts of the report" items={[
              { title: "Customers you choose", text: "Markets, cities, incomes, ages, genders, buying habits and well-studied biases. Every choice is a dropdown, built on published facts.", shot: "/shots/builder.png", alt: "The panel builder: pick markets, cities, incomes and ages from dropdowns." },
              { title: "A score out of 100", text: "Demand, price fit and trust, so you can compare two versions of your idea on the same panel.", shot: "/shots/tab-summary.png", alt: "The score and summary tab of a sample report." },
              { title: "What to fix first", text: "The top reasons people pass, each with a practical fix, and the group to sell to first.", shot: "/shots/tab-next.png", alt: "The what to do next tab: the top reasons buyers pass, each with a fix." },
              { title: "A sales kit you can use", text: "Answers to the questions buyers ask most, price ranges they'd accept, and replies to their doubts, ready for your page or pitch.", shot: "/shots/tab-questions.png", alt: "The questions to answer tab: what buyers ask most, with replies." },
            ]} />
          </div>

        </section>

        {/* ---------------- how it works ---------------- */}
        <section className="border-y bg-[#F7FAF9]">
          <div className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
            <div>
              <h2 className="mt-3 text-3xl font-semibold tracking-[-0.03em] sm:text-5xl">Three steps. About ten minutes.</h2>
              <ol className="mt-12 grid gap-x-10 gap-y-8 md:grid-cols-3">
                {[["Pick your customers", "Start from your industry, or build your panel from scratch. Every choice is a dropdown."],
                  ["Copy one message", "Press Copy the message for Claude, paste it into the Claude app or claude.ai, and send it."],
                  ["Read your score", "Claude plays every customer, then writes your score, the reasons, what to fix and your sales replies."]].map(([t, d], i) => (
                  <li key={t} className="border-t border-foreground/15 pt-6">
                    <span aria-hidden className="font-display block text-7xl leading-none font-bold tracking-[-0.05em] text-foreground/15 tabular-nums">{i + 1}</span>
                    <h3 className="mt-5 text-xl font-semibold tracking-tight">{t}</h3><p className="mt-2 text-muted-foreground">{d}</p>
                  </li>
                ))}
              </ol>
              <div className="mt-10 flex flex-wrap gap-3">
                <Button className="h-11 rounded-xl px-5" asChild><a href={href(SITE.app)}>Build my panel</a></Button>
                <Button variant="ghost" className="h-11 rounded-xl px-5" asChild><a href={href("/how-to-use.html")}>Read the beginner's guide</a></Button>
              </div>
            </div>
          </div>
        </section>

        {/* ---------------- honest limits ---------------- */}
        <section className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
          <div className="max-w-2xl">
            <h2 className="mt-3 text-3xl font-semibold tracking-[-0.03em] sm:text-5xl">What AI customers can, and can't, tell you.</h2>
          </div>
          <div className="mt-12 grid gap-px overflow-hidden rounded-3xl border bg-border md:grid-cols-3">
            {[["Good for", "Finding objections, questions and price ranges early, and picking between two pitches before you spend."],
              ["Read as a ceiling", "AI customers lean agreeable, so treat the buy rate as the best case. The reasons and doubts matter more than the number."],
              ["Not a replacement", "Confirm with real people next: a waitlist, a pre-sale, or a price on a page. The report tells you what to test."]].map(([t, d]) => (
              <div key={t} className="bg-background p-8"><p className="text-xl font-semibold tracking-tight">{t}</p><p className="mt-3 text-sm leading-relaxed text-muted-foreground">{d}</p></div>
            ))}
          </div>
        </section>

        {/* ---------------- FAQ ---------------- */}
        <section className="border-t bg-[#F7FAF9]">
          <div className="mx-auto grid max-w-7xl grid-cols-1 gap-12 px-5 py-24 [&>*]:min-w-0 lg:grid-cols-[1fr_1.4fr] lg:px-8">
            <div>
              <h2 className="text-3xl font-semibold tracking-[-0.03em] sm:text-4xl">Questions, answered</h2>
              <p className="mt-4 text-muted-foreground">Can't find yours? The help centre has more, and you can ask in public.</p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Button variant="outline" className="rounded-xl" asChild><a href={href("/faq/")}>All questions</a></Button>
                <Button variant="ghost" className="rounded-xl" asChild><a href={href("/contact/")}>Contact us</a></Button>
              </div>
            </div>
            <Accordion type="single" collapsible className="w-full">
              {FAQ.map(([q, a]) => (
                <AccordionItem key={q} value={q}><AccordionTrigger className="py-5 text-base">{q}</AccordionTrigger><AccordionContent className="text-muted-foreground">{a}</AccordionContent></AccordionItem>
              ))}
            </Accordion>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
          <div className="relative isolate overflow-hidden rounded-[2rem] bg-[#081C21] px-6 py-16 text-center text-white sm:px-16 sm:py-20">
            <h2 className="mx-auto max-w-2xl text-3xl font-semibold tracking-[-0.03em] text-balance sm:text-5xl">Find your objections before your customers do.</h2>
            <p className="mx-auto mt-4 max-w-lg text-white/70">Free. No sign-up. Uses the Claude app you already have.</p>
            <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row">
              <Button size="lg" className="h-12 rounded-xl bg-white px-6 text-base text-[#081C21] hover:bg-white/90" asChild><a href={href(SITE.app)}>Build my panel</a></Button>
              <Button size="lg" variant="ghost" className="h-12 rounded-xl px-6 text-base text-white hover:bg-white/10 hover:text-white" asChild><a href={href("/sample/")}>See a sample report</a></Button>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
