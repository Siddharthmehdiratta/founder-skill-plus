import type { Metadata } from "next";
import { CheckIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { PageShell, Section } from "@/components/site/shell";
import { SITE, href } from "@/lib/site";

export const metadata: Metadata = { title: "Pricing", description: "Founder Plus is free and open source under the MIT licence." };

const ALL = ["Panels of any size and mix", "Markets with official facts", "Answers in English, Hinglish, Hindi and more", "A score out of 100", "What to fix first", "Questions buyers need answered", "A sales answer kit", "Review analysis for real customers", "B2B panels", "Your idea never leaves your browser"];

export default function Page() {
  return (
    <PageShell group="Product" kicker="Pricing" title="Free. Every feature, for everyone." lead="No trial, no card, no account. The whole tool is open source under the MIT licence, so it stays free.">
      <Section>
        <div className="mx-auto grid max-w-4xl overflow-hidden rounded-[2rem] border shadow-xl shadow-primary/5 md:grid-cols-[1fr_1.2fr]">
          <div className="bg-[#081C21] p-9 text-white">
            <p className="text-sm font-medium text-white/70">Everything</p>
            <p className="mt-4 flex items-baseline gap-2"><span className="text-6xl font-semibold tracking-[-0.04em]">₹0</span><span className="text-white/60">forever</span></p>
            <p className="mt-4 text-sm text-white/70">Also $0, €0 and £0. You only need the Claude app, which has a free plan.</p>
            <Button size="lg" className="mt-8 h-12 w-full rounded-xl bg-white text-[#081C21] hover:bg-white/90" asChild><a href={href(SITE.app)}>Build my panel</a></Button>
            <a href={href(SITE.sample)} className="mt-3 block text-center text-sm text-white/70 hover:text-white">See a sample first</a>
          </div>
          <div className="p-9">
            <p className="font-medium">What's included</p>
            <ul className="mt-5 grid gap-3 text-sm">{ALL.map((t) => <li key={t} className="flex gap-2.5"><CheckIcon className="mt-0.5 size-4 shrink-0 text-primary" />{t}</li>)}</ul>
          </div>
        </div>
      </Section>
      <Section tint>
        <div className="mx-auto max-w-3xl">
          <h2 className="text-3xl font-semibold tracking-[-0.03em]">Questions about price</h2>
          <Accordion type="single" collapsible className="mt-6">
            {[["Why is it free?", "It's an open-source project to help founders test ideas cheaply. The code is public on GitHub under MIT, so anyone can use it, copy it and check it."], ["Will it stay free?", "The code is MIT licensed, so it can never be taken back. If a paid version ever appears, this free version stays available."], ["Does running the panel cost money?", "It runs in your own Claude app. 10 customers work on Claude's free plan; bigger panels may need a paid Claude plan, which is between you and Anthropic."], ["Do you see my business idea?", "No. There's no account and no database. The builder runs in your browser, and the message goes only to your own Claude chat."]].map(([q, a]) => (
              <AccordionItem key={q} value={q}><AccordionTrigger className="py-5 text-base">{q}</AccordionTrigger><AccordionContent className="text-muted-foreground">{a}</AccordionContent></AccordionItem>
            ))}
          </Accordion>
        </div>
      </Section>
    </PageShell>
  );
}
