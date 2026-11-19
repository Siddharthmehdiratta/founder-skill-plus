import type { Metadata } from "next";
import { DownloadIcon, ExpandIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageShell } from "@/components/site/shell";
import { Modal } from "@/components/site/modal";
import { SITE, href } from "@/lib/site";

export const metadata: Metadata = { title: "Sample report", description: "A designed 7-page sample report for an example business: exactly what you get for your own idea." };

const PAGES = ["Cover", "Score and summary", "What to fix first", "Why they pass", "Questions to answer", "What they would pay", "Get your own report"];
const PDF = "/sample/founder-plus-sample-report.pdf";

export default function Page() {
  return (
    <PageShell group="Product" kicker="Sample report" title="See a full report before you start" lead="A 7-page sample for FocusFlow, an example study app tested on 10 AI customers in four countries. Tap a page to read it, or download the PDF."
      actions={<><Button className="h-11 gap-2 rounded-xl px-5" asChild><a href={href(PDF)} download><DownloadIcon className="size-4" />Download the PDF</a></Button><Button variant="outline" className="h-11 rounded-xl px-5" asChild><a href={href(SITE.sample)}>Explore it live</a></Button></>}>
      <div className="mx-auto max-w-7xl px-5 py-14 lg:px-8">
        <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 lg:grid-cols-4">
          {PAGES.map((t, i) => (
            <Modal key={t} wide title={`Page ${i + 1}: ${t}`} trigger={
              <button type="button" className="group text-left">
                <span className="relative block overflow-hidden rounded-xl border shadow-sm transition-all group-hover:-translate-y-1 group-hover:shadow-xl group-hover:shadow-primary/10">
                  <img src={href(`/sample/page-${i + 1}.png`)} alt="" loading={i < 4 ? "eager" : "lazy"} className="block w-full" />
                  <span className="absolute right-2 bottom-2 grid size-8 place-items-center rounded-lg bg-background/90 opacity-0 shadow transition-opacity group-hover:opacity-100"><ExpandIcon className="size-4" /></span>
                </span>
                <span className="mt-2.5 block text-sm"><span className="text-muted-foreground">{i + 1}.</span> {t}</span>
              </button>}>
              <img src={href(`/sample/page-${i + 1}.png`)} alt={`Sample report page ${i + 1}: ${t}`} className="w-full rounded-lg border" />
            </Modal>
          ))}
        </div>
        <div className="mt-14 rounded-3xl bg-[#081C21] p-8 text-white sm:p-10">
          <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">Get this for your own idea</h2>
          <p className="mt-2 max-w-xl text-white/70">Free, in about ten minutes. No sign-up. Runs in the Claude app you already have.</p>
          <a href={href("/builder.html")} className="mt-6 inline-flex h-12 items-center rounded-xl bg-white px-6 font-medium text-[#081C21]">Build my panel</a>
        </div>
      </div>
    </PageShell>
  );
}
