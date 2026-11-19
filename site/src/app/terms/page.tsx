import type { Metadata } from "next";
import { PageShell } from "@/components/site/shell";
import { SITE, href } from "@/lib/site";

export const metadata: Metadata = { title: "Terms", description: "The plain-English rules for using Founder Plus: free, open source, no guarantees." };

export default function Page() {
  return (
    <PageShell group="Company" kicker="Terms" title="Terms of use" lead="A plain-English summary. The MIT licence in the GitHub project is the legal text. Updated 19 November 2026.">
      <article className="mx-auto max-w-3xl px-5 py-16 text-[1.04rem] leading-[1.75] text-[#26363B]">
        {[["Free and open source", "Founder Plus is free to use, copy and change under the MIT licence. There is nothing to buy and no account to create."],
          ["No guarantees", "The tools are provided as they are, without a warranty of any kind. If something is wrong, tell us and we will try to fix it, but we cannot promise it will suit every purpose."],
          ["Estimates, not promises", "AI customers are a simulation. Scores, quotes and prices are estimates to help you find gaps. They are not a forecast of sales and do not replace talking to real customers."],
          ["Not professional advice", "Nothing here is legal, tax, financial or other professional advice. Check important decisions with a qualified person."],
          ["Your content stays yours", "What you type or upload belongs to you. See the privacy page for what happens to it."],
          ["Use it fairly", "Do not paste other people's private details into the tools. Remove names and contact details from reviews first."],
          ["Names and trademarks", "Claude is made by Anthropic. This project is independent and is not affiliated with, endorsed by or sponsored by Anthropic or any company named in an example."]].map(([t, d]) => (
          <section key={t} className="border-b py-7 first:pt-0 last:border-b-0"><h2 className="text-xl font-semibold tracking-tight">{t}</h2><p className="mt-2 text-muted-foreground">{d}</p></section>
        ))}
        <p className="mt-6 flex flex-wrap gap-x-6 gap-y-2"><a href={`https://github.com/${SITE.repo}/blob/main/LICENSE`} className="font-medium text-primary">Read the MIT licence</a><a href={href("/privacy/")} className="font-medium text-primary">Privacy</a><a href={href("/contact/")} className="font-medium text-primary">Contact us</a></p>
      </article>
    </PageShell>
  );
}
