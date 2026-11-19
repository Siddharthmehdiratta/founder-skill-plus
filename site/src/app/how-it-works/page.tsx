import type { Metadata } from "next";
import { CheckIcon, GaugeIcon, ShieldCheckIcon } from "lucide-react";
import { CtaBand, PageShell, Section, SectionHead, Shot } from "@/components/site/shell";
import { BrowserMockup } from "@/components/velora/browser-mockup";

export const metadata: Metadata = { title: "How it works", description: "How the AI customer panel is built from real facts, how the 0 to 100 score is made, and the honest limits." };

export default function Page() {
  return (
    <PageShell group="Product" kicker="How it works" title="How your AI customer panel works" lead="What happens between pressing Build my panel and reading your score, and where the tool's limits are.">
      <Section>
        <ol className="grid gap-4 md:grid-cols-3">
          {[["You describe the offer", "Your business, the price, and the pitch exactly as a buyer would see it. Start from a ready setup for your industry."], ["You choose the customers", "Markets, headcount, genders, ages, incomes, buying habits and biases. Every choice is a dropdown or a number."], ["Claude plays every customer", "Each AI customer reads your pitch and answers as one person: yes or no, why, their doubts, and what would change their mind."]].map(([t, d], i) => (
            <li key={t} className="rounded-3xl border p-7"><span className="text-sm font-semibold text-primary">Step {i + 1}</span><h2 className="mt-3 text-xl font-semibold tracking-tight">{t}</h2><p className="mt-2 text-muted-foreground">{d}</p></li>
          ))}
        </ol>
        <BrowserMockup url="founder plus · panel builder" className="mt-12 overflow-hidden rounded-2xl shadow-xl shadow-primary/5"><Shot src="/shots/builder.png" alt="The panel builder." /></BrowserMockup>
      </Section>
      <Section tint>
        <div className="grid grid-cols-1 gap-12 [&>*]:min-w-0 lg:grid-cols-2">
          <SectionHead eyebrow="Real facts, not guesses" title="Each customer is built from published data" text="Markets come with official facts about how people there pay and save: for example household spending from India's MoSPI survey, income tiers from the ICE 360 survey, or ONS figures for the UK. Facts carry a source link, and customers are told which facts are real." />
          <ul className="grid gap-4 text-sm">
            {["Incomes, ages and genders spread across the panel in the shares you set", "Buying habits like \"reads every review\" or \"free-tier forever\"", "One well-studied bias per customer, such as loss aversion or social proof", "Answers in English, Hinglish, Hindi, German, Mandarin and more"].map((t) => <li key={t} className="flex gap-3 rounded-2xl border bg-background p-4"><CheckIcon className="mt-0.5 size-4 shrink-0 text-primary" />{t}</li>)}
          </ul>
        </div>
      </Section>
      <Section>
        <div className="grid grid-cols-1 gap-12 [&>*]:min-w-0 lg:grid-cols-2">
          <SectionHead eyebrow="The score" title="How the 0 to 100 score is made" text="The score compares versions of your idea on the same panel. It is not a sales forecast." />
          <div className="overflow-hidden rounded-3xl border">
            <table className="w-full text-sm">
              <thead className="bg-muted/60 text-left"><tr><th className="px-6 py-4 font-medium">Part</th><th className="px-4 py-4 font-medium">Points</th><th className="px-6 py-4 font-medium">What it measures</th></tr></thead>
              <tbody>{[["Demand", "60", "How keen buyers are (1 to 5) and how many said yes"], ["Price fit", "20", "How many find your price below their \"too expensive\" point"], ["Trust", "20", "How few hold back because they don't trust it yet"]].map(([a, b, c]) => <tr key={a} className="border-t"><td className="px-6 py-4 font-medium">{a}</td><td className="px-4 py-4 tabular-nums">{b}</td><td className="px-6 py-4 text-muted-foreground">{c}</td></tr>)}</tbody>
            </table>
          </div>
        </div>
      </Section>
      <Section tint>
        <SectionHead eyebrow="Honest limits" title="What AI customers can and can't tell you" />
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {[[CheckIcon, "Good for", "Finding objections, questions and price ranges early, and picking between two pitches before you spend."], [GaugeIcon, "Read as a ceiling", "AI customers lean agreeable, so treat the buy rate as the best case. The reasons and doubts matter more than the number."], [ShieldCheckIcon, "Not a replacement", "Confirm with real people next: a waitlist, a pre-sale, or a price on a page. The report tells you what to test."]].map(([I, t, d]) => {
            const C = I as typeof CheckIcon;
            return <div key={t as string} className="rounded-3xl border bg-background p-7"><C className="size-5 text-primary" /><h3 className="mt-4 text-lg font-semibold tracking-tight">{t as string}</h3><p className="mt-2 text-sm text-muted-foreground">{d as string}</p></div>;
          })}
        </div>
      </Section>
      <CtaBand />
    </PageShell>
  );
}
