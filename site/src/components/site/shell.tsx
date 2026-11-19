import DIMS from "@/lib/shot-dims.json";
import { SiteHeader } from "./header";
import { SiteFooter } from "./footer";
import { href } from "@/lib/site";

/* Every inner page: header, a calm page title band, the content, the footer. */
export function PageShell({ kicker, title, lead, group = "", crumb, children, actions }: {
  kicker: string; title: string; lead: string; group?: string; crumb?: string; children: React.ReactNode; actions?: React.ReactNode;
}) {
  return (
    <>
      <SiteHeader active={group} />
      <main id="main" className="overflow-x-clip">
        <section className="relative isolate overflow-hidden border-b">
          <div className="mx-auto max-w-7xl px-5 pt-14 pb-12 sm:pt-20 sm:pb-16 lg:px-8">
            <nav aria-label="Breadcrumb" className="text-sm text-muted-foreground">
              <a href={href("/")} className="hover:text-foreground">Home</a><span className="mx-2">/</span>
              {group && <><span>{group}</span><span className="mx-2">/</span></>}<span className="text-foreground">{crumb ?? kicker}</span>
            </nav>
            <h1 className="rise mt-6 max-w-4xl text-5xl leading-[0.98] font-bold tracking-[-0.04em] text-balance sm:text-7xl">{title}</h1>
            <p className="mt-5 max-w-2xl text-lg leading-relaxed text-muted-foreground text-pretty">{lead}</p>
            {actions && <div className="mt-8 flex flex-wrap gap-3">{actions}</div>}
          </div>
        </section>
        {children}
      </main>
      <SiteFooter />
    </>
  );
}

export function Section({ children, tint = false, className = "" }: { children: React.ReactNode; tint?: boolean; className?: string }) {
  return (
    <section className={tint ? "border-y bg-[#F7FAF9]" : ""}>
      <div className={`mx-auto max-w-7xl px-5 py-16 sm:py-20 lg:px-8 ${className}`}>{children}</div>
    </section>
  );
}

export function SectionHead({ eyebrow, title, text }: { eyebrow?: string; title: string; text?: string }) {
  return (
    <div className="max-w-2xl">
            <h2 className="mt-3 text-3xl font-semibold tracking-[-0.03em] text-balance sm:text-4xl">{title}</h2>
      {text && <p className="mt-4 text-muted-foreground">{text}</p>}
    </div>
  );
}

export function Src({ url, name }: { url: string; name: string }) {
  return <a href={url} target="_blank" rel="noopener" className="ml-1 inline-flex rounded-full bg-primary/8 px-2 py-0.5 align-middle text-xs font-medium text-primary hover:bg-primary/15">{name}</a>;
}

export function Shot({ src, alt, className = "", eager = false }: { src: string; alt: string; className?: string; eager?: boolean }) {
  return <picture><source type="image/webp" srcSet={href(src.replace(/\.png$/, ".webp"))} /><img src={href(src)} alt={alt} width={(DIMS as Record<string, number[]>)[src]?.[0]} height={(DIMS as Record<string, number[]>)[src]?.[1]} loading={eager ? "eager" : "lazy"} decoding="async" className={`block h-auto w-full ${className}`} /></picture>;
}

export function CtaBand() {
  return (
    <section className="mx-auto max-w-7xl px-5 py-20 lg:px-8">
      <div className="relative isolate overflow-hidden rounded-[2rem] bg-[#081C21] px-6 py-14 text-center text-white sm:px-16">
        <h2 className="mx-auto max-w-2xl text-3xl font-semibold tracking-[-0.03em] text-balance sm:text-4xl">Hear what customers think before you spend.</h2>
        <p className="mx-auto mt-4 max-w-lg text-white/70">Free. No sign-up. Uses the Claude app you already have.</p>
        <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
          <a href={href("/builder.html")} className="inline-flex h-12 items-center justify-center rounded-xl bg-white px-6 font-medium text-[#081C21] hover:bg-white/90">Build my panel</a>
          <a href={href("/example-report.html")} className="inline-flex h-12 items-center justify-center rounded-xl px-6 font-medium text-white hover:bg-white/10">See a sample report</a>
        </div>
      </div>
    </section>
  );
}
