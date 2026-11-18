"""Browser check of every Founder Plus page (desktop and phone). Run: python3 -m http.server 8767 --directory docs, then python3 tools/check_site.py"""
import asyncio, sys
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8767/"
fails = []
def check(c, m):
    print(("ok  " if c else "FAIL"), m)
    if not c: fails.append(m)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width":1366,"height":900}); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        for name in ["index.html","builder.html","how-it-works.html","faq.html","how-to-use.html","feedback.html","help.html","report.html","github.html","example-report.html","example-report-india.html"]:
            await pg.goto(BASE+name); await pg.wait_for_timeout(200)
            h1 = await pg.locator("h1").count()
            check(h1 == 1, f"{name}: one h1 ({h1})")
            if name not in ("example-report.html","example-report-india.html"):
                check(await pg.locator("header.fp-top .dd").count() == 3, f"{name}: shared menu with dropdowns")
        await pg.goto(BASE+"index.html"); check(await pg.locator(".slide").count() == 5, "home is 5 full-screen slides")
        await pg.click("#s-home .next-slide"); await pg.wait_for_timeout(900); check(await pg.text_content(".slide-count") == "2 / 5", "Next goes to slide 2")
        await pg.goto(BASE+"how-it-works.html"); await pg.click(".deck-bar .deck-next"); await pg.wait_for_timeout(700)
        check(await pg.text_content(".deck-count") == "2 of 4", "How it works deck moves on")
        await pg.goto(BASE+"faq.html"); await pg.fill("#q","price"); await pg.wait_for_timeout(100)
        vis = await pg.evaluate("[...document.querySelectorAll('.faq-group details')].filter(d=>!d.hidden).length")
        check(0 < vis < 10, f"FAQ search narrows ({vis})")
        await pg.goto(BASE+"builder.html")
        check(await pg.locator("#genders select").count() >= 1, "builder still has dropdowns")
        await pg.select_option("#tpl", index=2); check(len(await pg.text_content("#out")) > 500, "industry setup loads")
        check(not errs, f"no page errors {errs[:2]}")
        ph = await b.new_page(viewport={"width":360,"height":780}, is_mobile=True)
        for name in ["index.html","builder.html","how-it-works.html","faq.html","how-to-use.html","feedback.html","help.html","report.html","github.html"]:
            await ph.goto(BASE+name); w = await ph.evaluate("document.documentElement.scrollWidth"); check(w <= 362, f"{name} fits phone ({w})")
        check(await ph.locator(".tabbar span").count() == 5, "phone tab bar has 5 labelled buttons")
        await ph.click(".tabbar [data-sheet-open]"); check(await ph.is_visible("#sheet") and await ph.locator("#sheet .sheet-group a").count() >= 14, "phone Menu lists every page")
        await b.close()
    print("FAILED %d" % len(fails) if fails else "all Founder Plus checks passed"); sys.exit(1 if fails else 0)
asyncio.run(main())
