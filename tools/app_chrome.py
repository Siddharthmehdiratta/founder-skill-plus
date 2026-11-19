"""Gives the hand-made app pages (builder, guide, review analysis) a simple header and footer that match the website.
Run: python3 tools/app_chrome.py   (edits site/public/*.html in place; keeps the icon sprite that the page uses)"""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
BAR = """
<a class="skip" href="#main">Skip to content</a>
<header class="site-bar">
  <div class="wrap">
    <a class="brand" href="./"><svg aria-hidden="true"><use href="#f-logo"/></svg>Founder Plus</a>
    <nav class="bar-nav" aria-label="Main"><a href="builder.html">Build my panel</a><a href="how-it-works/">How it works</a><a href="how-to-use.html">Beginner's guide</a><a href="help/">Help</a><a href="contact/">Contact</a></nav>
    <div class="bar-right"><a class="bar-btn" href="help/">Help</a><a class="bar-btn ghost" href="./">Back to site</a></div>
  </div>
</header>
"""
FOOT = """<footer class="bar-foot"><div class="wrap"><span>Founder Plus. Free and open source (MIT). AI customers are research, not real customers.</span><nav aria-label="Footer"><a href="./">Home</a><a href="faq/">FAQ</a><a href="contact/#report">Report a problem</a><a href="privacy/">Privacy</a></nav></div></footer>
"""
for name in ["builder.html", "how-to-use.html", "feedback.html"]:
    p = ROOT / "site" / "public" / name
    s = p.read_text()
    a, b = s.index("<!--HEADER-->") + 13, s.index("<!--/HEADER-->")
    m = re.search(r"<svg[^>]*position:absolute.*?</svg>", s[a:b], re.S)
    s = s[:a] + "\n" + (m.group(0) if m else "") + BAR + s[b:]
    a, b = s.index("<!--FOOTER-->") + 13, s.index("<!--/FOOTER-->")
    s = s[:a] + "\n" + FOOT + '<script src="site.js"></script>\n' + s[b:]
    p.write_text(s)
    print("updated", name)
