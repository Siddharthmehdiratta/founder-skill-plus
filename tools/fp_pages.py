"""Builds the Founder Plus website pages (docs/*.html) from one shared header, footer and icon set.
Run: python3 tools/fp_pages.py
builder.html, how-to-use.html and feedback.html are kept by hand; this script refreshes their header and footer."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SPRITE = (ROOT / "tools" / "fp" / "sprite.html").read_text()
LANDING = (ROOT / "tools" / "fp" / "landing.html").read_text()
REPO = "https://github.com/Siddharthmehdiratta/founder-skill-plus"
ASK = REPO + "/discussions/new?category=q-a"
BUG = REPO + "/issues/new"
FAVICON = "<link rel=\"icon\" href=\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='9' fill='%230E9A74'/%3E%3Ccircle cx='16' cy='16' r='6' fill='none' stroke='%23fff' stroke-width='3'/%3E%3C/svg%3E\">"
NAV = [("index.html#features", "Features"), ("how-it-works.html", "How it works"), ("example-report.html", "Sample report"), ("how-to-use.html", "Guide"), ("faq.html", "FAQ")]
EXTRA_ICONS = """  <symbol id="f-search" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></g></symbol>
  <symbol id="f-help" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6v.6M12 17h.01"/></g></symbol>
  <symbol id="f-shield" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M12 3 4 6v6c0 4.5 3.4 8 8 9 4.6-1 8-4.5 8-9V6z"/></symbol>
  <symbol id="f-globe" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></g></symbol>
</svg>"""
SPRITE_FULL = SPRITE.replace("</svg>", EXTRA_ICONS, 1) if "f-search" not in SPRITE else SPRITE


def head(title, desc):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<link rel="preload" href="fonts/plus-jakarta-sans-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
{FAVICON}
<link rel="stylesheet" href="theme.css">
</head>
<body>
"""


def header(active=""):
    links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h == active else ""}>{t}</a>' for h, t in NAV)
    return f"""{SPRITE_FULL}
<header class="fp-top">
  <div class="wrap">
    <a class="brand" href="index.html"><svg aria-hidden="true"><use href="#f-logo"/></svg>Founder Plus</a>
    <nav aria-label="Main">{links}</nav>
    <div class="right"><a class="sibling" href="https://siddharthmehdiratta.github.io/creator-growth-studio/">Creator Growth Studio</a><a class="fbtn light sm" href="builder.html">Build my panel</a>
      <button class="menu-btn" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="mnav"><span></span><span></span><span></span></button></div>
  </div>
  <nav class="mnav" id="mnav" aria-label="Mobile" hidden>{links}<a class="fbtn primary" href="builder.html">Build my panel</a></nav>
</header>
"""


FOOT = f"""<footer class="fp-foot"><div class="wrap">
  <div><a class="brand" href="index.html"><svg aria-hidden="true"><use href="#f-logo"/></svg>Founder Plus</a><p>AI customers are research, not real customers. Use them to find objections and pick between pitches, then test with real people. Free and open source (MIT), made by Siddharth Mehdiratta.</p></div>
  <div><b>Product</b><a href="builder.html">Build my panel</a><a href="how-it-works.html">How it works</a><a href="example-report.html">Sample: 4 countries</a><a href="example-report-india.html">Sample: India tiers</a><a href="feedback.html#pim">Analyse your reviews</a></div>
  <div><b>Help</b><a href="how-to-use.html">Beginner's guide</a><a href="faq.html">FAQ</a><a href="{ASK}">Ask a question</a><a href="{BUG}">Report a problem</a><a href="feedback.html">Give feedback</a></div>
  <div><b>Project</b><a href="{REPO}">GitHub</a><a href="https://siddharthmehdiratta.github.io/creator-growth-studio/">Creator Growth Studio</a></div>
</div></footer>
<script src="site.js"></script>
"""


def page_hero(kicker, title, lead, crumb):
    return f"""<section class="fp-page-hero"><div class="wrap"><p class="crumbs"><a href="index.html">Home</a><span>/</span>{crumb}</p><span class="kicker">{kicker}</span><h1>{title}</h1><p class="lead">{lead}</p></div></section>"""


CTA = """<section class="fp-cta"><div class="wrap"><div><h2>Ready to hear what customers think?</h2><p>Free. No sign-up. Uses the Claude app you already have.</p></div><a class="fbtn light lg" href="builder.html">Build my panel</a></div></section>"""


def write(name, title, desc, body, active=""):
    (DOCS / name).write_text(head(title, desc) + header(active) + f'<main id="main">\n{body}\n</main>\n' + FOOT + "</body>\n</html>\n")
    print("wrote", name)


HOME = LANDING.replace('href="#build"', 'href="builder.html"') + """
<section class="fp-section">
  <div class="wrap">
    <div class="fp-head"><span class="kicker">See it first</span><h2>Two real sample reports</h2><p>Both were made by the tool, on example businesses. Open one to see exactly what you'll get.</p></div>
    <div class="fp-cards two">
      <a class="fc link" href="example-report.html"><span class="fic c2"><svg aria-hidden="true"><use href="#f-globe"/></svg></span><h3>FocusFlow: a study app in 4 countries</h3><p>10 AI customers in India, the USA, Europe and China react to a $8 a month app. Score 34: price and privacy are the blockers.</p><span class="more">Open the sample report</span></a>
      <a class="fc link" href="example-report-india.html"><span class="fic c3"><svg aria-hidden="true"><use href="#f-users"/></svg></span><h3>India by city and income tier</h3><p>Customers from Tier 1 metros to Tier 4 towns, with official income facts, react to the same offer in English and Hinglish.</p><span class="more">Open the sample report</span></a>
    </div>
  </div>
</section>
""" + CTA

HOW = page_hero("How it works", "How your AI customer panel works", "What happens between pressing Build my panel and reading your score, and where the tool's limits are.", "How it works") + """
<section class="fp-section"><div class="wrap">
  <ol class="fp-steps">
    <li><span class="n">1</span><h3>You describe the offer</h3><p>Your business, the price, and the pitch exactly as a buyer would see it. Start from a ready setup for your industry.</p></li>
    <li><span class="n">2</span><h3>You choose the customers</h3><p>Markets, headcount, genders, ages, incomes, buying habits and biases. Every choice is a dropdown or a number.</p></li>
    <li><span class="n">3</span><h3>Claude plays every customer</h3><p>Each AI customer reads your pitch and answers as one person: yes or no, why, their doubts, and what would change their mind.</p></li>
  </ol>
</div></section>
<section class="fp-section tint"><div class="wrap">
  <div class="fp-split">
    <div><span class="kicker">Real facts, not guesses</span><h2>Each customer is built from published data</h2>
      <p class="muted">Markets come with official facts about how people there pay and save: for example household spending from India's MoSPI survey, income tiers from the ICE 360 survey, or ONS figures for the UK. Facts carry a source link, and customers are told which facts are real.</p></div>
    <ul class="fp-ticks"><li>Incomes, ages and genders spread across the panel in the shares you set</li><li>Buying habits like "reads every review" or "free-tier forever"</li><li>One well-studied bias per customer, such as loss aversion or social proof</li><li>Answers in English, Hinglish, Hindi, German, Mandarin and more</li></ul>
  </div>
</div></section>
<section class="fp-section"><div class="wrap">
  <div class="fp-split">
    <div><span class="kicker">The score</span><h2>How the 0 to 100 score is made</h2>
      <p class="muted">The score compares versions of your idea on the same panel. It is not a sales forecast.</p></div>
    <div class="fp-table"><table><thead><tr><th>Part</th><th>Points</th><th>What it measures</th></tr></thead><tbody>
      <tr><td><b>Demand</b></td><td>60</td><td>How keen buyers are (1 to 5) and how many said yes</td></tr>
      <tr><td><b>Price fit</b></td><td>20</td><td>How many find your price below their "too expensive" point</td></tr>
      <tr><td><b>Trust</b></td><td>20</td><td>How few hold back because they don't trust it yet</td></tr></tbody></table></div>
  </div>
</div></section>
<section class="fp-section tint"><div class="wrap">
  <div class="fp-head"><span class="kicker">Honest limits</span><h2>What AI customers can and can't tell you</h2></div>
  <div class="fp-cards three">
    <div class="fc"><span class="fic c1"><svg aria-hidden="true"><use href="#f-check"/></svg></span><h3>Good for</h3><p>Finding objections, questions and price ranges early, and picking between two pitches before you spend.</p></div>
    <div class="fc"><span class="fic c3"><svg aria-hidden="true"><use href="#f-gauge"/></svg></span><h3>Read as a ceiling</h3><p>AI customers lean agreeable, so treat the buy rate as the best case. The reasons and doubts matter more than the number.</p></div>
    <div class="fc"><span class="fic c4"><svg aria-hidden="true"><use href="#f-shield"/></svg></span><h3>Not a replacement</h3><p>Confirm with real people next: a waitlist, a pre-sale, or a price on a page. The report tells you what to test.</p></div>
  </div>
</div></section>
""" + CTA

FAQS = [
    ("Getting started", [
        ("Is it really free?", "Yes. Founder Plus is open source under the MIT licence. The quick test runs in the Claude app you already use, including the free plan."),
        ("Do I need to install anything?", "No. Build your panel on the website, press Run it in Claude, and paste the message into the Claude app or claude.ai. Claude Code is only needed for bigger panels and the full interactive report."),
        ("How many AI customers should I use?", "20 is a good first look. 10 is faster and safer on Claude's free plan. Use 30 or more with Claude Code when you want steadier numbers."),
        ("Can I start from an example?", "Yes. Pick your industry at the top of the builder. It fills every field with a realistic setup that you can change."),
    ]),
    ("The results", [
        ("How accurate is it?", "It's research, not a forecast. AI customers lean agreeable, so read the buy rate as a ceiling. The value is in the reasons, doubts and questions, which you can then check with real people."),
        ("What does the score mean?", "0 to 100, made of Demand (60 points), Price fit (20) and Trust (20). Use it to compare two versions of your idea on the same panel."),
        ("Why do some customers answer in Hinglish or other languages?", "You choose the languages per market. Real customers in India often think and write in Hinglish, so their answers come back that way, with an English translation."),
    ]),
    ("Customers and markets", [
        ("Which markets have real facts built in?", "India, the United States, the United Kingdom, Europe, China and Japan come with published facts about income and how people pay. You can add your own facts with source links."),
        ("Can I test a business that sells to other businesses?", "Yes. Choose Businesses (B2B) and set the roles that decide, like owner, manager and finance, with what each cares about."),
        ("Why are gender and age dropdowns?", "So every panel adds up to 100% and the setup file stays valid. Leave gender empty if it doesn't matter for your product."),
    ]),
    ("Privacy", [
        ("Where does my business idea go?", "The builder runs in your browser and stores nothing. The message goes only where you paste it: your own Claude chat."),
        ("Can I save my setup?", "Yes. Download customer.json and open it again later with Open a saved setup."),
    ]),
]
faq_html = "".join(f'<section class="faq-group"><h2 id="g{i}">{n}</h2><div class="faq">' + "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items) + "</div></section>" for i, (n, items) in enumerate(FAQS))
chips = "".join(f'<a href="#g{i}">{n}</a>' for i, (n, _) in enumerate(FAQS))
FAQ = page_hero("Help centre", "Frequently asked questions", "Quick answers about getting started, the results, markets and privacy.", "FAQ") + f"""
<section class="fp-section tight"><div class="wrap narrow">
  <div class="faq-search"><svg aria-hidden="true"><use href="#f-search"/></svg><label for="q" class="sr">Search the questions</label><input id="q" type="search" placeholder="Search the questions, for example: price" autocomplete="off"></div>
  <nav class="chips" aria-label="Topics">{chips}</nav>
  <p class="small muted" id="faq-none" hidden>No question matches that. Try another word, or ask below.</p>
  {faq_html}
  <div class="ask"><div><span class="fic c1"><svg aria-hidden="true"><use href="#f-help"/></svg></span><h2>Still have a question?</h2><p>Ask in our public Q and A on GitHub. Answers stay there for the next person. A free GitHub account is needed to post.</p></div>
    <div class="ask-actions"><a class="fbtn primary lg" href="{ASK}">Ask a question</a><a class="fbtn outline lg" href="{BUG}">Report a problem</a></div></div>
</div></section>
"""


def refresh(name, hero=None):
    p = DOCS / name
    s = p.read_text()
    if "<!--HEADER-->" not in s:
        m = re.search(r"<header>.*?</header>", s, re.S)
        if m:
            inner = re.search(r"<h1>(.*?)</h1>\s*<p>(.*?)</p>", m.group(0), re.S)
            hero_html = ""
            if inner:
                hero_html = f'<section class="fp-page-hero"><div class="wrap"><p class="crumbs"><a href="index.html">Home</a><span>/</span>{hero}</p><h1>{inner.group(1)}</h1><p class="lead">{inner.group(2)}</p></div></section>'
            s = s[:m.start()] + "<!--HEADER-->\n<!--/HEADER-->\n" + hero_html + s[m.end():]
        m = re.search(r"<footer>.*?</footer>", s, re.S)
        if m:
            s = s[:m.start()] + "<!--FOOTER-->\n<!--/FOOTER-->" + s[m.end():]
    a, b = s.index("<!--HEADER-->") + 13, s.index("<!--/HEADER-->")
    active = {"how-to-use.html": "how-to-use.html"}.get(name, "")
    s = s[:a] + "\n" + header(active) + s[b:]
    a, b = s.index("<!--FOOTER-->") + 13, s.index("<!--/FOOTER-->")
    s = s[:a] + "\n" + FOOT + s[b:]
    p.write_text(s)
    print("refreshed", name)


if __name__ == "__main__":
    write("index.html", "Founder Plus: test your business idea on AI customers", "Free. Pick who you want to sell to, and a panel of AI customers reacts to your offer in their own words. Claude gives you a score, what to fix and what to say.", HOME)
    write("how-it-works.html", "How it works: Founder Plus", "How the AI customer panel is built from real facts, how the 0 to 100 score is made, and the honest limits.", HOW, "how-it-works.html")
    write("faq.html", "FAQ: Founder Plus", "Answers about getting started, the results, markets and privacy.", FAQ, "faq.html")
    refresh("builder.html")
    refresh("how-to-use.html", "Guide")
    refresh("feedback.html", "Feedback")
