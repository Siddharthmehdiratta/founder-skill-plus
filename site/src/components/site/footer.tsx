import { MENU, SITE, href } from "@/lib/site";
import { GithubMark, LogoMark } from "./brand-icons";

export function SiteFooter() {
  return (
    <footer className="border-t bg-[#F7FAF9]">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 py-16 lg:grid-cols-[1.4fr_repeat(4,1fr)] lg:px-8">
        <div className="max-w-xs">
          <a href={href("/")} className="flex items-center gap-2.5 font-semibold tracking-tight"><LogoMark className="size-7" />{SITE.name}</a>
          <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
            {SITE.blurb}
          </p>
          <a href={SITE.repo} className="mt-5 inline-flex items-center gap-2 rounded-lg border bg-background px-3 py-2 text-sm font-medium shadow-xs hover:bg-muted">
            <GithubMark className="size-4" />Star on GitHub
          </a>
        </div>
        {MENU.map((g) => (
          <div key={g.name}>
            <p className="text-sm font-medium">{g.name}</p>
            <ul className="mt-4 grid gap-2.5 text-sm text-muted-foreground">
              {g.items.map((it) => (
                <li key={it.title}><a href={href(it.href)} className="hover:text-foreground">{it.title}</a></li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t">
        <div className="mx-auto flex max-w-7xl flex-col gap-2 px-5 py-6 text-xs text-muted-foreground sm:flex-row sm:justify-between lg:px-8">
          <p>© 2026 Siddharth Mehdiratta. Free under the MIT licence.</p>
          <p>{SITE.disclaimer}</p>
        </div>
      </div>
    </footer>
  );
}
