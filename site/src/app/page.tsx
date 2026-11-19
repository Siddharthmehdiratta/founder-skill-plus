import { ArrowRightIcon, CheckIcon, ClipboardListIcon, GaugeIcon, GlobeIcon, MessageSquareTextIcon, ShieldCheckIcon, TargetIcon, UsersIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { BorderBeam } from "@/components/velora/border-beam";
import { BrowserMockup } from "@/components/velora/browser-mockup";
import { SiteHeader } from "@/components/site/header";
import { SiteFooter } from "@/components/site/footer";
import { Shot } from "@/components/site/shell";
import { SITE, href } from "@/lib/site";

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
        <section className="relative isolate overflow-hidden">
          <div aria-hidden className="absolute inset-0 -z-10 bg-[radial-gradient(60%_50%_at_50%_0%,#E3F4EE_0%,transparent_70%)]" />
          <div aria-hidden className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,var(--color-border)_1px,transparent_1px),linear-gradient(to_bottom,var(--color-border)_1px,transparent_1px)] bg-size-[4rem_4rem] opacity-50 mask-[radial-gradient(ellipse_60%_50%_at_50%_0%,black,transparent_75%)]" />
          <div className="mx-auto max-w-7xl px-5 pt-16 pb-10 text-center sm:pt-24 lg:px-8">
            <a href={href("/example-report-india.html")} className="inline-flex items-center gap-2 rounded-full border bg-background/80 px-3 py-1 text-sm text-muted-foreground shadow-xs hover:text-foreground">
              <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">New</span>
              India by city and income tier
              <ArrowRightIcon className="size-3.5" />
            </a>
            <h1 className="mx-auto mt-7 max-w-4xl text-[2.6rem] leading-[1.05] font-semibold tracking-[-0.04em] text-balance sm:text-6xl lg:text-7xl">
              Test your business idea on AI customers before you spend.
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-muted-foreground text-pretty sm:text-xl">
              Pick who you want to sell to. A panel of AI customers reads your offer and reacts in their own words. You get a score, what to fix, and what to say.
            </p>
            <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Button size="lg" className="h-12 rounded-xl px-6 text-base shadow-lg shadow-primary/25" asChild>
                <a href={href(SITE.app)}>Build my panel<ArrowRightIcon /></a>
              </Button>
              <Button size="lg" variant="outline" className="h-12 rounded-xl px-6 text-base" asChild>
                <a href={href(SITE.sample)}>See a sample report</a>
              </Button>
            </div>
            <ul className="mt-6 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
              {["Free", "No sign-up", "Runs in Claude"].map((t) => <li key={t} className="flex items-center gap-1.5"><CheckIcon className="size-4 text-primary" />{t}</li>)}
            </ul>
          </div>

          <div className="mx-auto max-w-6xl px-5 pb-20 lg:px-8">
            <div className="relative">
              <div aria-hidden className="absolute -inset-x-10 -top-10 -bottom-4 -z-10 rounded-[3rem] bg-[radial-gradient(50%_60%_at_50%_40%,#A9E2CB_0%,transparent_70%)] opacity-60 blur-2xl" />
              <div className="mx-auto w-full max-w-[19rem] overflow-hidden rounded-[2.4rem] border-8 border-[#081C21] bg-[#081C21] shadow-2xl sm:hidden">
                <Shot eager src="/shots/report-phone.png" alt="A sample report on a phone: score 34 out of 100." className="rounded-[1.8rem]" />
              </div>
              <BrowserMockup url="founder plus · sample report" className="relative hidden overflow-hidden rounded-2xl shadow-2xl shadow-primary/10 sm:block">
                <Shot eager src="/shots/report.png" alt="A sample report: 10 AI customers in four countries give a study app a score of 34 out of 100." />
                <BorderBeam size={260} duration={9} colorFrom="#0B7A5C" colorTo="#7FD6B4" />
              </BrowserMockup>
              <p className="mt-4 text-center text-xs text-muted-foreground">Real report, example business.</p>
            </div>
          </div>
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

        {/* ---------------- features ---------------- */}
        <section className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-sm font-medium text-primary">What you get</p>
            <h2 className="mt-3 text-3xl font-semibold tracking-[-0.03em] sm:text-5xl">Customer research in an afternoon, not a month.</h2>
          </div>
          <div className="mt-14 grid gap-4 lg:grid-cols-6">
            <article className="overflow-hidden rounded-3xl border bg-background lg:col-span-4">
              <div className="p-7 pb-0 sm:p-9 sm:pb-0">
                <UsersIcon className="size-5 text-primary" />
                <h3 className="mt-4 text-xl font-semibold tracking-tight">Customers you choose</h3>
                <p className="mt-2 max-w-md text-muted-foreground">Markets, cities, incomes, ages, genders, buying habits and well-studied biases. Every choice is a dropdown, built on published facts.</p>
              </div>
              <div className="mt-8 ml-7 overflow-hidden rounded-tl-xl border-t border-l shadow-sm sm:ml-9"><Shot src="/shots/builder.png" alt="The panel builder: business, pitch, price and markets." /></div>
            </article>
            <article className="overflow-hidden rounded-3xl border bg-linear-to-b from-[#EEF8F4] to-background lg:col-span-2">
              <div className="p-7 sm:p-9">
                <GaugeIcon className="size-5 text-primary" />
                <h3 className="mt-4 text-xl font-semibold tracking-tight">A score out of 100</h3>
                <p className="mt-2 text-muted-foreground">Demand, price fit and trust, so you can compare two versions of your idea on the same panel.</p>
              </div>
              <div className="mx-7 overflow-hidden rounded-t-xl border border-b-0 shadow-sm sm:mx-9"><Shot src="/shots/report2-phone.png" alt="Score breakdown on a phone." /></div>
            </article>
            <article className="overflow-hidden rounded-3xl border bg-background lg:col-span-2">
              <div className="p-7 sm:p-9">
                <TargetIcon className="size-5 text-primary" />
                <h3 className="mt-4 text-xl font-semibold tracking-tight">What to fix first</h3>
                <p className="mt-2 text-muted-foreground">The top reasons people pass, each with a practical fix, and the group to sell to first.</p>
              </div>
              <div className="mx-7 overflow-hidden rounded-t-xl border border-b-0 shadow-sm sm:mx-9"><Shot src="/shots/india-phone.png" alt="The India tiers sample report on a phone." /></div>
            </article>
            <article className="overflow-hidden rounded-3xl border bg-background lg:col-span-4">
              <div className="grid gap-8 p-7 sm:p-9 md:grid-cols-2">
                <div>
                  <MessageSquareTextIcon className="size-5 text-primary" />
                  <h3 className="mt-4 text-xl font-semibold tracking-tight">A sales kit you can use</h3>
                  <p className="mt-2 text-muted-foreground">Answers to the questions buyers ask most, price ranges they'd accept, and replies to their doubts, ready for your page or pitch.</p>
                  <ul className="mt-6 grid gap-3 text-sm">
                    {[[GlobeIcon, "India, USA, UK, Europe, China and Japan with official facts"], [ClipboardListIcon, "Turn real customer reviews into a fix list"], [ShieldCheckIcon, "Honest limits, printed on every report"]].map(([I, t]) => {
                      const C = I as typeof CheckIcon;
                      return <li key={t as string} className="flex items-center gap-2.5"><C className="size-4 text-primary" />{t as string}</li>;
                    })}
                  </ul>
                </div>
                <div className="overflow-hidden rounded-xl border shadow-sm"><Shot src="/shots/report3.png" alt="Questions buyers need answered, from the sample report." /></div>
              </div>
            </article>
          </div>
        </section>

        {/* ---------------- how it works ---------------- */}
        <section className="border-y bg-[#F7FAF9]">
          <div className="mx-auto grid max-w-7xl items-center gap-14 px-5 py-24 lg:grid-cols-2 lg:px-8">
            <div>
              <p className="text-sm font-medium text-primary">How it works</p>
              <h2 className="mt-3 text-3xl font-semibold tracking-[-0.03em] sm:text-5xl">Three steps. About ten minutes.</h2>
              <ol className="mt-10 grid gap-8">
                {[["Pick your customers", "Start from your industry, or build your panel from scratch. Every choice is a dropdown."],
                  ["Copy one message", "Press Copy the message for Claude, paste it into the Claude app or claude.ai, and send it."],
                  ["Read your score", "Claude plays every customer, then writes your score, the reasons, what to fix and your sales replies."]].map(([t, d], i) => (
                  <li key={t} className="flex gap-5">
                    <span className="grid size-10 shrink-0 place-items-center rounded-full border bg-background text-sm font-semibold text-primary shadow-xs">{i + 1}</span>
                    <div><h3 className="text-lg font-semibold tracking-tight">{t}</h3><p className="mt-1 text-muted-foreground">{d}</p></div>
                  </li>
                ))}
              </ol>
              <div className="mt-10 flex flex-wrap gap-3">
                <Button className="h-11 rounded-xl px-5" asChild><a href={href(SITE.app)}>Build my panel</a></Button>
                <Button variant="ghost" className="h-11 rounded-xl px-5" asChild><a href={href("/how-to-use.html")}>Read the beginner's guide</a></Button>
              </div>
            </div>
            <div className="relative mx-auto w-full max-w-sm">
              <div aria-hidden className="absolute -inset-10 -z-10 rounded-full bg-[radial-gradient(closest-side,#CBEBDD,transparent)]" />
              <div className="overflow-hidden rounded-[2.4rem] border-8 border-[#081C21] bg-[#081C21] shadow-2xl">
                <Shot src="/shots/builder-phone.png" alt="The panel builder on a phone." className="rounded-[1.8rem]" />
              </div>
            </div>
          </div>
        </section>

        {/* ---------------- honest limits ---------------- */}
        <section className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-sm font-medium text-primary">Honest by design</p>
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
            <div aria-hidden className="absolute inset-0 -z-10 bg-[radial-gradient(60%_80%_at_50%_0%,#0EA47A_0%,transparent_70%)] opacity-60" />
            <h2 className="mx-auto max-w-2xl text-3xl font-semibold tracking-[-0.03em] text-balance sm:text-5xl">Find your objections before your customers do.</h2>
            <p className="mx-auto mt-4 max-w-lg text-white/70">Free. No sign-up. Uses the Claude app you already have.</p>
            <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row">
              <Button size="lg" className="h-12 rounded-xl bg-white px-6 text-base text-[#081C21] hover:bg-white/90" asChild><a href={href(SITE.app)}>Build my panel</a></Button>
              <Button size="lg" variant="ghost" className="h-12 rounded-xl px-6 text-base text-white hover:bg-white/10 hover:text-white" asChild><a href={href(SITE.sample)}>See a sample report</a></Button>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
