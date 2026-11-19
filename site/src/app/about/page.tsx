import type { Metadata } from "next";
import { PageShell, Section, SectionHead, CtaBand } from "@/components/site/shell";
import { href } from "@/lib/site";

export const metadata: Metadata = { title: "About", description: "Who makes Founder Plus, and why it's free." };

export default function Page() {
  return (
    <PageShell kicker="About" title="Cheap, honest customer research for every founder" lead="Founder Plus is a free, open-source tool made by Siddharth Mehdiratta in Pune, India. It's an upgraded fork of Jake Schincariol's Founder skill pack (MIT).">
      <Section>
        <div className="grid grid-cols-1 gap-12 [&>*]:min-w-0 lg:grid-cols-2">
          <SectionHead eyebrow="Why it exists" title="Most ideas fail on things a customer would have said in a minute." />
          <div className="grid gap-5 text-lg leading-relaxed text-muted-foreground">
            <p>Price too high. Doesn't trust a new brand. Already uses something free. Real research finds these, but it takes weeks and money most founders don't have yet.</p>
            <p>An AI panel won't replace real customers. It does surface the likely objections and questions in an afternoon, so your first real test is a much better one.</p>
          </div>
        </div>
      </Section>
      <Section tint>
        <SectionHead eyebrow="What we believe" title="Four rules the tool never breaks" />
        <div className="mt-10 grid gap-4 md:grid-cols-2">
          {[["Research, not a forecast", "Every report says AI customers lean agreeable and that the buy rate is a ceiling."], ["Real facts, with sources", "Market facts come from official surveys, with links, and customers are told which facts are real."], ["Your idea stays yours", "The builder runs in your browser. Your pitch goes only to your own Claude chat."], ["Free and open", "Every line of code is public under the MIT licence."]].map(([t, d]) => (
            <div key={t} className="rounded-3xl border bg-background p-7"><h3 className="text-lg font-semibold tracking-tight">{t}</h3><p className="mt-2 text-muted-foreground">{d}</p></div>
          ))}
        </div>
      </Section>
      <Section>
        <div className="grid grid-cols-1 gap-10 [&>*]:min-w-0 lg:grid-cols-2">
          <SectionHead eyebrow="The maker" title="Siddharth Mehdiratta" />
          <div className="grid gap-5 text-lg leading-relaxed text-muted-foreground">
            <p>Based in Pune. Founder Plus is one of two free projects; the other is <a className="font-medium text-primary" href="https://siddharthmehdiratta.github.io/creator-growth-studio/">Creator Growth Studio</a>, which shows creators which posts grow their account and why.</p>
            <p>Have an idea or found a problem? <a className="font-medium text-primary" href={href("/contact/")}>Get in touch</a>.</p>
          </div>
        </div>
      </Section>
      <CtaBand />
    </PageShell>
  );
}
