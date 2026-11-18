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
CGS_URL = "https://siddharthmehdiratta.github.io/creator-growth-studio/"
# One menu, used by the desktop dropdowns, the phone menu sheet and the footer.
MENU = [
    ("Product", [("builder.html", "f-rocket", "Build my panel", "Pick customers, get your score"),
                 ("how-it-works.html", "f-sliders", "How it works", "The panel, the score, the limits"),
                 ("example-report.html", "f-globe", "Sample: 4 countries", "A study app tested in 4 markets"),
                 ("example-report-india.html", "f-users", "Sample: India tiers", "Tier 1 metros to Tier 4 towns"),
                 ("feedback.html#pim", "f-chart", "Analyse your reviews", "Turn reviews into a fix list")]),
    ("Learn", [("how-to-use.html", "f-book", "Beginner's guide", "Your first panel, step by step"),
               ("faq.html", "f-search", "FAQ", "Search quick answers")]),
    ("Help", [("help.html", "f-help", "Help centre", "Every way to get help"),
              (ASK, "f-msg", "Ask a question", "Public questions and answers on GitHub"),
              ("report.html", "f-flag", "Report a problem", "Tell us what broke"),
              ("feedback.html", "f-heart", "Give feedback", "What to keep, what to change")]),
    ("Project", [("github.html", "f-code", "GitHub project", "Stars, licence, run it yourself"),
                 (REPO, "f-gh", "Code on GitHub", "Read every line"),
                 (CGS_URL, "f-spark", "Creator Growth Studio", "Our sister project for creators")]),
]


def _item(h, ic, t, sub, active=""):
    cur = ' aria-current="page"' if h == active else ""
    return f'<a href="{h}"{cur}><span class="mi-ic"><svg aria-hidden="true"><use href="#{ic}"/></svg></span><span><b>{t}</b><small>{sub}</small></span></a>'
EXTRA_ICONS = """  <symbol id="f-search" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></g></symbol>
  <symbol id="f-help" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6v.6M12 17h.01"/></g></symbol>
  <symbol id="f-shield" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M12 3 4 6v6c0 4.5 3.4 8 8 9 4.6-1 8-4.5 8-9V6z"/></symbol>
  <symbol id="f-globe" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></g></symbol>
  <symbol id="f-home" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M3 11 12 4l9 7M5 9.5V20h5v-6h4v6h5V9.5"/></symbol>
  <symbol id="f-menu" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z"/></symbol>
  <symbol id="f-rocket" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M5 15c-1.5 1.5-2 5-2 5s3.5-.5 5-2M9 12a17 17 0 0 1 9-9c1 0 3 2 3 3a17 17 0 0 1-9 9zM9 12l-4-1 3-4h4M12 15l1 4 4-3v-4M15 9h.01"/></symbol>
  <symbol id="f-book" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2zM4 21V5M8 7h7"/></symbol>
  <symbol id="f-flag" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M5 21V4h11l-2 4 2 4H5"/></symbol>
  <symbol id="f-heart" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></symbol>
  <symbol id="f-code" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="m8 8-4 4 4 4M16 8l4 4-4 4M14 5l-4 14"/></symbol>
  <symbol id="f-gh" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.7c-2.8.6-3.4-1.3-3.4-1.3-.4-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.4 1.1 2.9.8.1-.6.4-1.1.6-1.3-2.2-.3-4.6-1.1-4.6-5a3.9 3.9 0 0 1 1-2.7 3.6 3.6 0 0 1 .1-2.7s.8-.3 2.8 1a9.6 9.6 0 0 1 5 0c1.9-1.3 2.7-1 2.7-1 .6 1.4.2 2.4.1 2.7a3.9 3.9 0 0 1 1 2.7c0 3.9-2.4 4.7-4.6 5 .4.3.7.9.7 1.9V21c0 .3.2.6.7.5A10 10 0 0 0 12 2z"/></symbol>
  <symbol id="f-x" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" d="M6 6l12 12M18 6 6 18"/></symbol>
  <symbol id="f-down-c" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="m6 9 6 6 6-6"/></symbol>
  <symbol id="f-back" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" d="M19 12H5m0 0 6-6m-6 6 6 6"/></symbol>
  <symbol id="f-next" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" d="M5 12h14m0 0-6-6m6 6-6 6"/></symbol>
  <symbol id="f-info" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></g></symbol>
  <symbol id="f-star" viewBox="0 0 20 20"><path d="M10 1.8l2.4 5 5.4.7-4 3.8 1 5.4L10 14.1l-4.8 2.6 1-5.4-4-3.8 5.4-.7z"/></symbol>
  <symbol id="f-target" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/></g></symbol>
  <symbol id="f-msg" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M4 5h16v11H9l-5 4z"/></symbol>
  <symbol id="f-sliders" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M4 7h10M18 7h2M4 17h4M12 17h8M16 5v4M10 15v4"/></symbol>
  <symbol id="f-chart" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M4 20V4M4 20h16M8 16v-4M12 16V8M16 16v-6"/></symbol>
  <symbol id="f-up" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 16V4m0 0L7 9m5-5 5 5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3"/></symbol>
  <symbol id="f-lock" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></g></symbol>
  <symbol id="f-spark" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8zM19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z"/></symbol>
</svg>"""
SPRITE_FULL = SPRITE.replace("</svg>", EXTRA_ICONS, 1)


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
    """Desktop: Home, three dropdowns and GitHub. Phone: a labelled tab bar at the bottom plus a full menu sheet."""
    groups = dict(MENU)
    def dd(name):
        on = any(h == active for h, *_ in groups[name])
        return (f'<div class="dd"><button class="dd-btn{" on" if on else ""}" type="button" aria-expanded="false">{name}<svg aria-hidden="true"><use href="#f-down-c"/></svg></button>'
                f'<div class="dd-menu">{"".join(_item(*i, active) for i in groups[name])}</div></div>')
    cur = lambda h: ' aria-current="page"' if h == active else ""
    sheet = "".join(f'<div class="sheet-group"><h3>{n}</h3>{"".join(_item(*i, active) for i in items)}</div>' for n, items in MENU)
    tab = lambda h, ic, t: f'<a href="{h}"{cur(h)}><svg aria-hidden="true"><use href="#{ic}"/></svg><span>{t}</span></a>'
    return f"""{SPRITE_FULL}
<a class="skip" href="#main">Skip to content</a>
<header class="fp-top">
  <div class="wrap">
    <a class="brand" href="index.html"><svg aria-hidden="true"><use href="#f-logo"/></svg>Founder Plus</a>
    <nav class="dnav" aria-label="Main"><a href="index.html"{cur("index.html")}>Home</a>{dd("Product")}{dd("Learn")}{dd("Help")}<a href="github.html"{cur("github.html")}>GitHub</a></nav>
    <div class="right"><a class="fbtn light sm" href="builder.html">Build my panel</a></div>
  </div>
</header>
<nav class="tabbar" aria-label="Quick links">{tab("index.html", "f-home", "Home")}{tab("builder.html", "f-rocket", "Build")}{tab("how-to-use.html", "f-book", "Guide")}{tab("help.html", "f-help", "Help")}<button type="button" data-sheet-open aria-controls="sheet" aria-expanded="false"><svg aria-hidden="true"><use href="#f-menu"/></svg><span>Menu</span></button></nav>
<div class="sheet" id="sheet" role="dialog" aria-modal="true" aria-label="Menu" hidden>
  <div class="sheet-card">
    <div class="sheet-head"><b>Menu</b><button type="button" class="sheet-x" data-sheet-close aria-label="Close menu"><svg aria-hidden="true"><use href="#f-x"/></svg></button></div>
    <a class="sheet-home" href="index.html"><svg aria-hidden="true"><use href="#f-home"/></svg>Home</a>
    {sheet}
    <a class="fbtn primary lg sheet-cta" href="builder.html">Build my panel</a>
  </div>
</div>
"""


FOOT = f"""<footer class="fp-foot"><div class="wrap">
  <div><a class="brand" href="index.html"><svg aria-hidden="true"><use href="#f-logo"/></svg>Founder Plus</a><p>AI customers are research, not real customers. Use them to find objections and pick between pitches, then test with real people. Free and open source (MIT), made by Siddharth Mehdiratta.</p></div>
  {"".join(f'<div><b>{n}</b>' + "".join(f'<a href="{h}">{t}</a>' for h, _, t, _ in items) + '</div>' for n, items in MENU)}
</div></footer>
<script src="site.js"></script>
"""


def page_hero(kicker, title, lead, crumb, compact=False):
    return f"""<section class="fp-page-hero{' compact' if compact else ''}"><div class="wrap"><p class="crumbs"><a href="index.html">Home</a><span>/</span>{crumb}</p><span class="kicker">{kicker}</span><h1>{title}</h1><p class="lead">{lead}</p></div></section>"""


CTA = """<section class="fp-cta"><div class="wrap"><div><h2>Ready to hear what customers think?</h2><p>Free. No sign-up. Uses the Claude app you already have.</p></div><a class="fbtn light lg" href="builder.html">Build my panel</a></div></section>"""


def write(name, title, desc, body, active=""):
    (DOCS / name).write_text(head(title, desc) + header(active) + f'<main id="main">\n{body}\n</main>\n' + FOOT + "</body>\n</html>\n")
    print("wrote", name)


def deck(label, slides, done=("builder.html", "Build my panel")):
    """A slide deck: one card at a time, Back and Next buttons, dots, a counter, swipe and arrow keys."""
    n = len(slides)
    items = "".join(f'<div class="deck-slide" id="{i}" data-title="{t}" role="group" aria-roledescription="slide" aria-label="{k + 1} of {n}: {t}">{h}</div>' for k, (i, t, h) in enumerate(slides))
    back = '<button class="deck-prev fbtn outline" type="button"><svg aria-hidden="true"><use href="#f-back"/></svg>Back</button>'
    nxt = '<button class="deck-next fbtn primary" type="button">Next<svg aria-hidden="true"><use href="#f-next"/></svg></button>'
    fin = f'<a class="fbtn primary deck-done" href="{done[0]}" hidden>{done[1]}</a>'
    return f"""<section class="deck-sec"><div class="wrap">
<div class="deck" aria-roledescription="carousel" aria-label="{label}" tabindex="0">
  <div class="deck-bar">{back}<div class="deck-mid"><span class="deck-count" aria-live="polite">1 of {n}</span><b data-deck-label>{slides[0][1]}</b><div class="deck-dots"></div></div>{nxt}{fin}</div>
  <div class="deck-track">{items}</div>
  <div class="deck-foot">{back}{nxt}{fin}</div>
</div></div></section>"""


def next_btn(label):
    return f'<button class="next-slide" type="button" data-next>Next: {label}<svg aria-hidden="true"><use href="#f-down-c"/></svg></button>'


_L = LANDING.replace('href="#build"', 'href="builder.html"')
_HERO_INNER = _L[_L.index('<div class="glow g1"'):_L.index("</section>")].replace('class="fp-visual"', 'class="fp-visual tilt"')
_FEAT = _L[_L.index('<div class="fp-cards">', _L.index('id="features"')):]
_FEAT = _FEAT[:_FEAT.index("</div>\n  </div>\n</section>")] + "</div>"
_STEPS = _L[_L.index('<ol class="fp-steps">'):_L.index("</ol>") + 5].replace("from your industry below,", "from your industry,")

HOME = f"""
<section class="slide dark fp-hero" id="s-home" data-title="Home">
  {_HERO_INNER}
  {next_btn("What you get")}
</section>
<section class="slide" id="s-what" data-title="What you get">
  <div class="wrap"><div class="fp-head center"><h2>Customer research in an afternoon, not a month</h2><p>Find objections and pick between pitches before you spend on ads, stock or a shop.</p></div>
  <div class="fp-cards">
      <div class="fc"><span class="fic c1"><svg aria-hidden="true"><use href="#f-users"/></svg></span><h3>Customers you choose</h3><p>Markets, incomes, ages, habits and biases, from real facts.</p></div>
      <div class="fc"><span class="fic c2"><svg aria-hidden="true"><use href="#f-chat"/></svg></span><h3>Their own words</h3><p>Yes or no, why, and what would change their mind.</p></div>
      <div class="fc"><span class="fic c3"><svg aria-hidden="true"><use href="#f-gauge"/></svg></span><h3>A score and fixes</h3><p>0 to 100, with the fixes ranked by buyers won.</p></div>
      <div class="fc"><span class="fic c4"><svg aria-hidden="true"><use href="#f-doc"/></svg></span><h3>A sales kit</h3><p>Answers to their questions and replies to their doubts.</p></div>
    </div>
  <p class="slide-links"><a class="fbtn outline" href="how-it-works.html">How it works</a></p></div>
  {next_btn("How it works")}
</section>
<section class="slide tint" id="s-how" data-title="How it works">
  <div class="wrap"><div class="fp-head center"><h2>Three steps, about ten minutes</h2><p>No install. No sign-up. Uses the Claude app you already have.</p></div>
  {_STEPS}
  <p class="slide-links"><a class="fbtn outline" href="how-to-use.html">Read the beginner's guide</a></p></div>
  {next_btn("See a sample")}
</section>
<section class="slide" id="s-samples" data-title="Samples">
  <div class="wrap"><div class="fp-head center"><h2>See a real report first</h2><p>Both were made by the tool, on example businesses.</p></div>
    <div class="fp-cards two">
      <a class="fc link" href="example-report.html"><span class="fic c2"><svg aria-hidden="true"><use href="#f-globe"/></svg></span><h3>FocusFlow: a study app in 4 countries</h3><p>10 AI customers in India, the USA, Europe and China react to a $8 a month app. Score 34: price and privacy are the blockers.</p><span class="more">Open the sample report</span></a>
      <a class="fc link" href="example-report-india.html"><span class="fic c3"><svg aria-hidden="true"><use href="#f-users"/></svg></span><h3>India by city and income tier</h3><p>Customers from Tier 1 metros to Tier 4 towns react to the same offer in English and Hinglish.</p><span class="more">Open the sample report</span></a>
    </div></div>
  {next_btn("Get started")}
</section>
<section class="slide tint" id="s-start" data-title="Get started">
  <div class="wrap"><div class="fp-head center"><h2>Ready to hear what customers think?</h2><p>Free. Or find help first. Everything is one tap away.</p></div>
    <p class="slide-links"><a class="fbtn primary lg" href="builder.html">Build my panel</a></p>
    <div class="help-grid">
      <a href="how-to-use.html"><svg aria-hidden="true"><use href="#f-book"/></svg><b>Beginner's guide</b></a>
      <a href="faq.html"><svg aria-hidden="true"><use href="#f-search"/></svg><b>FAQ</b></a>
      <a href="{ASK}"><svg aria-hidden="true"><use href="#f-msg"/></svg><b>Ask a question</b></a>
      <a href="report.html"><svg aria-hidden="true"><use href="#f-flag"/></svg><b>Report a problem</b></a>
      <a href="feedback.html"><svg aria-hidden="true"><use href="#f-heart"/></svg><b>Give feedback</b></a>
      <a href="github.html"><svg aria-hidden="true"><use href="#f-gh"/></svg><b>GitHub project</b></a>
    </div></div>
</section>
"""

HOW = page_hero("How it works", "How your AI customer panel works", "Four short slides: the steps, where the facts come from, how the score is made, and the honest limits.", "How it works", compact=True) + deck("How it works", [
    ("steps", "The 3 steps", """<div class="dk-head"><h2>The 3 steps</h2><p>Describe, choose, read.</p></div>
  <ol class="fp-steps">
    <li><span class="n">1</span><h3>You describe the offer</h3><p>Your business, the price, and the pitch exactly as a buyer would see it. Start from a ready setup for your industry.</p></li>
    <li><span class="n">2</span><h3>You choose the customers</h3><p>Markets, headcount, genders, ages, incomes, buying habits and biases. Every choice is a dropdown or a number.</p></li>
    <li><span class="n">3</span><h3>Claude plays every customer</h3><p>Each AI customer reads your pitch and answers as one person: yes or no, why, their doubts, and what would change their mind.</p></li>
  </ol>"""),
    ("facts", "Real facts", """<div class="fp-split">
    <div><h2>Each customer is built from published data</h2>
      <p class="muted">Markets come with official facts about how people there pay and save: for example household spending from India's MoSPI survey, income tiers from the ICE 360 survey, or ONS figures for the UK. Facts carry a source link, and customers are told which facts are real.</p></div>
    <ul class="fp-ticks"><li>Incomes, ages and genders spread across the panel in the shares you set</li><li>Buying habits like "reads every review" or "free-tier forever"</li><li>One well-studied bias per customer, such as loss aversion or social proof</li><li>Answers in English, Hinglish, Hindi, German, Mandarin and more</li></ul>
  </div>"""),
    ("score", "The score", """<div class="fp-split">
    <div><h2>How the 0 to 100 score is made</h2>
      <p class="muted">The score compares versions of your idea on the same panel. It is not a sales forecast.</p></div>
    <div class="fp-table"><table><thead><tr><th>Part</th><th>Points</th><th>What it measures</th></tr></thead><tbody>
      <tr><td><b>Demand</b></td><td>60</td><td>How keen buyers are (1 to 5) and how many said yes</td></tr>
      <tr><td><b>Price fit</b></td><td>20</td><td>How many find your price below their "too expensive" point</td></tr>
      <tr><td><b>Trust</b></td><td>20</td><td>How few hold back because they don't trust it yet</td></tr></tbody></table></div>
  </div>"""),
    ("limits", "Honest limits", """<div class="dk-head"><h2>What AI customers can and can't tell you</h2></div>
  <div class="fp-cards three">
    <div class="fc"><span class="fic c1"><svg aria-hidden="true"><use href="#f-check"/></svg></span><h3>Good for</h3><p>Finding objections, questions and price ranges early, and picking between two pitches before you spend.</p></div>
    <div class="fc"><span class="fic c3"><svg aria-hidden="true"><use href="#f-gauge"/></svg></span><h3>Read as a ceiling</h3><p>AI customers lean agreeable, so treat the buy rate as the best case. The reasons and doubts matter more than the number.</p></div>
    <div class="fc"><span class="fic c4"><svg aria-hidden="true"><use href="#f-shield"/></svg></span><h3>Not a replacement</h3><p>Confirm with real people next: a waitlist, a pre-sale, or a price on a page. The report tells you what to test.</p></div>
  </div>"""),
]) + CTA

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
FAQ = page_hero("FAQ", "Frequently asked questions", "Quick answers about getting started, the results, markets and privacy.", "FAQ") + f"""
<section class="fp-section tight"><div class="wrap narrow">
  <div class="faq-search"><svg aria-hidden="true"><use href="#f-search"/></svg><label for="q" class="sr">Search the questions</label><input id="q" type="search" placeholder="Search the questions, for example: price" autocomplete="off"></div>
  <nav class="chips" aria-label="Topics">{chips}</nav>
  <p class="small muted" id="faq-none" hidden>No question matches that. Try another word, or ask below.</p>
  {faq_html}
  <div class="ask"><div><span class="fic c1"><svg aria-hidden="true"><use href="#f-help"/></svg></span><h2>Still have a question?</h2><p>Ask in our public Q and A on GitHub. Answers stay there for the next person. A free GitHub account is needed to post.</p></div>
    <div class="ask-actions"><a class="fbtn primary lg" href="{ASK}">Ask a question</a><a class="fbtn outline lg" href="{BUG}">Report a problem</a></div></div>
</div></section>
"""


_popular = [FAQS[0][1][0], FAQS[0][1][1], FAQS[1][1][0], FAQS[3][1][0]]
HELP = page_hero("Help centre", "How can we help?", "Pick what you need. Every option is free and answered in public, so the next person learns too.", "Help centre") + f"""
<section class="fp-section tight"><div class="wrap">
  <form class="faq-search big" action="faq.html" method="get" role="search"><svg aria-hidden="true"><use href="#f-search"/></svg><label for="hq" class="sr">Search the questions</label><input id="hq" name="q" type="search" placeholder="Search answers, for example: price" autocomplete="off"><button class="fbtn primary" type="submit">Search</button></form>
  <div class="hub">
    {"".join(f'<a class="hub-c" href="{h}"><span class="mi-ic"><svg aria-hidden="true"><use href="#{ic}"/></svg></span><b>{t}</b><small>{sub}</small></a>' for h, ic, t, sub in [
        ("how-to-use.html", "f-book", "Beginner's guide", "Your first panel, step by step"),
        ("faq.html", "f-search", "FAQ", "Quick answers, searchable"),
        (ASK, "f-msg", "Ask a question", "Post it in our public Q and A"),
        ("report.html", "f-flag", "Report a problem", "Something broke or looks wrong"),
        ("feedback.html", "f-heart", "Give feedback", "Tell us what to keep or change"),
        ("github.html", "f-code", "GitHub project", "Code, licence and how to help build it"),
        ("example-report.html", "f-globe", "Sample report", "See exactly what you'll get"),
        ("how-it-works.html", "f-sliders", "How it works", "The panel, the score, the limits")])}
  </div>
  <div class="fp-split help-split">
    <div><h2>Popular questions</h2><div class="faq">{"".join(f'<details><summary>{q}</summary><p>{x}</p></details>' for q, x in _popular)}</div><p><a href="faq.html">See all questions</a></p></div>
    <div class="note-card"><h3>How replies work</h3><ol class="nums"><li><b>You post</b> a question, problem or idea on GitHub.</li><li><b>We reply there</b>, in public, usually within a few days.</li><li><b>You get an email</b> from GitHub when someone answers.</li></ol><p class="small muted">A free GitHub account is needed to post. Nothing is sent until you press the final button on GitHub.</p></div>
  </div>
</div></section>
"""


def fld(label, name, kind="text", opts=None, req=False, hint=""):
    r = " required" if req else ""
    h = f'<small>{hint}</small>' if hint else ""
    fid = "f-" + "".join(c for c in name.lower() if c.isalnum())
    if kind == "area":
        ctl = f'<textarea id="{fid}" name="{name}" rows="4"{r}></textarea>'
    elif kind == "select":
        ctl = f'<select id="{fid}" name="{name}"{r}><option value="">Choose one</option>' + "".join(f"<option>{o}</option>" for o in opts) + "</select>"
    else:
        ctl = f'<input id="{fid}" name="{name}" type="text"{r}>'
    return f'<div class="fld"><label for="{fid}">{label}</label>{h}{ctl}</div>'


PARTS = ["Home page", "Panel builder", "Running it in Claude", "The report", "Beginner's guide", "Something else"]
REPORT = page_hero("Report a problem", "Something broke? Tell us.", "The more exact you are, the faster it gets fixed. Please don't include passwords or private numbers.", "Report a problem") + f"""<section class="fp-section tight"><div class="wrap narrow">
  <form class="gh-form card" data-gh-issue="{BUG}" data-kind="Problem">
    <p class="muted">Answer what you can. Skip what you don't know.</p>
    {fld("What went wrong, in one line?", "title", req=True, hint="For example: Run it in Claude does nothing")}{fld("Which part?", "Part", "select", PARTS)}
    {fld("What did you do?", "Steps", "area", hint="The buttons you pressed, in order")}{fld("What happened?", "What happened", "area")}{fld("What did you expect?", "Expected", "area")}
    {fld("Device", "Device", "select", ["Phone", "Computer", "Tablet"])}{fld("Browser", "Browser", hint="For example: Chrome on Windows")}
    <button class="fbtn primary lg" type="submit">Send report on GitHub</button>
    <p class="small muted">This opens GitHub in a new tab with your words filled in. Press <b>Create</b> there to send it. A free GitHub account is needed. Nothing is sent until you press it.</p>
    <p class="form-ok callout good" hidden>GitHub is open in a new tab. Press Create there to send. Thank you.</p>
  </form>
</div></section>"""

GITHUB = page_hero("GitHub project", "Free, open source and yours to copy", "Every line is public under the MIT licence. Use it, change it, or help build it.", "GitHub project") + f"""
<section class="fp-section tight"><div class="wrap">
  <div class="gh-stats" data-gh-repo="Siddharthmehdiratta/founder-skill-plus">
    <div><b data-gh="stars">…</b><span>Stars</span></div><div><b data-gh="forks">…</b><span>Copies (forks)</span></div><div><b data-gh="issues">…</b><span>Open issues</span></div><div><b data-gh="updated">…</b><span>Last update</span></div><div><b data-gh="license">…</b><span>Licence</span></div>
  </div>
  <p class="gh-actions"><a class="fbtn primary lg" href="{REPO}"><svg aria-hidden="true"><use href="#f-gh"/></svg>Open on GitHub</a><a class="fbtn outline lg" href="{REPO}/stargazers">Give it a star</a></p>
  <div class="fp-split">
    <div><h2>What's inside</h2>
      <ul class="tree"><li><b>docs/</b><span>This website, the panel builder and the sample reports.</span></li>
        <li><b>skills/</b><span>Claude Code skills: the AI customer panel, the score and the reports.</span></li>
        <li><b>tests/</b><span>Automatic checks for the maths and every page.</span></li></ul></div>
    <div><h2>Use it in Claude Code</h2>
      <ol class="nums"><li><b>Open Claude Code.</b> In the terminal, the desktop app or the web.</li><li><b>Paste the link</b> {REPO} and say "install this skill pack".</li><li><b>Ask for a panel.</b> For example: "test my study app on 30 customers in India".</li></ol>
      <pre class="code"><code>git clone {REPO}.git
cd founder-skill-plus/docs
python3 -m http.server 8000</code></pre></div>
  </div>
  <h2 class="gh-h">Help build it</h2>
  <div class="fp-cards three">
    <a class="fc link" href="{REPO}/stargazers"><span class="fic c3"><svg aria-hidden="true"><use href="#f-star"/></svg></span><h3>Star the repo</h3><p>It helps other founders find it.</p></a>
    <a class="fc link" href="report.html"><span class="fic c4"><svg aria-hidden="true"><use href="#f-flag"/></svg></span><h3>Report a problem</h3><p>Bugs get fixed faster with exact steps.</p></a>
    <a class="fc link" href="{REPO}/pulls"><span class="fic c1"><svg aria-hidden="true"><use href="#f-code"/></svg></span><h3>Send a change</h3><p>Open a pull request. Tests run on every change.</p></a>
  </div>
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
    active = name
    s = s[:a] + "\n" + header(active) + s[b:]
    a, b = s.index("<!--FOOTER-->") + 13, s.index("<!--/FOOTER-->")
    s = s[:a] + "\n" + FOOT + s[b:]
    p.write_text(s)
    print("refreshed", name)


if __name__ == "__main__":
    write("index.html", "Founder Plus: test your business idea on AI customers", "Free. Pick who you want to sell to, and a panel of AI customers reacts to your offer in their own words. Claude gives you a score, what to fix and what to say.", HOME, "index.html")
    write("help.html", "Help centre: Founder Plus", "Every way to get help: beginner's guide, FAQ, ask a question, report a problem, give feedback.", HELP, "help.html")
    write("report.html", "Report a problem: Founder Plus", "Something broke? Tell us exactly what happened.", REPORT, "report.html")
    write("github.html", "GitHub project: Founder Plus", "Free and open source under MIT. Stars, licence, what's inside and how to use it.", GITHUB, "github.html")
    write("how-it-works.html", "How it works: Founder Plus", "How the AI customer panel is built from real facts, how the 0 to 100 score is made, and the honest limits.", HOW, "how-it-works.html")
    write("faq.html", "FAQ: Founder Plus", "Answers about getting started, the results, markets and privacy.", FAQ, "faq.html")
    refresh("builder.html")
    refresh("how-to-use.html", "Guide")
    refresh("feedback.html", "Feedback")
