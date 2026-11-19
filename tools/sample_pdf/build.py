"""Builds the sample report PDF and page previews from report.html (uses Chrome through Playwright).
Run: python3 tools/sample_pdf/build.py"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "site" / "public" / "sample"
async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width": 900, "height": 1200}, device_scale_factor=1.6)
        await pg.goto((HERE / "report.html").as_uri()); await pg.wait_for_timeout(800)
        await pg.pdf(path=str(OUT / "founder-plus-sample-report.pdf"), format="A4", print_background=True)
        for i, el in enumerate(await pg.query_selector_all(".page")):
            await el.screenshot(path=str(OUT / f"page-{i + 1}.png"))
        await b.close()
    print("built", sorted(x.name for x in OUT.iterdir()))
asyncio.run(main())
