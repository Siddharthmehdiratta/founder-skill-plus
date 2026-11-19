import type { Metadata } from "next";
import { Button } from "@/components/ui/button";
import { PageShell, Section, SectionHead } from "@/components/site/shell";
import { GhStats } from "@/components/site/gh-stats";
import { GithubMark } from "@/components/site/brand-icons";
import { SITE, href } from "@/lib/site";

export const metadata: Metadata = { title: "Open source", description: "Free and open source under MIT. Live stars, what's inside and how to run your own copy." };

export default function Page() {
  return (
    <PageShell group="Company" kicker="Open source" title="Free, open source, and yours to copy" lead="Every line of code is public under the MIT licence. Use it, change it, or help build it."
      actions={<><Button className="h-11 gap-2 rounded-xl px-5" asChild><a href={SITE.repo}><GithubMark className="size-4" />Open on GitHub</a></Button><Button variant="outline" className="h-11 rounded-xl px-5" asChild><a href={`${SITE.repo}/stargazers`}>Give it a star</a></Button></>}>
      <Section><GhStats repo="Siddharthmehdiratta/founder-skill-plus" /></Section>
      <Section tint>
        <div className="grid grid-cols-1 gap-12 [&>*]:min-w-0 lg:grid-cols-2">
          <div>
            <SectionHead title="What's inside" />
            <ul className="mt-8 grid gap-3">
              {[["site/", "This website, built with Next.js and Tailwind from the free Velora UI template."], ["site/public/", "The panel builder, guide, review analysis and sample reports, in plain HTML and JavaScript."], ["docs/", "The published website that GitHub Pages serves."], ["skills/", "Claude Code skills: the AI customer panel, the score, the reports and the other founder skills."], ["tests/", "Automatic checks for the maths and every page."]].map(([f, d]) => (
                <li key={f} className="rounded-2xl border bg-background p-4"><p className="font-mono text-sm text-primary">{f}</p><p className="mt-1 text-sm text-muted-foreground">{d}</p></li>
              ))}
            </ul>
          </div>
          <div>
            <SectionHead title="Use it in Claude Code" />
            <ol className="mt-8 grid gap-4">
              {[["Open Claude Code.", "In the terminal, the desktop app or the web."], ["Paste the link", "to this repo and say \"install this skill pack\"."], ["Ask for a panel.", "For example: \"test my study app on 30 customers in India\"."]].map(([b, t], i) => <li key={b} className="flex gap-3"><span className="grid size-7 shrink-0 place-items-center rounded-full border bg-background text-sm font-semibold text-primary">{i + 1}</span><p><b className="font-medium">{b}</b> <span className="text-muted-foreground">{t}</span></p></li>)}
            </ol>
            <pre className="mt-8 overflow-x-auto rounded-2xl bg-[#081C21] p-5 text-sm leading-relaxed text-[#DDF2EA]"><code>{`git clone ${SITE.repo}.git
cd founder-skill-plus/docs
python3 -m http.server 8000`}</code></pre>
          </div>
        </div>
      </Section>
      <Section>
        <SectionHead title="Help build it" />
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {[[`${SITE.repo}/stargazers`, "Star the repo", "It helps other founders find it."], ["/contact/#report", "Report a problem", "Bugs get fixed faster with exact steps."], [`${SITE.repo}/pulls`, "Send a change", "Open a pull request. Tests run on every change."]].map(([h, t, d]) => (
            <a key={t} href={href(h)} className="rounded-3xl border p-7 hover:border-primary/30 hover:bg-[#F3FAF7]"><h3 className="font-semibold tracking-tight">{t}</h3><p className="mt-2 text-sm text-muted-foreground">{d}</p></a>
          ))}
        </div>
        <p className="mt-8 text-xs text-muted-foreground">Website design based on Velora UI by Colorlib (MIT). Fonts: Geist (SIL Open Font License).</p>
      </Section>
    </PageShell>
  );
}
