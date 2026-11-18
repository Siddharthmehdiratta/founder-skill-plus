#!/usr/bin/env python3
"""The Product Improvement Manager's tool for founder-product. Standard library only, no network.

It turns real customer feedback (reviews, survey answers, support messages, WhatsApp chats, app-store
reviews, or a founder-consumer panel) into a ranked plan of what to fix, build and keep:

    python3 feedback.py load reviews.csv [more files...]   # CSV, TXT or a panel's results.json
    python3 feedback.py brief                              # the tagging brief for Claude
    python3 feedback.py check                              # which items are untagged or badly tagged
    python3 feedback.py report                             # feedback-report.md, .json and .html

State lives in founder/feedback/ (--dir to change it): items.json, tags.json, tag-brief.md, report files.

Claude reads every item and tags it (theme, sentiment, type, severity, effort). The tool never tags; it
counts the tags and ranks themes, so every number in the report traces back to real feedback.
"""

import argparse
import csv
import io
import json
import os
import sys

SENTIMENTS = ["positive", "neutral", "negative"]
TYPES = ["bug", "complaint", "feature_request", "question", "pricing", "service", "usability", "praise"]
TEXT_COLUMNS = ("review", "text", "feedback", "comment", "comments", "body", "message", "content", "answer", "response")
RATING_COLUMNS = ("rating", "stars", "score", "star_rating")
SOURCE_COLUMNS = ("source", "platform", "channel", "site")
DATE_COLUMNS = ("date", "created", "created_at", "time", "timestamp")


class FeedbackError(Exception):
    pass


def _path(d, *p):
    return os.path.join(d, *p)


def _read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def _num(v):
    try:
        return float(str(v).strip().split("/")[0])
    except (TypeError, ValueError):
        return None


# ── loading ─────────────────────────────────────────────────────────────────────
def parse_csv(text, source=""):
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        return []
    cols = {c.lower().strip(): c for c in rows[0].keys() if c}
    pick = lambda names: next((cols[n] for n in names if n in cols), None)
    tcol = pick(TEXT_COLUMNS)
    if tcol is None:
        raise FeedbackError("no text column found. Name one of: %s" % ", ".join(TEXT_COLUMNS))
    rcol, scol, dcol = pick(RATING_COLUMNS), pick(SOURCE_COLUMNS), pick(DATE_COLUMNS)
    out = []
    for r in rows:
        t = (r.get(tcol) or "").strip()
        if t:
            out.append({"text": t, "rating": _num(r.get(rcol)) if rcol else None,
                        "source": (r.get(scol) or "").strip() if scol else source, "date": (r.get(dcol) or "").strip() if dcol else ""})
    return out


def parse_txt(text, source=""):
    """One piece of feedback per paragraph; if there are no blank lines, one per line."""
    text = text.replace("\r\n", "\n").strip()
    parts = [p.strip() for p in text.split("\n\n")] if "\n\n" in text else [l.strip() for l in text.split("\n")]
    return [{"text": p, "rating": None, "source": source, "date": ""} for p in parts if p]


def parse_panel(res, source="buyer panel"):
    """A founder-consumer results.json: every buyer's reason, doubt and questions become feedback."""
    out = []
    for b in res.get("buyers") or []:
        bits = [b.get("reason", ""), b.get("objection", ""), b.get("unprompted_doubt", "")]
        for q in b.get("questions_before_buying") or []:
            bits.append(q.get("question", "") if isinstance(q, dict) else str(q))
        t = " ".join(x.strip() for x in bits if x and str(x).strip())
        if t:
            out.append({"text": t, "rating": None, "source": "%s (%s, simulated)" % (source, b.get("id", "")), "date": ""})
    return out


def load(d, files, append=False):
    items = _read_json(_path(d, "items.json")) if append and os.path.exists(_path(d, "items.json")) else []
    seen = {i["text"].lower() for i in items}
    added = 0
    for f in files:
        try:
            with open(f, encoding="utf-8-sig") as fh:
                text = fh.read()
        except FileNotFoundError:
            raise FeedbackError("no such file: %s" % f)
        name = os.path.basename(f)
        if f.lower().endswith(".json"):
            got = parse_panel(json.loads(text))
            if not got:
                raise FeedbackError("%s is not a buyer panel results.json (no buyers in it)" % f)
        elif f.lower().endswith(".csv"):
            got = parse_csv(text, name)
        else:
            got = parse_txt(text, name)
        for g in got:
            key = g["text"].lower()
            if key in seen:  # exact duplicates count once
                continue
            seen.add(key)
            items.append(g)
            added += 1
    if not items:
        raise FeedbackError("no feedback found in those files")
    for i, it in enumerate(items):
        it["id"] = "F%03d" % (i + 1)
    _write_json(_path(d, "items.json"), items)
    return added, len(items)


# ── tagging brief and checks ────────────────────────────────────────────────────
BRIEF = """You are the Product Improvement Manager. Read every piece of customer feedback below and tag it.

Rules:
- Tag what the customer actually said. Do not invent problems or praise.
- Reuse the same theme name for the same issue, so they can be counted. Use 5 to 12 short themes in total,
  in plain words (e.g. "delivery delays", "price too high", "app crashes on login", "friendly staff").
- One item can carry up to 2 themes if it clearly raises two issues.
- Mixed items ("tasty, but late"): put the complaint in "themes" with the item's sentiment, and the praised
  thing in "praise_themes" with a "praise_quote", so the praise is counted as praise.
- severity: 1 = minor annoyance, 2 = hurts the experience, 3 = loses the customer, money or safety.
- effort: your estimate of the work to fix or build it: 1 = days, 2 = weeks, 3 = months. Write 0 for praise.

Write the file {out} with your file-writing tool, containing ONLY a JSON object, one entry per id:
{{
  "F001": {{"themes": ["theme"], "sentiment": one of {sentiments}, "type": one of {types},
           "severity": 1 to 3, "effort": 0 to 3, "quote": "the most telling 3 to 12 words from the item",
           "praise_themes": ["only for mixed items"], "praise_quote": "the words of praise"}},
  ...
}}

Feedback ({n} items):
{items}
"""


def brief(d):
    items = _read_json(_path(d, "items.json"))
    lines = ["%s%s: %s" % (i["id"], (" [%g stars]" % i["rating"]) if i.get("rating") is not None else "", i["text"].replace("\n", " "))
             for i in items]
    text = BRIEF.format(out=os.path.abspath(_path(d, "tags.json")), sentiments=" / ".join(SENTIMENTS),
                        types=" / ".join(TYPES), n=len(items), items="\n".join(lines))
    with open(_path(d, "tag-brief.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    return _path(d, "tag-brief.md")


def _tag_problem(t):
    if not isinstance(t, dict):
        return "not an object"
    th = t.get("themes")
    if not isinstance(th, list) or not th or not all(isinstance(x, str) and x.strip() for x in th) or len(th) > 2:
        return "'themes' must be a list of 1 or 2 names"
    if t.get("sentiment") not in SENTIMENTS:
        return "'sentiment' must be one of %s" % ", ".join(SENTIMENTS)
    if t.get("type") not in TYPES:
        return "'type' must be one of %s" % ", ".join(TYPES)
    if isinstance(t.get("severity"), bool) or t.get("severity") not in (1, 2, 3):
        return "'severity' must be 1, 2 or 3"
    if isinstance(t.get("effort"), bool) or t.get("effort") not in (0, 1, 2, 3):
        return "'effort' must be 0, 1, 2 or 3"
    pt = t.get("praise_themes")
    if pt is not None and (not isinstance(pt, list) or len(pt) > 2 or not all(isinstance(x, str) and x.strip() for x in pt)):
        return "'praise_themes' must be a list of up to 2 names"
    return None


def check(d):
    items = _read_json(_path(d, "items.json"))
    try:
        tags = _read_json(_path(d, "tags.json"))
    except FileNotFoundError:
        return [(i["id"], "not tagged") for i in items]
    except json.JSONDecodeError:
        return [("tags.json", "not valid JSON")]
    probs = []
    for i in items:
        if i["id"] not in tags:
            probs.append((i["id"], "not tagged"))
        else:
            p = _tag_problem(tags[i["id"]])
            if p:
                probs.append((i["id"], p))
    return probs


# ── report ──────────────────────────────────────────────────────────────────────
def report(d):
    items = {i["id"]: i for i in _read_json(_path(d, "items.json"))}
    tags = _read_json(_path(d, "tags.json"))
    good = [(items[k], v) for k, v in tags.items() if k in items and _tag_problem(v) is None]
    if not good:
        raise FeedbackError("no valid tags yet: run brief, have Claude tag the items, then check")
    n = len(good)
    themes = {}
    for it, t in good:
        mentions = [(th, t) for th in t["themes"]]
        for th in t.get("praise_themes") or []:  # the praised part of a mixed item counts as praise
            mentions.append((th, {"sentiment": "positive", "type": "praise", "severity": 1, "effort": 0,
                                  "quote": t.get("praise_quote") or t.get("quote")}))
        for th, tt in mentions:
            key = th.strip().lower()
            e = themes.setdefault(key, {"theme": th.strip(), "items": []})
            if not any(x is it for x, _ in e["items"]):
                e["items"].append((it, tt))
    rows = []
    for e in themes.values():
        its = e["items"]
        neg = sum(1 for _, t in its if t["sentiment"] == "negative")
        pos = sum(1 for _, t in its if t["sentiment"] == "positive")
        sev = sum(t["severity"] for _, t in its) / float(len(its))
        efforts = [t["effort"] for _, t in its if t["effort"] > 0]
        effort = (sum(efforts) / float(len(efforts))) if efforts else 0.0
        ratings = [it["rating"] for it, _ in its if it.get("rating") is not None]
        types = {}
        for _, t in its:
            types[t["type"]] = types.get(t["type"], 0) + 1
        main_type = max(types.items(), key=lambda kv: kv[1])[0]
        reach = len(its) / float(n)
        # Priority: how many raise it x how much it hurts x how negative it is, divided by the effort to fix.
        priority = (reach * sev * (neg / float(len(its)))) / (effort if effort else 1.0) * 100
        q = lambda want: [t.get("quote") or it["text"][:90] for it, t in its if t["sentiment"] == want]
        quotes = (q("positive") if pos > neg else q("negative") or q("neutral")) or [t.get("quote") or it["text"][:90] for it, t in its]
        quotes = quotes[:3]
        rows.append({"theme": e["theme"], "mentions": len(its), "share": reach, "negative": neg, "positive": pos,
                     "severity": round(sev, 2), "effort": round(effort, 2), "avg_rating": (sum(ratings) / len(ratings)) if ratings else None,
                     "type": main_type, "priority": round(priority, 1), "quotes": quotes, "ids": [it["id"] for it, _ in its][:6]})
    problems = sorted([r for r in rows if r["negative"] > 0 and r["negative"] >= r["positive"]], key=lambda r: -r["priority"])
    praise = sorted([r for r in rows if r["positive"] > r["negative"]], key=lambda r: -r["mentions"])
    requests = sorted([r for r in rows if r["type"] == "feature_request"], key=lambda r: -r["mentions"])

    def lane(r):  # effort is already inside the priority, so the lanes follow priority alone
        if r["priority"] >= 15:
            return "Now"
        if r["priority"] >= 8:
            return "Next"
        return "Later"
    for r in problems:
        r["lane"] = lane(r)
    sent = {s: sum(1 for _, t in good if t["sentiment"] == s) for s in SENTIMENTS}
    typ = {k: sum(1 for _, t in good if t["type"] == k) for k in TYPES}
    rated = [it["rating"] for it, _ in good if it.get("rating") is not None]
    # Health: share of positive minus share of negative, mapped to 0..100.
    health = round(50 + 50 * (sent["positive"] - sent["negative"]) / float(n))
    res = {"items": len(items), "tagged": n, "sentiment": sent, "types": typ, "health": health,
           "avg_rating": (sum(rated) / len(rated)) if rated else None, "themes": sorted(rows, key=lambda r: -r["mentions"]),
           "fix_first": problems[:5], "keep": praise[:5], "requests": requests[:5],
           "simulated": any("simulated" in (it.get("source") or "") for it, _ in good)}
    res["plain"] = plain(res)
    return res


def plain(res):
    s, n = res["sentiment"], res["tagged"]
    L = ["%d pieces of feedback: %d positive, %d neutral, %d negative." % (n, s["positive"], s["neutral"], s["negative"])]
    if res["avg_rating"] is not None:
        L.append("Average rating: %.1f stars." % res["avg_rating"])
    if res["fix_first"]:
        f = res["fix_first"][0]
        L.append("Fix first: %s (%d of %d customers raised it)." % (f["theme"], f["mentions"], n))
    if res["requests"]:
        L.append("Most asked-for: %s (%d)." % (res["requests"][0]["theme"], res["requests"][0]["mentions"]))
    if res["keep"]:
        L.append("Customers love: %s (%d). Protect it and use it in your marketing." % (res["keep"][0]["theme"], res["keep"][0]["mentions"]))
    if res["simulated"]:
        L.append("Some of this feedback is from simulated buyers. Confirm it with real customers.")
    return L


def report_md(res):
    pct = lambda v: "%.0f%%" % (v * 100)
    L = ["# Product improvement report", "", "**Customer health: %d / 100.** (50 = as many happy as unhappy customers.)" % res["health"], ""]
    L += ["- %s" % x for x in res["plain"]]
    L += ["", "## Fix first (ranked)", "", "| # | problem | mentions | severity | effort | priority | when |", "| ---: | --- | ---: | ---: | ---: | ---: | --- |"]
    for i, r in enumerate(res["fix_first"], 1):
        L.append("| %d | %s | %d (%s) | %.1f | %.1f | %.1f | %s |" % (i, r["theme"], r["mentions"], pct(r["share"]), r["severity"], r["effort"], r["priority"], r["lane"]))
    for title, key in (("Most requested", "requests"), ("What customers love (keep it)", "keep")):
        if res[key]:
            L += ["", "## %s" % title, ""]
            for r in res[key]:
                L.append("- **%s** (%d): %s" % (r["theme"], r["mentions"], " · ".join('"%s"' % q for q in r["quotes"][:2])))
    L += ["", "## Every theme", "", "| theme | mentions | negative | positive | avg rating | main type |", "| --- | ---: | ---: | ---: | ---: | --- |"]
    for r in res["themes"]:
        L.append("| %s | %d | %d | %d | %s | %s |" % (r["theme"], r["mentions"], r["negative"], r["positive"],
                                                    "%.1f" % r["avg_rating"] if r["avg_rating"] is not None else "-", r["type"]))
    L += ["", "Priority = share of customers who raise it x average severity x share negative, divided by effort (x100).",
          "Effort is an estimate from tagging. Now = priority 15 or more; Next = 8 or more; Later = the rest."]
    return "\n".join(L) + "\n"


def report_html(res):
    blob = json.dumps(res, ensure_ascii=False).replace("</", "<\\/")
    return HTML.replace("__DATA__", blob)


HTML = r"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Product improvement report</title><style>
body{margin:0;font:15px/1.55 system-ui,sans-serif;background:#f4f1ff;color:#1b1530}
header{background:linear-gradient(120deg,#0f766e,#0ea5e9 50%,#7c3aed);color:#fff;padding:26px 20px 60px}header h1{margin:0;font-size:24px}
main{max-width:980px;margin:-40px auto 40px;padding:0 14px}.box{background:#fff;border:1px solid #e7e2f5;border-radius:16px;padding:16px;margin-bottom:14px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-bottom:14px}.kpi{border-radius:16px;padding:14px;color:#fff}
.kpi .v{font-size:30px;font-weight:800}.kpi .l{font-size:12px;text-transform:uppercase;opacity:.9}
.lane{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.lane>div{border-radius:14px;padding:10px;background:#faf7ff;border:1px solid #e7e2f5}
.lane h3{margin:0 0 6px}.card{background:#fff;border-radius:10px;padding:8px 10px;margin:6px 0;border-left:4px solid #ef4444;font-size:14px}
.card.Next{border-color:#f59e0b}.card.Later{border-color:#94a3b8}.thin{color:#8f88a6;font-size:12px}
blockquote{margin:6px 0;padding:6px 10px;border-left:4px solid #0ea5e9;background:#f0f9ff;border-radius:0 8px 8px 0;font-size:14px}
table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid #eee;padding:6px;text-align:left}
@media(max-width:640px){.lane{grid-template-columns:1fr}}
</style></head><body><header><h1>Product improvement report</h1><div>What customers say, ranked into what to fix, build and keep</div></header><main>
<div class="kpis" id="k"></div><div class="box"><h2>In plain words</h2><ul id="p"></ul></div>
<div class="box"><h2>Improvement plan</h2><div class="lane" id="lanes"></div></div>
<div class="box"><h2>Most requested</h2><div id="req"></div></div><div class="box"><h2>What customers love (keep it)</h2><div id="keep"></div></div>
<div class="box"><h2>Every theme</h2><table id="t"></table><p class="thin">Priority = share who raise it x severity x share negative, divided by effort (x100). Effort is an estimate.</p></div>
</main><script>
const R = __DATA__; const esc = t => String(t == null ? "" : t).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const hc = R.health >= 65 ? "#10b981" : R.health >= 45 ? "#f59e0b" : "#ef4444";
document.getElementById("k").innerHTML = [["Customer health", R.health + "/100", hc], ["Feedback read", R.tagged, "#7c3aed"],
  ["Negative", R.sentiment.negative, "#ef4444"], ["Positive", R.sentiment.positive, "#10b981"]].concat(R.avg_rating != null ? [["Avg rating", R.avg_rating.toFixed(1) + "★", "#0ea5e9"]] : [])
  .map(([l,v,c]) => `<div class="kpi" style="background:${c}"><div class="l">${l}</div><div class="v">${esc(v)}</div></div>`).join("");
document.getElementById("p").innerHTML = R.plain.map(x => `<li>${esc(x)}</li>`).join("");
document.getElementById("lanes").innerHTML = ["Now","Next","Later"].map(l => `<div><h3>${l}</h3>` + R.fix_first.filter(r => r.lane === l).map(r => `<div class="card ${l}"><b>${esc(r.theme)}</b><br><span class="thin">${r.mentions} mentions · severity ${r.severity} · effort ${r.effort} · priority ${r.priority}</span><blockquote>${esc(r.quotes[0])}</blockquote></div>`).join("") + "</div>").join("");
const list = (id, rs) => document.getElementById(id).innerHTML = rs.length ? rs.map(r => `<p><b>${esc(r.theme)}</b> <span class="thin">(${r.mentions})</span></p>` + r.quotes.slice(0,2).map(q => `<blockquote>${esc(q)}</blockquote>`).join("")).join("") : "<p class='thin'>None yet.</p>";
list("req", R.requests); list("keep", R.keep);
document.getElementById("t").innerHTML = "<tr><th>Theme</th><th>Mentions</th><th>Negative</th><th>Positive</th><th>Avg rating</th><th>Type</th></tr>" + R.themes.map(r => `<tr><td>${esc(r.theme)}</td><td>${r.mentions}</td><td>${r.negative}</td><td>${r.positive}</td><td>${r.avg_rating != null ? r.avg_rating.toFixed(1) : "-"}</td><td>${esc(r.type)}</td></tr>`).join("");
</script></body></html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default=os.path.join("founder", "feedback"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    lp = sub.add_parser("load")
    lp.add_argument("files", nargs="+")
    lp.add_argument("--append", action="store_true", help="add to the feedback already loaded")
    sub.add_parser("brief")
    sub.add_parser("check")
    sub.add_parser("report")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "load":
            added, total = load(a.dir, a.files, a.append)
            print("loaded %d new pieces of feedback (%d in total) into %s. Next: feedback.py brief" % (added, total, a.dir))
        elif a.cmd == "brief":
            print("wrote %s. Tag every item as it says, then: feedback.py check" % brief(a.dir))
        elif a.cmd == "check":
            probs = check(a.dir)
            if not probs:
                print("every item is tagged. Next: feedback.py report")
            for pid, p in probs[:50]:
                print("%s: %s" % (pid, p))
            return 1 if probs else 0
        elif a.cmd == "report":
            res = report(a.dir)
            _write_json(_path(a.dir, "feedback-report.json"), res)
            with open(_path(a.dir, "feedback-report.md"), "w", encoding="utf-8") as fh:
                fh.write(report_md(res))
            with open(_path(a.dir, "feedback-report.html"), "w", encoding="utf-8") as fh:
                fh.write(report_html(res))
            print("health %d/100 from %d pieces of feedback. Wrote feedback-report.md, .json and .html in %s" % (res["health"], res["tagged"], a.dir))
    except FeedbackError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    except FileNotFoundError:
        print("error: nothing loaded in %s yet: run feedback.py load <your file> first" % a.dir, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
