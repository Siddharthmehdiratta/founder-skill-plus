#!/usr/bin/env python3
"""The buyer panel for founder-consumer. Standard library only, no network.

It does the bookkeeping for a swarm of simulated buyers: it deals one persona card
per buyer from your target-customer profile (income, age, behaviour, objection),
writes one brief per buyer for a sub-agent to answer, checks the answers, and
tallies who buys, who doesn't, and why.

    python3 panel.py init --customer founder/customer.json --pitch founder/pitch.md [--n 100] [--seed 7]
    python3 panel.py prompts [--wave 10]     # one brief per buyer still to run, listed in waves
    python3 panel.py check                   # which answers are missing or broken
    python3 panel.py save P003 < reply.txt   # file a buyer's own JSON that it printed instead of writing
    python3 panel.py tally [--out founder/panel/results.md]
    python3 panel.py status

State lives in founder/panel/ (--dir to change it): panel.json, personas.json,
briefs/<id>.md, answers/<id>.json, results.md, results.json.

The tool never answers for a buyer. Every number in results.md is counted from
the answer files the sub-agents wrote. Simulated buyers are a fast, cheap way to
find objections and weak spots. They are not customers: confirm what matters
with real ones (a pre-sale, a waitlist, a landing page with a price on it).
"""

import argparse
import re
import json
import os
import random
import sys

FIRST_NAMES = [
    "Maya", "Jordan", "Priya", "Marcus", "Sofia", "Ethan", "Aisha", "Liam", "Chloe", "Daniel", "Nadia", "Owen",
    "Grace", "Ravi", "Emma", "Kenji", "Zoe", "Luca", "Hana", "Noah", "Fatima", "Caleb", "Isla", "Mateo", "Leah",
    "Omar", "Ava", "Theo", "Mei", "Jonah", "Sara", "Diego", "Ruby", "Kofi", "Nora", "Felix", "Amara", "Ben", "Lina",
    "Sam", "Aria", "Julian", "Keisha", "Marco", "Ines", "Tariq", "Elena", "Hugo", "Yara", "Callum", "Rosa", "Idris",
    "Freya", "Andre", "Leila", "Mason", "Talia", "Rohan", "Esme", "Victor", "Anya", "Kai", "Beatriz", "Declan",
    "Sana", "Jasper", "Min", "Gabriel", "Olivia", "Arjun", "Clara", "Malik", "Iris", "Wes", "Noor", "Rafael", "Ivy",
    "Dev", "Maeve", "Tomas", "Celine", "Adrian", "Lucia", "Hamza", "Poppy", "Ezra", "Sienna", "Darius", "Quinn",
    "Selin", "Rhys", "Nia", "Oscar", "Tess", "Bilal", "Jade", "Luis", "Harper", "Emil", "Kira", "Pablo", "Alma",
    "Seth", "Zara", "Nico", "Farah", "Levi", "June", "Eli", "Ana", "Yusuf", "Lena", "Cole", "Mira", "Raj", "Elle",
    "Finn", "Dana", "Sol", "Ada",
]
# Region presets: currency, how numbers are grouped, and first names by gender (m / f).
# A region only sets defaults; anything in customer.json ("currency", "names") wins.
REGIONS = {
    "IN": {"label": "India", "currency": "\u20b9", "grouping": "lakh", "names": {
        "m": ["Aarav", "Vivaan", "Aditya", "Arjun", "Kabir", "Rohan", "Karan", "Nikhil", "Varun", "Rahul", "Yash", "Pranav",
              "Kunal", "Sahil", "Vikram", "Imran", "Farhan", "Joseph", "Suresh", "Amit", "Omkar", "Gurpreet", "Dhruv",
              "Parth", "Atharva", "Zaid", "Anil", "Deepak", "Harsh", "Tushar"],
        "f": ["Aditi", "Ananya", "Diya", "Isha", "Kavya", "Meera", "Nisha", "Pooja", "Priya", "Riya", "Sneha", "Tanvi",
              "Shruti", "Neha", "Anjali", "Divya", "Radhika", "Gauri", "Sayali", "Aisha", "Zoya", "Sana", "Simran",
              "Harleen", "Lakshmi", "Swati", "Mariam", "Riddhi", "Janhvi", "Kriti"]}},
    "US": {"label": "United States", "currency": "$", "names": {
        "m": ["James", "Michael", "David", "Chris", "Tyler", "Brandon", "Jose", "Luis", "Marcus", "Andre", "Kevin", "Ryan",
              "Ethan", "Noah", "Jason", "Daniel", "Carlos", "Darnell", "Kenji", "Raj", "Omar", "Matt", "Josh", "Jake",
              "Anthony", "Eric", "Brian", "Malik", "Trevor", "Diego"],
        "f": ["Jessica", "Ashley", "Emily", "Sarah", "Maria", "Jasmine", "Brianna", "Megan", "Lauren", "Sofia", "Hannah",
              "Kayla", "Olivia", "Emma", "Mia", "Aaliyah", "Grace", "Nicole", "Rachel", "Priya", "Mei", "Gabriela",
              "Taylor", "Amanda", "Destiny", "Chloe", "Natalie", "Camila", "Tiffany", "Erin"]}},
    "UK": {"label": "United Kingdom", "currency": "\u00a3", "names": {
        "m": ["Oliver", "Harry", "George", "Jack", "Charlie", "Thomas", "James", "William", "Alfie", "Callum", "Liam",
              "Mohammed", "Ali", "Rhys", "Ewan", "Jamie", "Connor", "Kieran", "Arjun", "Kwame", "Tom", "Ben", "Sam",
              "Dan", "Josh", "Luke", "Owen", "Ryan", "Joe", "Adam"],
        "f": ["Olivia", "Amelia", "Isla", "Ava", "Emily", "Sophie", "Grace", "Lily", "Freya", "Chloe", "Ellie", "Jessica",
              "Amira", "Priya", "Aisha", "Holly", "Megan", "Rebecca", "Hannah", "Lucy", "Charlotte", "Zara", "Ruby",
              "Poppy", "Niamh", "Eilidh", "Katie", "Laura", "Abigail", "Fatima"]}},
    "EU": {"label": "Europe (mixed)", "currency": "\u20ac", "names": {
        "m": ["Lukas", "Felix", "Jonas", "Matteo", "Lorenzo", "Hugo", "Louis", "Pablo", "Javier", "Pieter", "Lars",
              "Mikkel", "Tomasz", "Jakub", "Andrei", "Nikos", "Joao", "Thomas", "Leon", "Elias", "Luca", "Marco",
              "Antoine", "Sergio", "Daan", "Emil", "Piotr", "Stefan", "Karim", "Mehmet"],
        "f": ["Emma", "Mia", "Lena", "Sofia", "Giulia", "Chiara", "Camille", "Manon", "Lucia", "Carmen", "Anna", "Sanne",
              "Freja", "Ingrid", "Zofia", "Julia", "Elena", "Maria", "Ines", "Ana", "Clara", "Lea", "Marta", "Eva",
              "Nora", "Elif", "Yasmin", "Hanna", "Laura", "Beatriz"]}},
    "CN": {"label": "China", "currency": "\u00a5", "names": {
        "m": ["Wei", "Hao", "Jun", "Lei", "Tao", "Ming", "Jie", "Bo", "Yang", "Peng", "Chao", "Gang", "Qiang", "Long",
              "Feng", "Kai", "Yu", "Zhen", "Hui", "Bin", "Xin", "Jian", "Rui", "Hong", "Wen", "Liang", "Cheng", "Dong",
              "Hai", "Shan"],
        "f": ["Fang", "Jing", "Li", "Na", "Min", "Yan", "Ying", "Xiu", "Mei", "Lan", "Hua", "Ling", "Ting", "Xue", "Juan",
              "Qian", "Yue", "Lin", "Dan", "Yun", "Jia", "Ning", "Lu", "Shu", "Xia", "Hui", "Wen", "Zhi", "Rong", "Qing"]}},
    "JP": {"label": "Japan", "currency": "JP\u00a5", "names": {
        "m": ["Haruto", "Sota", "Yuto", "Ren", "Takumi", "Kenta", "Daiki", "Shota", "Ryo", "Hiroshi", "Takeshi", "Kaito",
              "Riku", "Yuki", "Kenji", "Naoki", "Kazuki", "Sho", "Tatsuya", "Yusuke"],
        "f": ["Yui", "Hina", "Aoi", "Sakura", "Yuna", "Mio", "Rin", "Haruka", "Ayaka", "Misaki", "Nanami", "Emi",
              "Kana", "Yoko", "Mai", "Saki", "Natsuki", "Asuka", "Akari", "Riko"]}},
    "AE": {"label": "UAE", "currency": "AED ", "names": {
        "m": ["Mohammed", "Ahmed", "Omar", "Khalid", "Saeed", "Rashid", "Hamdan", "Yousef", "Faisal", "Ali", "Rahul",
              "Arjun", "Vikram", "Joseph", "Ramon", "Bilal", "Tariq", "James", "Imran", "Hassan"],
        "f": ["Fatima", "Mariam", "Aisha", "Noora", "Shamma", "Hessa", "Layla", "Sara", "Reem", "Amna", "Priya",
              "Anjali", "Maria", "Grace", "Zainab", "Huda", "Divya", "Joy", "Nadia", "Rania"]}},
    "SG": {"label": "Singapore", "currency": "S$", "names": {
        "m": ["Wei Jie", "Jun Hao", "Darren", "Marcus", "Ryan", "Muhammad", "Hafiz", "Arjun", "Ravi", "Ethan", "Jayden",
              "Kelvin", "Zhi Hao", "Irfan", "Bryan", "Sean", "Daniel", "Aloysius", "Hariz", "Vikram"],
        "f": ["Hui Min", "Xin Yi", "Jia Hui", "Rachel", "Michelle", "Nur", "Siti", "Aisyah", "Priya", "Divya", "Chloe",
              "Charmaine", "Shi Min", "Farah", "Sarah", "Vanessa", "Cheryl", "Kavitha", "Joanne", "Natasha"]}},
    "AU": {"label": "Australia", "currency": "A$", "names": {
        "m": ["Jack", "Oliver", "William", "Noah", "Thomas", "Lachlan", "Cooper", "Riley", "Liam", "Ethan", "Harrison",
              "Mitchell", "Nguyen", "Arjun", "Ahmed", "Lucas", "Zac", "Josh", "Kai", "Daniel"],
        "f": ["Charlotte", "Olivia", "Amelia", "Isla", "Mia", "Chloe", "Sophie", "Zoe", "Ruby", "Matilda", "Jessica",
              "Emily", "Grace", "Linh", "Priya", "Aisha", "Sienna", "Georgia", "Hannah", "Ella"]}},
    "BR": {"label": "Brazil", "currency": "R$", "names": {
        "m": ["Joao", "Pedro", "Lucas", "Gabriel", "Matheus", "Rafael", "Gustavo", "Felipe", "Bruno", "Thiago", "Diego",
              "Leonardo", "Rodrigo", "Caio", "Vinicius", "Marcelo", "Andre", "Paulo", "Eduardo", "Henrique"],
        "f": ["Maria", "Ana", "Julia", "Beatriz", "Mariana", "Larissa", "Camila", "Fernanda", "Leticia", "Gabriela",
              "Amanda", "Bruna", "Isabela", "Luana", "Carolina", "Juliana", "Patricia", "Aline", "Rafaela", "Vitoria"]}},
}
NAMES_IN = REGIONS["IN"]["names"]["m"] + REGIONS["IN"]["names"]["f"]
INITIALS = "KSMRBDPGTNAJLVCH"
MALE = {"m", "male", "man", "men", "boy"}
FEMALE = {"f", "female", "woman", "women", "girl"}


def region_of(customer):
    """The region preset for a customer, or None. "locale": "IN" still works as an alias of "region": "IN"."""
    code = (customer.get("region") or customer.get("locale") or "").strip().upper()
    code = {"GB": "UK"}.get(code, code)
    if code and code not in REGIONS:
        raise PanelError("unknown region %r: use one of %s, or leave it out and set currency and names yourself"
                         % (code, ", ".join(sorted(REGIONS))))
    return REGIONS.get(code)


def _spread(items, n, rng):
    """n values dealt from items by their shares (exact quotas), in random order."""
    out = []
    for it, k in zip(items, _quota(items, n)):
        out += [it] * k
    rng.shuffle(out)
    return out


INTENT_LABELS = {1: "definitely not", 2: "probably not", 3: "not sure", 4: "probably would", 5: "definitely would"}
# Share of stated intent that usually turns into a real purchase. Starting values only, a common market-research
# rule of thumb, NOT a law: override in customer.json "intent_weights" once you have real sales to compare.
INTENT_WEIGHTS = {"5": 0.75, "4": 0.25, "3": 0.10, "2": 0.0, "1": 0.0}
SKEPTIC_SHARE = 0.2
REASONS = ["price", "habit", "need", "trust", "quality", "convenience", "timing", "values", "other"]
ANSWER_FIELDS = {"id", "buys", "reason_code", "reason"}
WAVE = 10


class PanelError(Exception):
    pass


# ── dealing ─────────────────────────────────────────────────────────────────────
def _quota(items, n, key="share"):
    """Split n across items by their shares, exactly (largest remainder)."""
    total = sum(float(it.get(key, 1)) for it in items) or 1.0
    raw = [n * float(it.get(key, 1)) / total for it in items]
    counts = [int(r) for r in raw]
    order = sorted(range(len(items)), key=lambda i: raw[i] - counts[i], reverse=True)
    for i in order[: n - sum(counts)]:
        counts[i] += 1
    return counts


def unsourced(c):
    """Warnings for market facts or reviews without a source link: buyers are told these are real."""
    m = c.get("market") or {}
    out = []
    for kind in ("facts", "reviews"):
        k = sum(1 for x in m.get(kind) or [] if not str(x.get("source", "")).strip())
        if k:
            out.append("%d market %s have no 'source' link. Buyers are told these are real: add links, or remove them." % (k, kind))
    return out


def validate_customer(c):
    for k in ("business", "target", "segments", "behaviours", "objections"):
        if k not in c or c[k] in ("", [], None):
            raise PanelError("customer.json needs '%s'" % k)
    for s in c["segments"]:
        if "name" not in s or "income" not in s or len(s["income"]) != 2:
            raise PanelError("every segment needs a name and an income [low, high]")
    for b in c["behaviours"]:
        if "name" not in b:
            raise PanelError("every behaviour needs a name")
    region_of(c)
    for g in c.get("genders") or []:
        if "name" not in g:
            raise PanelError("every gender needs a name")
    for g in c.get("age_groups") or []:
        if "name" not in g or len(g.get("range") or []) != 2 or g["range"][0] > g["range"][1]:
            raise PanelError("every age group needs a name and a range [youngest, oldest]")
    for lg in c.get("languages") or []:
        if "name" not in lg:
            raise PanelError("every language needs a name and a share")
    m = c.get("market") or {}
    if not isinstance(m, dict):
        raise PanelError("'market' must be an object with 'facts' and/or 'reviews'")
    for f in m.get("facts") or []:
        if not (isinstance(f, dict) and str(f.get("text", "")).strip()):
            raise PanelError("every market fact needs a 'text' (and ideally a 'source' link)")
    for rv in m.get("reviews") or []:
        if not (isinstance(rv, dict) and str(rv.get("text", "")).strip()):
            raise PanelError("every review needs a 'text' (and ideally 'about', 'stars' and a 'source' link)")
    for dim in c.get("dimensions") or []:
        if "name" not in dim or not dim.get("values") or any("name" not in v for v in dim["values"]):
            raise PanelError("every dimension needs a name and values, each with a name and a share")


SIZES = {"small": 20, "medium": 100, "large": 250}


def pick_segments(customer, only):
    """Keep only the named segments (categories), e.g. only="Category A,Category B". Case-insensitive."""
    if not only:
        return customer
    want = [x.strip().lower() for x in only.split(",") if x.strip()]
    def matches(w, seg):
        name = seg["name"].lower()
        return name == w or name.split(":")[0].strip() == w  # "Category A" matches "Category A: HNI buyers"

    picked, missing = [], []
    for w in want:
        hits = [seg for seg in customer["segments"] if matches(w, seg)]
        if not hits:
            missing.append(w)
        picked += [h for h in hits if h not in picked]
    if missing:
        raise PanelError("no segment called %s. Segments: %s" % (", ".join(repr(m) for m in missing),
                                                                ", ".join(seg["name"] for seg in customer["segments"])))
    return dict(customer, segments=picked)


def segment_counts(customer, n):
    """Headcount per segment: exact "count"s if every segment has one (n is then their total), else n split by share."""
    segs = customer["segments"]
    has = [("count" in s) for s in segs]
    if any(has) and not all(has):
        raise PanelError("give every segment a 'count', or none of them (then 'share' is used)")
    if all(has):
        counts = [int(s["count"]) for s in segs]
        if any(c < 0 for c in counts) or sum(counts) < 1:
            raise PanelError("segment counts must be 0 or more, with at least 1 buyer in total")
        return counts
    return _quota(segs, n)


def deal(customer, n=100, seed=7):
    """Deal n persona cards. Same customer + n + seed = the same cards, every time.
    If every segment has a "count", those counts are used and n becomes their total."""
    validate_customer(customer)
    if all("count" in s for s in customer["segments"]):
        n = sum(segment_counts(customer, n))
    if n < 1:
        raise PanelError("--n must be at least 1")
    rng = random.Random(seed)
    age = customer.get("age", [25, 45])
    segs = []
    for s, k in zip(customer["segments"], segment_counts(customer, n)):
        segs += [s] * k
    behs = []
    for b, k in zip(customer["behaviours"], _quota(customer["behaviours"], n)):
        behs += [b] * k
    rng.shuffle(segs)
    rng.shuffle(behs)
    reg = region_of(customer)
    if customer.get("names"):
        pools = {"m": list(customer["names"]), "f": list(customer["names"])}
    elif reg:
        pools = {k: list(v) for k, v in reg["names"].items()}
    else:
        pools = {"m": FIRST_NAMES[:], "f": FIRST_NAMES[:]}
    pools["any"] = list(dict.fromkeys(pools["m"] + pools["f"]))
    objections = customer["objections"]
    habits = customer.get("habits") or []
    genders = _spread(customer["genders"], n, rng) if customer.get("genders") else [None] * n
    ages = _spread(customer["age_groups"], n, rng) if customer.get("age_groups") else [None] * n
    dims = [(dim["name"], _spread(dim["values"], n, rng)) for dim in customer.get("dimensions") or []]
    used = set()

    def pick_name(g):
        key = "any"
        if g is not None:
            gn = str(g.get("name", "")).strip().lower()
            key = "m" if gn in MALE else "f" if gn in FEMALE else "any"
        pool = [x for x in pools[key] if x not in used]
        if pool:
            nm = pool[rng.randrange(len(pool))]
        else:
            # Pool used up: add a surname initial ("Aarav K."), the way people tell two Aaravs apart.
            nm = None
            for letter in INITIALS:
                cand = ["%s %s." % (x, letter) for x in pools[key] if "%s %s." % (x, letter) not in used]
                if cand:
                    nm = cand[rng.randrange(len(cand))]
                    break
            k = 2
            while nm is None:
                cand = ["%s %d" % (x, k) for x in pools[key] if "%s %d" % (x, k) not in used]
                if cand:
                    nm = cand[rng.randrange(len(cand))]
                k += 1
        used.add(nm)
        return nm

    langs = _spread(customer["languages"], n, rng) if customer.get("languages") else [None] * n
    reviews = (customer.get("market") or {}).get("reviews") or []

    def reviews_for(b):
        # Careful shoppers read more reviews; plenty of people read none.
        if not reviews:
            return []
        careful = any(w in (b.get("name", "") + " " + b.get("how", "")).lower() for w in ("review", "research", "compare"))
        k = min(len(reviews), 3 if careful else rng.choice([0, 0, 1, 2]))
        return sorted(rng.sample(range(len(reviews)), k))

    skeptic = float(customer.get("skeptic_share", SKEPTIC_SHARE))
    open_ids = set(rng.sample(range(n), int(round(n * max(0.0, min(1.0, skeptic))))))
    cards = []
    for i in range(n):
        s, b = segs[i], behs[i]
        lo, hi = float(s["income"][0]), float(s["income"][1])
        cards.append({
            "id": "P%03d" % (i + 1),
            "name": pick_name(genders[i]),
            "age": rng.randint(int(ages[i]["range"][0]), int(ages[i]["range"][1])) if ages[i] else rng.randint(int(age[0]), int(age[1])),
            "gender": genders[i]["name"] if genders[i] else "",
            "age_group": ages[i]["name"] if ages[i] else "",
            "traits": {dn: vals[i]["name"] for dn, vals in dims},
            "language": langs[i]["name"] if langs[i] else (customer.get("language") or ""),
            "segment": s["name"],
            "income": int(round(rng.uniform(lo, hi), -3)),
            "behaviour": b["name"],
            "behaviour_how": b.get("how", ""),
            "objection": "" if i in open_ids else objections[rng.randrange(len(objections))],
            "habit": habits[rng.randrange(len(habits))] if habits else "",
            "reviews": reviews_for(b),
        })
    return cards


# ── state ───────────────────────────────────────────────────────────────────────
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


def init(d, customer_path, pitch_path, n=100, seed=None, only=None):
    try:
        customer = _read_json(customer_path)
    except FileNotFoundError:
        raise PanelError("no such file: %s" % customer_path)
    try:
        with open(pitch_path, encoding="utf-8") as fh:
            pitch = fh.read().strip()
    except FileNotFoundError:
        raise PanelError("no such file: %s (write the pitch first: what you sell, the price, where)" % pitch_path)
    if not pitch:
        raise PanelError("the pitch is empty")
    if seed is None:
        seed = random.SystemRandom().randrange(1, 10 ** 6)
    customer = pick_segments(customer, only)
    cards = deal(customer, n, seed)
    n = len(cards)
    _write_json(_path(d, "panel.json"), {"n": n, "seed": seed, "customer": customer, "pitch": pitch})
    _write_json(_path(d, "personas.json"), cards)
    os.makedirs(_path(d, "briefs"), exist_ok=True)
    os.makedirs(_path(d, "answers"), exist_ok=True)
    return cards


def load_state(d):
    try:
        return _read_json(_path(d, "panel.json")), _read_json(_path(d, "personas.json"))
    except FileNotFoundError:
        raise PanelError("no panel in %s: run init first" % d)


BRIEF = """You are a simulated buyer on a consumer panel. A founder wants to know, before spending any money, whether real people like you would buy. Your answer is only useful if it is honest: most people do not buy most things, and a polite yes is worse than a clear no.

=== WHO YOU ARE ===
{name}, {age}{gender_part}. {segment}. You earn about {cur}{income_txt} a year{where_line}.
How you buy: {behaviour}. {behaviour_how}
{habit_line}{traits_line}{objection_line}
You are one of these people: {target}.
These facts are context about one specific person's life, not a script. Act as this individual would, never as a stereotype of any group.
=== END ===
{market_block}
=== WHAT IS BEING OFFERED (you see it for the first time, the way a passer-by or a scroller would) ===
{pitch}
=== END ===

Before you answer, picture the real moment: you are busy, you have other options, and spending money means not spending it on something else. Decide as {name} would, with {name}'s money, habits and doubts, in a normal week. Do not be agreeable. Do not invent facts about the business beyond what is written above.{language_line}

Create the file {out} with your file-writing tool (do not just print the answer in your reply) containing ONLY this JSON, no markdown fence, nothing else:
{{
  "id": "{id}",
  "intent": 1 to 5 (1 definitely not, 2 probably not, 3 not sure, 4 probably would, 5 definitely would),
  "buys": true only if intent is 4 or 5, else false,
  "purchases_first_month": how many times you would buy in the first month (0 if you would not buy),
  "reason_code": one of {reasons},
  "reason": "why, in one or two sentences, in your own voice",{reason_en_line}
  "objection": "the doubt that weighs most for you, in your own words",
  "unprompted_doubt": "a doubt or question you have that nobody has mentioned to you, in your own words, or empty",
  "would_change_my_mind": "the one thing that would flip your answer, or empty",
  "price_too_cheap": the price at which it would seem too cheap to be any good (a number),
  "price_cheap": the price at which it would feel like a bargain (a number),
  "price_expensive": the price at which it starts to feel expensive but you might still buy (a number),
  "price_too_expensive": the price at which you would not buy it at all (a number)
}}
"""


def write_briefs(d, wave=WAVE):
    state, cards = load_state(d)
    target = state["customer"]["target"]
    todo = []
    for c in cards:
        out = _path(d, "answers", c["id"] + ".json")
        if _answer_ok(out, c["id"]) is None:
            continue
        brief = BRIEF.format(pitch=state["pitch"], target=target, out=os.path.abspath(out),
                             habit_line=("Your day: %s.\n" % c["habit"]) if c.get("habit") else "",
                             cur=_currency(state["customer"]),
                             gender_part=(", %s" % c["gender"]) if c.get("gender") else "",
                             traits_line="".join("Your %s: %s.\n" % (k, v) for k, v in (c.get("traits") or {}).items()),
                             language_line=_language_line(c.get("language", "")),
                             reason_en_line=("\n  \"reason_en\": \"the same reason translated into English\","
                                             if _foreign(c.get("language", "")) else ""),
                             market_block=_market_block(state["customer"], c), income_txt=_money(c["income"], state["customer"]),
                             where_line=(", in %s" % state["customer"]["where"]) if state["customer"].get("where") else "",
                             objection_line=('The first thing that comes to mind when you hear an offer like this: "%s"' % c["objection"])
                             if c.get("objection") else "Nobody has told you what to doubt. React the way you really would.",
                             reasons=" / ".join(REASONS), **c)
        bp = _path(d, "briefs", c["id"] + ".md")
        with open(bp, "w", encoding="utf-8") as fh:
            fh.write(brief)
        todo.append((c["id"], os.path.abspath(bp)))
    waves = [todo[i:i + wave] for i in range(0, len(todo), wave)]
    return waves


def _answer_ok(path, pid):
    """None if the answer file is good, else a short problem string."""
    if not os.path.exists(path):
        return "missing"
    try:
        a = _read_json(path)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return "not valid JSON"
    if not isinstance(a, dict):
        return "not a JSON object"
    missing = ANSWER_FIELDS - set(a)
    if missing:
        return "missing " + ", ".join(sorted(missing))
    if a.get("id") != pid:
        return "id is %r, expected %s" % (a.get("id"), pid)
    if not isinstance(a.get("buys"), bool):
        return "'buys' must be true or false"
    if not isinstance(a.get("reason"), str) or not a["reason"].strip():
        return "'reason' must be text"
    if "intent" in a:
        if isinstance(a["intent"], bool) or a["intent"] not in (1, 2, 3, 4, 5):
            return "'intent' must be a whole number 1 to 5"
        if a["buys"] != (a["intent"] >= 4):
            return "'buys' must be true exactly when intent is 4 or 5"
    if a.get("reason_code") not in REASONS:
        return "reason_code %r is not one of %s" % (a.get("reason_code"), ", ".join(REASONS))
    return None


def save(d, pid, text):
    """File a buyer's OWN answer that it printed instead of writing. Never used to answer for a buyer."""
    _, cards = load_state(d)
    if pid not in {c["id"] for c in cards}:
        raise PanelError("no buyer %s on this panel" % pid)
    start = text.find("{")
    if start < 0:
        raise PanelError("no JSON object in the reply")
    try:
        obj, _ = json.JSONDecoder().raw_decode(text[start:])
    except json.JSONDecodeError as e:
        raise PanelError("the reply's JSON does not parse: %s" % e)
    path = _path(d, "answers", pid + ".json")
    _write_json(path, obj)
    prob = _answer_ok(path, pid)
    if prob:
        os.remove(path)
        raise PanelError("%s's answer is not valid (%s); re-run its brief instead" % (pid, prob))
    return path


def check(d):
    _, cards = load_state(d)
    probs = []
    for c in cards:
        p = _answer_ok(_path(d, "answers", c["id"] + ".json"), c["id"])
        if p:
            probs.append((c["id"], p))
    return probs


# ── tally ───────────────────────────────────────────────────────────────────────
def _rate(rows):
    return (sum(1 for r in rows if r["buys"]) / len(rows)) if rows else 0.0


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _currency(customer):
    reg = region_of(customer)
    return customer.get("currency") or (reg["currency"] if reg else "$")


def _foreign(lang):
    lang = (lang or "").strip()
    return bool(lang) and lang.lower() not in ("english", "en")


def _market_block(customer, card):
    """Real, researched market facts every buyer knows, plus the few real reviews this buyer has read."""
    m = customer.get("market") or {}
    facts = [f["text"].strip() for f in (m.get("facts") or [])][:8]
    allrev = m.get("reviews") or []
    seen = [allrev[i] for i in card.get("reviews") or [] if i < len(allrev)]
    if not facts and not seen:
        return ""
    out = ["", "=== WHAT YOU ALREADY KNOW (real facts and real reviews, researched by the founder) ==="]
    if facts:
        out.append("How people around you buy things like this:")
        out += ["- %s" % f for f in facts]
    if seen:
        out.append("Reviews you have read of other options:")
        for rv in seen:
            stars = rv.get("stars")
            star_txt = ("%s/5 " % stars) if stars not in (None, "") else ""
            about = (" about %s" % rv["about"]) if rv.get("about") else ""
            out.append('- %sreview%s: "%s"' % (star_txt, about, rv["text"].strip()))
    elif allrev:
        out.append("You have not read any reviews of other options.")
    out.append("=== END ===")
    return "\n".join(out) + "\n"


def _language_line(lang):
    if not _foreign(lang):
        return ""
    lang = lang.strip()
    return ("\nYou think and talk in %s. Write reason, objection, unprompted_doubt and would_change_my_mind in %s,"
            " the way you would really say it (mixing in English words is fine if that is how you talk)." % (lang, lang))


def _money(v, customer):
    """Group digits the way the reader expects: 13,21,000 for India, 1,321,000 elsewhere."""
    v = int(round(float(v)))
    reg = region_of(customer)
    if not reg or reg.get("grouping") != "lakh":
        return "{:,}".format(v)
    t = str(abs(v))
    head, tail = t[:-3], t[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ("-" if v < 0 else "") + ",".join(parts + [tail]) if parts else ("-" if v < 0 else "") + tail


def _wilson(k, n, z=1.645):
    """90% Wilson interval for k successes out of n."""
    if not n:
        return 0.0, 0.0
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return max(0.0, mid - half), min(1.0, mid + half)


def _price_num(v):
    """6.5, "6.50", "₹2,50,000" and "$6.50" all work."""
    if isinstance(v, str):
        v = re.sub(r"[^0-9.]", "", v)
    return _num(v) if v not in (None, "") else None


def _price_text(price, res):
    """6.5 -> 6.50, 250000 -> 2,50,000 (India) or 250,000."""
    if float(price) != int(price):
        return "%.2f" % price
    return _money(price, res.get("customer_for_format") or {})


def _quote(r):
    """The buyer's reason as written, with the English translation when they answered in another language."""
    en = (r.get("reason_en") or "").strip()
    return r["reason"] + (" [English: %s]" % en if en and en != r["reason"] else "")


def _group_reviews(rows):
    out = {}
    for r in rows:
        k = len(r.get("reviews") or [])
        out.setdefault("read no reviews" if k == 0 else "read %d review%s" % (k, "" if k == 1 else "s"), []).append(r)
    return sorted(((k, len(v), _rate(v)) for k, v in out.items()), key=lambda t: t[0])


def _group_trait(rows, dn):
    out = {}
    for r in rows:
        v = (r.get("traits") or {}).get(dn)
        if v is not None:
            out.setdefault(v, []).append(r)
    return sorted(((k, len(v), _rate(v)) for k, v in out.items()), key=lambda t: -t[2])


def tally(d):
    state, cards = load_state(d)
    by_id = {c["id"]: c for c in cards}
    rows, skipped = [], []
    for c in cards:
        path = _path(d, "answers", c["id"] + ".json")
        p = _answer_ok(path, c["id"])
        if p:
            skipped.append((c["id"], p))
            continue
        a = _read_json(path)
        rows.append(dict(by_id[c["id"]], **{k: v for k, v in a.items() if k != "id"}, id=c["id"]))
    if not rows:
        raise PanelError("no valid answers yet: run the briefs first (panel.py prompts)")

    def group(key):
        out = {}
        for r in rows:
            out.setdefault(r[key], []).append(r)
        return sorted(((k, len(v), _rate(v)) for k, v in out.items()), key=lambda t: -t[2])

    # income in thirds of the buyers who answered (bands can differ a little between panels)
    cur = _currency(state["customer"])
    incomes = sorted(r["income"] for r in rows)
    cut1, cut2 = incomes[len(incomes) // 3], incomes[2 * len(incomes) // 3]
    for r in rows:
        r["income_band"] = ("under %s%s" % (cur, _money(cut1, state["customer"]))) if r["income"] < cut1 else (
            ("%s%s and up" % (cur, _money(cut2, state["customer"]))) if r["income"] >= cut2 else "%s%s to %s%s" % (cur, _money(cut1, state["customer"]), cur, _money(cut2, state["customer"])))

    no = [r for r in rows if not r["buys"]]
    yes = [r for r in rows if r["buys"]]

    def reasons(rs):
        out = {}
        for r in rs:
            out.setdefault(r["reason_code"], []).append(r)
        return sorted(((k, v) for k, v in out.items()), key=lambda kv: -len(kv[1]))

    def mean(vals):
        vals = [v for v in vals if v is not None]
        return sum(vals) / len(vals) if vals else None

    weights = dict(INTENT_WEIGHTS)
    weights.update({str(k): float(v) for k, v in (state["customer"].get("intent_weights") or {}).items()})
    rated = [r for r in rows if r.get("intent") in (1, 2, 3, 4, 5)]
    intent_counts = {str(k): sum(1 for r in rated if r["intent"] == k) for k in range(1, 6)}
    realistic = (sum(weights.get(str(r["intent"]), 0.0) for r in rated) / len(rated)) if rated else None
    lo, hi = _wilson(len(yes), len(rows))
    price = _price_num(state["customer"].get("price"))
    revenue_per_100 = None
    if price is not None:
        # Same weighting as the realistic estimate: each answer counts by the share of its stated intent that
        # becomes a real sale, times how often that buyer says they would buy (at least once if they buy at all).
        base = rated if rated else rows
        def w(r):
            return weights.get(str(r["intent"]), 0.0) if r in rated else (1.0 if r["buys"] else 0.0)
        units = sum(w(r) * max(_num(r.get("purchases_first_month")) or 0.0, 1.0) for r in base)
        revenue_per_100 = units / len(base) * 100 * price
    res = {
        "business": state["customer"]["business"], "seed": state["seed"], "dealt": len(cards),
        "answered": len(rows), "skipped": skipped, "buys": len(yes), "passes": len(no),
        "buy_rate": len(yes) / len(rows), "buy_rate_interval_90": [lo, hi],
        "price": price, "revenue_first_month_per_100_reached": revenue_per_100,
        "customer_for_format": {k: state["customer"][k] for k in ("region", "locale") if k in state["customer"]},
        "intent_counts": intent_counts, "intent_answers": len(rated), "intent_weights": weights, "realistic_rate": realistic, "currency": cur,
        "unprompted": [(r["id"], r["unprompted_doubt"]) for r in rows if (r.get("unprompted_doubt") or "").strip()],
        "by_segment": group("segment"), "by_behaviour": group("behaviour"), "by_income": group("income_band"),
        "by_gender": group("gender") if any(r.get("gender") for r in rows) else [],
        "by_age_group": group("age_group") if any(r.get("age_group") for r in rows) else [],
        "by_language": group("language") if len({r.get("language", "") for r in rows}) > 1 else [],
        "by_reviews_read": _group_reviews(rows) if (state["customer"].get("market") or {}).get("reviews") else [],
        "by_trait": {dn: _group_trait(rows, dn) for dn in sorted({k for r in rows for k in (r.get("traits") or {})})},
        "why_not": [(k, len(v), [_quote(r) for r in v[:2]], [r["id"] for r in v[:2]]) for k, v in reasons(no)],
        "why_yes": [(k, len(v), [_quote(r) for r in v[:2]], [r["id"] for r in v[:2]]) for k, v in reasons(yes)],
        "flip": [r["would_change_my_mind"] for r in no if (r.get("would_change_my_mind") or "").strip()],
        "purchases_first_month_per_buyer": mean([_num(r.get("purchases_first_month")) for r in yes]),
        "price_answers": sum(1 for r in rows if all(_num(r.get(k)) is not None for k in
                                                     ("price_too_cheap", "price_cheap", "price_expensive", "price_too_expensive"))),
    }
    return res


def results_md(res):
    pct = lambda v: "%.0f%%" % (v * 100)
    L = ["# Buyer panel: %s" % res["business"], ""]
    L.append("**%d buy · %d pass** (%s buy) out of %d simulated buyer%s. Seed %s, so the same cards can be dealt again."
             % (res["buys"], res["passes"], pct(res["buy_rate"]), res["answered"], "" if res["answered"] == 1 else "s", res["seed"]))
    lo, hi = res.get("buy_rate_interval_90", [None, None])
    if lo is not None:
        L.append("")
        L.append("With this many buyers, the buy rate could reasonably be anywhere from %s to %s (90%% range)." % (pct(lo), pct(hi)))
    if res.get("realistic_rate") is not None:
        ic = res["intent_counts"]
        L.append("")
        L.append("**Realistic estimate: about %s would actually buy.** Stated intent: %s definitely, %s probably, %s not sure,"
                 " %s probably not, %s definitely not. Only part of stated intent turns into real purchases, so each answer"
                 " is weighted (%s). These weights are starting guesses: replace them with your own real numbers."
                 % (pct(res["realistic_rate"]), ic["5"], ic["4"], ic["3"], ic["2"], ic["1"],
                    ", ".join("%s=%s" % (k, res["intent_weights"][k]) for k in ("5", "4", "3", "2", "1"))))
        if res.get("intent_answers", res["answered"]) < res["answered"]:
            L.append("Only %d of the %d answers gave an intent score (older answer format), so the realistic estimate"
                     " is based on those %d." % (res["intent_answers"], res["answered"], res["intent_answers"]))
    if res["skipped"]:
        L.append("")
        L.append("%d of %d buyers have no valid answer and are left out: %s." % (
            len(res["skipped"]), res["dealt"], ", ".join("%s (%s)" % s for s in res["skipped"][:10])))
    L.append("")
    L.append("These are simulated buyers, not customers. Use this to find objections and weak spots, then confirm the"
             " big ones with real people before you spend.")
    if res.get("revenue_first_month_per_100_reached") is not None:
        L.append("")
        L.append("**Money:** at %s%s, every 100 people of this type who see the offer would bring in about **%s%s in the"
                 " first month** (realistic buyers x purchases per buyer x price). Treat it as a ceiling to test, not a forecast."
                 % (res.get("currency", "$"), _price_text(res["price"], res), res.get("currency", "$"),
                    _money(res["revenue_first_month_per_100_reached"], res.get("customer_for_format") or {})))
    tables = [("By segment", res["by_segment"]), ("By buying behaviour", res["by_behaviour"]), ("By income", res["by_income"])]
    if res.get("by_gender"):
        tables.append(("By gender", res["by_gender"]))
    if res.get("by_age_group"):
        tables.append(("By age group", res["by_age_group"]))
    if res.get("by_language"):
        tables.append(("By language", res["by_language"]))
    if res.get("by_reviews_read"):
        tables.append(("By reviews read", res["by_reviews_read"]))
    for dn, rows_ in sorted((res.get("by_trait") or {}).items()):
        tables.append(("By %s" % dn, rows_))
    for title, rows_ in tables:
        L += ["", "## %s" % title, "", "| group | buyers | buy rate |", "| --- | ---: | ---: |"]
        for k, n, r in rows_:
            L.append("| %s | %d | %s%s |" % (k or "(not set)", n, pct(r), "  (thin)" if n < 8 else ""))
    L += ["", "## Why they pass", "", "| reason | buyers | in their words |", "| --- | ---: | --- |"]
    for k, n, quotes, ids in res["why_not"]:
        L.append("| %s | %d | %s |" % (k, n, " · ".join('"%s" (%s)' % (q.replace("|", "/"), i) for q, i in zip(quotes, ids))))
    L += ["", "## Why they buy", "", "| reason | buyers | in their words |", "| --- | ---: | --- |"]
    for k, n, quotes, ids in res["why_yes"]:
        L.append("| %s | %d | %s |" % (k, n, " · ".join('"%s" (%s)' % (q.replace("|", "/"), i) for q, i in zip(quotes, ids))))
    if res.get("unprompted"):
        L += ["", "## Doubts nobody planted", "",
              "Raised by buyers on their own. These are the ones your objection list missed. Add the repeat ones to customer.json.", ""]
        for pid, t in res["unprompted"][:15]:
            L.append("- %s (%s)" % (t, pid))
    if res["flip"]:
        L += ["", "## What would flip a no", ""]
        for f in res["flip"][:12]:
            L.append("- %s" % f)
    if res["purchases_first_month_per_buyer"] is not None:
        L += ["", "Buyers say they would buy **%.1f times** in the first month on average." % res["purchases_first_month_per_buyer"]]
    if res["price_answers"]:
        L += ["", "%d buyer%s gave all four price answers. Run founder-pricing's van_westendorp.py on the answers folder." % (res["price_answers"], "" if res["price_answers"] == 1 else "s")]
    return "\n".join(L) + "\n"


def compare(dir_a, dir_b):
    """Compare two panels (two pitches dealt with the same seed). Returns markdown."""
    for x in (dir_a, dir_b):
        if not os.path.exists(_path(x, "results.json")):
            raise PanelError("no results in %s: run tally on it first (panel.py --dir %s tally)" % (x, x))
    ra, rb = (_read_json(_path(x, "results.json")) for x in (dir_a, dir_b))
    sa, sb = (_read_json(_path(x, "panel.json")) for x in (dir_a, dir_b))
    pct = lambda v: "-" if v is None else "%.0f%%" % (v * 100)
    L = ["# Pitch A vs pitch B", ""]
    if sa["seed"] != sb["seed"] or sa["n"] != sb["n"]:
        L += ["**Warning:** the two panels used different buyers (seed or size differ). Re-run B with --seed %s --n %s"
              " so the only difference is the pitch." % (sa["seed"], sa["n"]), ""]
    L += ["| | A | B |", "| --- | ---: | ---: |",
          "| buy rate | %s | %s |" % (pct(ra["buy_rate"]), pct(rb["buy_rate"])),
          "| realistic estimate | %s | %s |" % (pct(ra.get("realistic_rate")), pct(rb.get("realistic_rate")))]
    seg_b = {k: (n, r) for k, n, r in rb["by_segment"]}
    L += ["", "## By segment", "", "| segment | A | B | change |", "| --- | ---: | ---: | ---: |"]
    for k, n, r in ra["by_segment"]:
        if k in seg_b:
            L.append("| %s | %s | %s | %+.0f pts |" % (k, pct(r), pct(seg_b[k][1]), (seg_b[k][1] - r) * 100))
    # who flipped, buyer by buyer (same seed means same people)
    def answers(d):
        out = {}
        folder = _path(d, "answers")
        for f in os.listdir(folder):
            if f.endswith(".json"):
                pid = f[:-5]
                if _answer_ok(_path(folder, f), pid) is None:
                    out[pid] = _read_json(_path(folder, f))
        return out
    aa, ab = answers(dir_a), answers(dir_b)
    won = [i for i in aa if i in ab and not aa[i]["buys"] and ab[i]["buys"]]
    lost = [i for i in aa if i in ab and aa[i]["buys"] and not ab[i]["buys"]]
    L += ["", "%d buyers switched to yes with B, %d switched to no." % (len(won), len(lost))]
    for i in won[:5]:
        L.append("- won %s: \"%s\"" % (i, ab[i]["reason"]))
    for i in lost[:5]:
        L.append("- lost %s: \"%s\"" % (i, ab[i]["reason"]))
    L += ["", "A difference of under about 10 points on 100 buyers can be noise. Test the winner on real people."]
    return "\n".join(L) + "\n"


def _esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def results_html(res):
    """One self-contained page: headline numbers, a bar per group, reasons and doubts. Opens in any browser."""
    pct = lambda v: "%.0f%%" % (v * 100)
    lo, hi = res.get("buy_rate_interval_90", [0, 0])
    cards = [("Raw buy rate", pct(res["buy_rate"]), "upper bound; range %s to %s" % (pct(lo), pct(hi)))]
    if res.get("realistic_rate") is not None:
        cards.insert(0, ("Realistic estimate", pct(res["realistic_rate"]), "weighted by stated intent"))
    if res.get("revenue_first_month_per_100_reached") is not None:
        cards.append(("First-month revenue", "%s%s" % (res.get("currency", "$"), _money(
            res["revenue_first_month_per_100_reached"], res.get("customer_for_format") or {})), "per 100 people reached"))
    cards.append(("Buyers", "%d" % res["answered"], "%d buy, %d pass" % (res["buys"], res["passes"])))
    tables = [("By segment", res["by_segment"]), ("By buying behaviour", res["by_behaviour"]), ("By income", res["by_income"])]
    for key, title in (("by_gender", "By gender"), ("by_age_group", "By age group"), ("by_language", "By language"),
                       ("by_reviews_read", "By reviews read")):
        if res.get(key):
            tables.append((title, res[key]))
    for dn, rows_ in sorted((res.get("by_trait") or {}).items()):
        tables.append(("By %s" % dn, rows_))
    H = ["<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
         "<title>Buyer panel: %s</title><style>" % _esc(res["business"]),
         "body{font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:0 auto;padding:24px;color:#1c2330;background:#fafbfc}",
         "h1{font-size:24px;margin:0 0 4px}h2{font-size:18px;margin:28px 0 10px}.sub{color:#5b6573;font-size:14px}",
         ".cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:18px 0}",
         ".card{background:#fff;border:1px solid #e3e7ec;border-radius:10px;padding:14px}.big{font-size:28px;font-weight:700}",
         ".row{display:grid;grid-template-columns:minmax(120px,38%) 1fr 54px;gap:10px;align-items:center;margin:6px 0;font-size:14px}",
         ".bar{background:#e9edf2;border-radius:6px;height:14px;overflow:hidden}.fill{background:#2f6fde;height:100%}",
         ".thin{color:#8a93a0;font-size:12px}blockquote{margin:8px 0;padding:8px 12px;background:#fff;border-left:3px solid #2f6fde;font-size:14px}",
         ".note{background:#fff6e0;border:1px solid #f1d58a;border-radius:8px;padding:10px 14px;font-size:14px}</style></head><body>",
         "<h1>Buyer panel: %s</h1><div class='sub'>Seed %s · simulated buyers, not customers</div>" % (_esc(res["business"]), _esc(res["seed"])),
         "<div class='cards'>"]
    for t, v, sub in cards:
        H.append("<div class='card'><div class='sub'>%s</div><div class='big'>%s</div><div class='thin'>%s</div></div>" % (_esc(t), _esc(v), _esc(sub)))
    H.append("</div><div class='note'>Use this to find objections and pick between pitches. Confirm the big calls with real"
             " people (a waitlist, a pre-sale, a price on a page) before you spend.</div>")
    for title, rows_ in tables:
        if not rows_:
            continue
        H.append("<h2>%s</h2>" % _esc(title))
        for k, n, r in rows_:
            H.append("<div class='row'><div>%s <span class='thin'>(%d%s)</span></div><div class='bar'><div class='fill' style='width:%.0f%%'></div></div><div>%s</div></div>"
                     % (_esc(k or "(not set)"), n, ", thin" if n < 8 else "", r * 100, pct(r)))
    for title, key in (("Why they pass", "why_not"), ("Why they buy", "why_yes")):
        if res.get(key):
            H.append("<h2>%s</h2>" % title)
            for k, n, quotes, ids in res[key]:
                H.append("<div><b>%s</b> <span class='thin'>%d buyer%s</span></div>" % (_esc(k), n, "" if n == 1 else "s"))
                for q, i in zip(quotes, ids):
                    H.append("<blockquote>%s <span class='thin'>(%s)</span></blockquote>" % (_esc(q), _esc(i)))
    if res.get("unprompted"):
        H.append("<h2>Doubts nobody planted</h2>")
        for pid, t in res["unprompted"][:15]:
            H.append("<blockquote>%s <span class='thin'>(%s)</span></blockquote>" % (_esc(t), _esc(pid)))
    if res.get("flip"):
        H.append("<h2>What would flip a no</h2><ul>")
        H += ["<li>%s</li>" % _esc(f) for f in res["flip"][:12]]
        H.append("</ul>")
    H.append("</body></html>")
    return "\n".join(H) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default=os.path.join("founder", "panel"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init")
    i.add_argument("--customer", required=True)
    i.add_argument("--pitch", required=True)
    i.add_argument("--n", type=int, default=100)
    i.add_argument("--quick", action="store_true", help="20 buyers: a cheap first look (same as --size small)")
    i.add_argument("--size", choices=sorted(SIZES), help="small = 20, medium = 100, large = 250 buyers")
    i.add_argument("--only", help='run only these segments, comma-separated, e.g. "Category A,Category B"')
    i.add_argument("--seed", type=int)
    p = sub.add_parser("prompts")
    p.add_argument("--wave", type=int, default=WAVE)
    sub.add_parser("check")
    sv = sub.add_parser("save")
    sv.add_argument("id")
    t = sub.add_parser("tally")
    t.add_argument("--out")
    sub.add_parser("status")
    cp = sub.add_parser("compare")
    cp.add_argument("a")
    cp.add_argument("b")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "init":
            n = SIZES["small"] if a.quick else SIZES[a.size] if a.size else a.n
            cards = init(a.dir, a.customer, a.pitch, n, a.seed, a.only)
            st, _ = load_state(a.dir)
            print("dealt %d buyers (seed %s) into %s. Next: panel.py prompts" % (len(cards), st["seed"], a.dir))
            for w in unsourced(st["customer"]):
                print("warning: %s" % w, file=sys.stderr)
        elif a.cmd == "prompts":
            waves = write_briefs(a.dir, a.wave)
            n = sum(len(w) for w in waves)
            if not n:
                print("every buyer has a valid answer. Next: panel.py tally")
            else:
                print("%d briefs in %d waves of up to %d. Launch one wave at a time:" % (n, len(waves), a.wave))
                for k, w in enumerate(waves, 1):
                    print("wave %d: %s" % (k, " ".join("%s=%s" % job for job in w)))
        elif a.cmd == "check":
            probs = check(a.dir)
            if not probs:
                print("all answers present and valid")
            for pid, prob in probs:
                print("%s: %s" % (pid, prob))
            return 1 if probs else 0
        elif a.cmd == "save":
            print("saved %s" % save(a.dir, a.id, sys.stdin.read()))
        elif a.cmd == "tally":
            res = tally(a.dir)
            text = results_md(res)
            out = a.out or _path(a.dir, "results.md")
            os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(text)
            _write_json(_path(a.dir, "results.json"), res)
            html = os.path.splitext(out)[0] + ".html"
            with open(html, "w", encoding="utf-8") as fh:
                fh.write(results_html(res))
            print("%d buy · %d pass (%.0f%%). Wrote %s and %s" % (res["buys"], res["passes"], res["buy_rate"] * 100, out, html))
        elif a.cmd == "compare":
            print(compare(a.a, a.b))
        elif a.cmd == "status":
            st, cards = load_state(a.dir)
            probs = check(a.dir)
            print("%d buyers dealt (seed %s), %d answered, %d to go" % (len(cards), st["seed"], len(cards) - len(probs), len(probs)))
    except PanelError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
