"""Browser check of the whole Founder Plus site, desktop and phone.
Serve docs/ at http://localhost:8767/founder-skill-plus/ then run: python3 tools/check_site.py"""
import sys, asyncio
from urllib.parse import unquote_plus
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8767/founder-skill-plus/"
fails = []
def check(c, m):
    print(("ok  " if c else "FAIL"), m)
    if not c: fails.append(m)
PAGES = ["", "how-it-works/", "pricing/", "faq/", "help/", "contact/", "about/", "open-source/", "privacy/", "changelog/"]
APPS = ["builder.html", "how-to-use.html", "feedback.html"]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = await b.new_context(viewport={"width": 1366, "height": 900}); pg = await ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        for name in PAGES:
            await pg.goto(BASE + name)
            check(await pg.locator("h1").count() == 1 and await pg.locator("header.site-header nav[aria-label=Main]").count() == 1 and await pg.locator("footer").count() == 1, f"{name or 'home'}: title, menu and footer")
        for name in APPS + ["example-report.html", "example-report-india.html"]:
            await pg.goto(BASE + name); await pg.wait_for_timeout(200)
            check(await pg.locator("h1").count() == 1, f"{name}: one title")
        for name in APPS:
            await pg.goto(BASE + name); check(await pg.locator("header.site-bar a[href='./']").count() >= 1, f"{name}: links back to the site")
        for old, new in [("faq.html", "faq/"), ("report.html", "contact/#report"), ("github.html", "open-source/")]:
            await pg.goto(BASE + old); await pg.wait_for_timeout(400); check(pg.url.endswith(new), f"old link {old} goes to {new}")
        await pg.goto(BASE + "faq/"); await pg.fill("#q", "price"); await pg.wait_for_timeout(300)
        vis = await pg.locator(".faq-group details").count(); check(0 < vis < 10, f"FAQ search narrows ({vis})")
        await pg.goto(BASE + "help/"); await pg.click("button:has-text('Help')"); await pg.wait_for_timeout(300)
        check(await pg.get_by_role("menuitem", name="Report a problem").first.is_visible(), "Help menu lists Report a problem"); await pg.keyboard.press("Escape")
        await pg.goto(BASE + "contact/"); await pg.fill("#Problem-title", "Copy button does nothing")
        async with ctx.expect_page() as newp:
            await pg.click("#report button[type=submit]")
        gh = await newp.value; u = unquote_plus(unquote_plus(gh.url)); await gh.close()
        check("founder-skill-plus/issues/new" in u and "Copy button does nothing" in u, "Report form opens a filled-in GitHub issue")
        await pg.goto(BASE + "builder.html")
        check(await pg.locator("#genders select").count() >= 1, "builder still has dropdowns")
        await pg.select_option("#tpl", index=2); check(len(await pg.text_content("#out")) > 500, "industry setup loads")
        check(not errs, f"no page errors {errs[:2]}")
        ph = await b.new_page(viewport={"width": 360, "height": 780}, is_mobile=True, has_touch=True)
        for name in PAGES + APPS:
            await ph.goto(BASE + name); w = await ph.evaluate("document.documentElement.scrollWidth"); check(w <= 362, f"{name or 'home'} fits a 360px phone ({w})")
        await ph.goto(BASE); await ph.click("button[aria-label='Open the menu']"); await ph.wait_for_timeout(400)
        check(await ph.locator("nav[aria-label=Mobile] a").count() >= 18, "phone Menu lists every page")
        await b.close()
    print("FAILED %d" % len(fails) if fails else "all Founder Plus checks passed"); sys.exit(1 if fails else 0)
asyncio.run(main())
