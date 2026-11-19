import { SiteHeader } from "@/components/site/header";
import { SiteFooter } from "@/components/site/footer";
import { Button } from "@/components/ui/button";
import { SITE, href } from "@/lib/site";

export const metadata = { title: "Page not found" };

export default function NotFound() {
  return (
    <>
      <SiteHeader active="" />
      <main id="main" className="mx-auto max-w-7xl px-5 py-24 sm:py-32 lg:px-8">
        <h1 className="hero-title">This page doesn't exist.</h1>
        <p className="mt-8 max-w-xl text-lg text-muted-foreground">The link may be old, or the address may have a typo. These will get you back on track.</p>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <Button size="lg" className="h-12 rounded-xl px-6 text-base" asChild><a href={href("/")}>Go to the home page</a></Button>
          <Button size="lg" variant="outline" className="h-12 rounded-xl px-6 text-base" asChild><a href={href(SITE.app)}>Build my panel</a></Button>
          <Button size="lg" variant="ghost" className="h-12 rounded-xl px-6 text-base" asChild><a href={href("/help/")}>Help centre</a></Button>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
