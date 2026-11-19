"use client";
import { ChevronDownIcon, MenuIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { MENU, SITE, href } from "@/lib/site";
import { Icon } from "./icon";
import { GithubMark, LogoMark } from "./brand-icons";

const link = "rounded-lg px-3 py-2 text-[0.92rem] text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

export function SiteHeader({ active = "" }: { active?: string }) {
  const groups = MENU.slice(0, 3);
  return (
    <header className="site-header sticky top-0 z-40 border-b border-border/70 bg-background/80 backdrop-blur-xl">
      <nav aria-label="Main" className="mx-auto flex h-16 max-w-7xl items-center gap-6 px-5 lg:px-8">
        <a href={href("/")} className="flex shrink-0 items-center gap-2.5 font-semibold tracking-tight">
          <LogoMark className="size-7" />
          <span>{SITE.name}</span>
        </a>

        <ul className="hidden items-center gap-0.5 md:flex">
          {groups.map((g) => (
            <li key={g.name}>
              <DropdownMenu modal={false}>
                <DropdownMenuTrigger asChild>
                  <button type="button" className={`group inline-flex items-center gap-1 data-[state=open]:bg-muted data-[state=open]:text-foreground ${link} ${active === g.name ? "text-foreground" : ""}`}>
                    {g.name}
                    <ChevronDownIcon aria-hidden className="size-3.5 transition-transform duration-200 group-data-[state=open]:rotate-180" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" sideOffset={12} className="w-[26rem] rounded-2xl p-2 shadow-xl shadow-foreground/5">
                  <div className="grid gap-0.5">
                    {g.items.map((it) => (
                      <DropdownMenuItem key={it.title} asChild className="items-start gap-3 rounded-xl p-2.5">
                        <a href={href(it.href)}>
                          <span className="grid size-9 shrink-0 place-items-center rounded-lg border bg-background text-primary shadow-xs">
                            <Icon name={it.icon} className="size-4" />
                          </span>
                          <span className="grid gap-0.5">
                            <span className="font-medium text-foreground">{it.title}</span>
                            <span className="text-xs leading-snug text-muted-foreground">{it.text}</span>
                          </span>
                        </a>
                      </DropdownMenuItem>
                    ))}
                  </div>
                </DropdownMenuContent>
              </DropdownMenu>
            </li>
          ))}
          <li><a href={href("/about/")} className={`block ${link} ${active === "About" ? "text-foreground" : ""}`}>About</a></li>
          <li><a href={href("/contact/")} className={`block ${link} ${active === "Contact" ? "text-foreground" : ""}`}>Contact</a></li>
        </ul>

        <div className="ml-auto flex items-center gap-2">
          <Button variant="ghost" className="hidden h-9 gap-2 px-3 lg:inline-flex" asChild>
            <a href={href("/open-source/")}><GithubMark className="size-4" />GitHub</a>
          </Button>
          <Button className="hidden h-9 px-4 sm:inline-flex" asChild>
            <a href={href(SITE.app)}>{SITE.cta}</a>
          </Button>

          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline" className="h-10 gap-2 px-3 md:hidden" aria-label="Open the menu">
                <MenuIcon />Menu
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-full gap-0 overflow-y-auto sm:max-w-sm">
              <SheetHeader className="border-b px-5 py-4">
                <SheetTitle>Menu</SheetTitle>
                <SheetDescription className="sr-only">Every page on the site</SheetDescription>
              </SheetHeader>
              <nav aria-label="Mobile" className="grid gap-5 px-3 py-4">
                <SheetClose asChild>
                  <a href={href("/")} className="rounded-xl bg-muted px-3 py-3 font-medium">Home</a>
                </SheetClose>
                {MENU.map((g) => (
                  <div key={g.name}>
                    <p className="px-3 pb-1 text-xs font-medium text-muted-foreground">{g.name}</p>
                    <ul className="grid">
                      {g.items.map((it) => (
                        <li key={it.title}>
                          <SheetClose asChild>
                            <a href={href(it.href)} className="flex items-center gap-3 rounded-xl px-3 py-2.5 hover:bg-muted">
                              <span className="grid size-9 shrink-0 place-items-center rounded-lg border text-primary"><Icon name={it.icon} className="size-4" /></span>
                              <span className="grid"><span className="font-medium">{it.title}</span><span className="text-xs text-muted-foreground">{it.text}</span></span>
                            </a>
                          </SheetClose>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
                <Button size="lg" className="h-12" asChild><a href={href(SITE.app)}>{SITE.cta}</a></Button>
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </nav>
    </header>
  );
}
