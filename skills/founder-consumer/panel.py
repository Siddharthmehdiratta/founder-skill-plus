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
# Market facts per region: how people there pay, save and spend. Each is from an official or named source,
# checked in November 2026. They describe markets, not how a nationality "thinks". Every buyer from that
# region sees them (turn off with "region_facts": false). Refresh them yearly; numbers go stale.
REGION_FACTS = {
    "IN": [
        {"text": "UPI handled 85.5% of all payments by number in the second half of 2025, but only about 9.5% by value: it is how people pay for everyday, small things.",
         "source": "https://www.thestatesman.com/business/upi-dominates-indias-digital-payments-debit-card-usage-declines-sharply-rbi-report-1503595761.html"},
        {"text": "Household debt reached 41.3% of GDP by March 2025, led by consumption loans: many people buy big items on loans and EMIs.",
         "source": "https://www.business-standard.com/economy/news/indias-household-debt-rises-to-41-3-per-cent-of-gdp-rbi-fsr-125123101081_1.html"},
        {"text": "Households' net financial saving was 7.0% of national disposable income in 2024-25, up from 5.8% a year earlier.",
         "source": "https://rbi.org.in/SCRIPTS/AnnualReportPublications.aspx?Id=1462"}],
    "US": [
        {"text": "In 2024, credit cards were used for 35% of payments, debit cards for 30% and cash for 14%; credit card use keeps growing.",
         "source": "https://frbservices.org/news/research/2025-findings-from-the-diary-of-consumer-payment-choice"},
        {"text": "23% of purchases and person-to-person payments were made remotely (online or by phone) in 2024, a share that has risen every year since 2021.",
         "source": "https://frbservices.org/news/fed360/issues/060325/cash-2025-findings-diary-consumer-payment-choice"},
        {"text": "The personal saving rate fell to 3.8% of disposable income in September 2026, a near four-year low: most income is spent.",
         "source": "https://www.bea.gov/taxonomy/term/741"}],
    "UK": [
        {"text": "Card payments were 64% of all UK payments in 2025, and debit cards alone more than half; contactless and phone wallets are everyday habits.",
         "source": "https://www.ukfinance.org.uk/news-and-insight/press-release/digital-payments-continue-grow-mobile-wallets-become-more-popular"},
        {"text": "Cash fell below 10% of UK payments for the first time in 2024.",
         "source": "https://www.ukfinance.org.uk/system/files/2025-10/Payment%20Markets%20Report%20Summary.pdf"}],
    "EU": [
        {"text": "In the euro area, cash was still used for 52% of in-store payments in 2024 (59% in 2022), mostly for small amounts; cards lead for payments over 50 euros.",
         "source": "https://www.ecb.europa.eu/press/pr/date/2024/html/ecb.pr241219~172b929461.en.html"},
        {"text": "62% of euro area consumers said it is important to keep cash as a way to pay.",
         "source": "https://www.ecb.europa.eu/stats/ecb_surveys/space/html/ecb.space2024~19d46f0f17.ro.html"},
        {"text": "Euro area households saved 14.4% of their disposable income in the last quarter of 2025.",
         "source": "https://ec.europa.eu/eurostat/web/products-euro-indicators/w/2-09042026-ap"}],
    "CN": [
        {"text": "Mobile wallets such as Alipay and WeChat Pay made up about 89% of in-store spending in 2025, as reported by Caixin; cards are rarely used.",
         "source": "https://www.caixinglobal.com/2026-05-20/china-leads-world-in-mobile-payment-uptake-as-asia-drives-growth-102445900.html"},
        {"text": "Disposable income per person was 43,377 yuan in 2025 nationwide and 56,502 yuan for urban residents.",
         "source": "https://www.stats.gov.cn/english/PressRelease/202601/t20260120_1962356.html"},
        {"text": "Household bank deposits grew nearly 10% in 2025 while borrowing weakened: people are saving cautiously.",
         "source": "https://www2.yicaiglobal.com/news/china-household-deposits-rise-nearly-10-in-2025-as-borrowing-weakens"}],
    "JP": [
        {"text": "Cashless payments were 58.0% of consumer spending in 2025, up from 16.6% in 2010; cash is still common.",
         "source": "https://www.meti.go.jp/english/press/2026/0331_005.html"},
        {"text": "Credit cards make up most of Japan's cashless payments.",
         "source": "https://trade.gov/country-commercial-guides/japan-financial-technology"}],
}
# Well-studied habits of mind from behavioural economics. Each buyer gets one, so the panel mixes real ways
# people decide. They apply to people everywhere; they are not tied to any country or group.
BIASES = {
    "loss aversion": "Losing money hurts you more than saving the same amount pleases you, so you worry about paying for something that turns out bad.",
    "anchoring": "You judge a price against the first price you saw for something similar.",
    "social proof": "You trust what friends and other buyers do more than what a brand says about itself.",
    "status quo": "You stick with what you already use unless the new option is clearly better.",
    "present bias": "Today's cost feels bigger to you than benefits that come later.",
    "price means quality": "You assume cheap means low quality and a higher price means better.",
    "mental budget": "You keep a rough budget for each kind of spending and dislike going over it.",
    "free is powerful": "Anything free (a trial, a sample, a free extra) feels worth more to you than it really is.",
    "authority": "You give weight to experts, reviews by professionals and well-known names.",
    "choice overload": "When there are many options or details, you put off deciding.",
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


def _age_group_for(customer, age):
    for g in customer.get("age_groups") or []:
        if g["range"][0] <= age <= g["range"][1]:
            return g["name"]
    return ""


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
# What real shoppers check before paying, in any country. Each buyer weighs these against the pitch, and
# names the questions the pitch leaves open. Those become the founder's FAQ and checkout fixes.
PRACTICAL_CHECKS = ["the total cost, including delivery, fees, taxes or add-ons",
                    "how you would pay (and whether your usual way of paying works)",
                    "when and how you would get it, and how much effort that takes",
                    "what happens if it is late, broken or not as described: returns, refunds, cancelling",
                    "warranty, support, and who you would call or message",
                    "who is behind it and whether they will still be around",
                    "what data they collect and what they do with it",
                    "how much of your time it takes to start using it"]
# What business buyers check before they sign, on top of price.
B2B_CHECKS = ["the total cost over a year, including installation, setup, training, maintenance and renewals",
              "the return on the money: what it saves or earns the business, and how fast",
              "who else has to approve it, and whether you can justify it to them",
              "contract terms: minimum period, lock-in, cancelling, payment terms and a proper GST/VAT invoice",
              "support: response times, on-site service, maintenance contract (AMC), warranty and spares",
              "how it fits what the business already uses, and the cost and risk of switching",
              "proof it works: references, case studies, clients like you",
              "whether the supplier is reliable and will still be around"]
QUESTION_TOPICS = [  # first match wins, so the specific topics come first
    ("contract, invoice, AMC and payment terms", ("contract", "invoice", "gst", "credit period", "payment terms", "lock-in",
                                                  "purchase order", "amc", "sla", "maintenance contract", "tender", "quotation")),
    ("data and privacy", ("data", "privacy", "track", "personal info", "collect", "stored", "spam", "see my")),
    ("refunds, cancelling, free trial", ("refund", "return", "cancel", "money back", "guarantee", "unsubscribe", "trial", "auto-renew", "charge me")),
    ("how to pay", ("upi", "card", "emi", "instal", "cash", "wallet", "paypal", "wechat", "alipay", "pay with", "pay in", "pay by", "se pay")),
    ("price, fees and discounts", ("free version", "free tier", "what's free", "is free", "lose if", "fee", "cost", "price", "tax", "gst", "vat", "hidden", "extra", "discount", "student", "cheaper", "rupee",
                                   "kitna", "paisa", "sasta", "mehenga", "how much", "per month", "monthly", "plan", "offer", "₹", "$", "€")),
    ("why this over free or current options", ("better than", "compare", " vs", "versus", "free app", "free option", "already have",
                                               "different from", "kaise better", "why should", "instead of", "screen time")),
    ("how it works day to day", ("disable", "hold", "bypass", "turn it off", "turn off", "lock", "uninstall", "setup", "set up", "install", "how does",
                                 "how do i", "device", "work with", "compatible", "portion", "size", "menu", "options")),
    ("delivery and timing", ("deliver", "arrive", "shipping", "reach", "late", "how long", "on time", "pickup")),
    ("quality and proof", ("quality", "fresh", "taste", "proof", "review", "sample", "spec", "results", "does it work", "actually work")),
    ("return on investment", ("roi", "return on", "payback", "save us", "saves", "worth it for the business", "pay for itself")),
    ("approvals and switching", ("approve", "approval", "management", "board", "boss", "partner", "switch", "existing vendor", "current vendor", "integrate")),
    ("support and warranty", ("support", "warranty", "help", "contact", "repair", "complain", "customer service")),
    ("who is behind it", ("who", "company", "brand", "legit", "scam", "founder", "still be around", "exist")),
]
TOPIC_NAMES = [t for t, _ in QUESTION_TOPICS] + ["other"]
ENGAGEMENT = ["none", "like", "comment", "share", "save", "follow"]
AFTER = ["tell friends", "post a review", "post on social media", "say nothing", "complain or ask for a refund"]
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
    k = sum(1 for dim in c.get("dimensions") or [] for v in dim["values"] for f in v.get("facts") or [] if not str(f.get("source", "")).strip())
    k += sum(1 for sg in _all_segments(c) for f in sg.get("facts") or [] if not str(f.get("source", "")).strip())
    if k:
        out.append("%d group %s no 'source' link. Buyers are told these are real: add links, or remove them." % (k, "fact has" if k == 1 else "facts have"))
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
        if "budget" in s and "income" not in s:
            s["income"] = s["budget"]
        if "name" not in s or "income" not in s or len(s["income"]) != 2:
            raise PanelError("every segment needs a name and an income [low, high]")
        if "roles" in s and (not isinstance(s["roles"], list) or not all(isinstance(r, dict) and "name" in r for r in s["roles"])):
            raise PanelError("a segment's 'roles' must be a list like [{\"name\": \"Owner\", \"share\": 0.8}]")
        if "age" in s and (not isinstance(s["age"], list) or len(s["age"]) != 2):
            raise PanelError("a segment's 'age' must be [youngest, oldest]")
    for b in c["behaviours"]:
        if "name" not in b:
            raise PanelError("every behaviour needs a name")
    region_of(c)
    for sg in c.get("segments") or []:
        if "budget" in sg and "income" not in sg:
            sg["income"] = sg["budget"]
    if c.get("test", "offer") not in ("offer", "content"):
        raise PanelError("'test' must be \"offer\" (a product or service) or \"content\" (a post, reel, ad or headline)")
    if c.get("mode", "b2c") not in ("b2c", "b2b"):
        raise PanelError("'mode' must be \"b2c\" (people) or \"b2b\" (businesses)")
    for r in c.get("roles") or []:
        if not isinstance(r, dict) or "name" not in r:
            raise PanelError("every role needs a name (and a share, and what they 'cares' about)")
    for g in c.get("genders") or []:
        if "name" not in g:
            raise PanelError("every gender needs a name")
    for g in c.get("age_groups") or []:
        if "name" not in g or len(g.get("range") or []) != 2 or g["range"][0] > g["range"][1]:
            raise PanelError("every age group needs a name and a range [youngest, oldest]")
    for mk in c.get("markets") or []:
        if not isinstance(mk, dict) or "name" not in mk:
            raise PanelError("every market needs a name (and a region, and a share or count)")
    if c.get("markets"):
        names = [mk["name"].strip().lower() for mk in c["markets"]]
        dup = sorted({x for x in names if names.count(x) > 1})
        if dup:
            raise PanelError("two markets are both called %s: give every market its own name" % ", ".join(map(repr, dup)))
        has = [("count" in mk) for mk in c["markets"]]
        if any(has) and not all(has):
            raise PanelError("give every market a 'count', or none of them (then 'share' is used)")
    b = c.get("biases", True)
    if isinstance(b, list):
        unknown = [x for x in b if x not in BIASES]
        if unknown:
            raise PanelError("unknown bias %s. Choose from: %s" % (", ".join(map(repr, unknown)), ", ".join(BIASES)))
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
        for v in dim["values"]:
            for f in v.get("facts") or []:
                if not (isinstance(f, dict) and str(f.get("text", "")).strip()):
                    raise PanelError("every fact on a dimension value needs a 'text' (and a 'source' link)")
    if c.get("income_is", "personal") not in ("personal", "household"):
        raise PanelError("'income_is' must be \"personal\" or \"household\"")
    for sg in _all_segments(c):
        if not isinstance(sg.get("facts") or [], list):
            raise PanelError("'facts' on segment %r must be a list" % sg.get("name"))
        for f in sg.get("facts") or []:
            if not (isinstance(f, dict) and str(f.get("text", "")).strip()):
                raise PanelError("every fact on segment %r needs a 'text' (and a 'source' link)" % sg.get("name"))
        if sg.get("income_is", "personal") not in ("personal", "household"):
            raise PanelError("'income_is' on segment %r must be \"personal\" or \"household\"" % sg.get("name"))


def _all_segments(c):
    """Segments at the top level and inside every market."""
    return list(c.get("segments") or []) + [sg for mk in c.get("markets") or [] for sg in mk.get("segments") or []]


SIZES = {"small": 20, "medium": 100, "large": 250}


def pick_segments(customer, only):
    """Keep only the named segments (categories), e.g. only="Category A,Category B". Case-insensitive, and
    "Category A" matches "Category A: HNI buyers". With markets, it applies inside every market."""
    if not only:
        return customer
    want = [x.strip().lower() for x in only.split(",") if x.strip()]

    def matches(w, seg):
        name = seg["name"].lower()
        return name == w or name.split(":")[0].strip() == w

    def pick(segs):
        return [sg for sg in segs if any(matches(w, sg) for w in want)]

    if customer.get("markets"):
        c = json.loads(json.dumps(customer))
        found, kept = set(), []
        for mk in c["markets"]:
            segs = mk.get("segments") or c.get("segments") or []
            got = pick(segs)
            found |= {w for w in want for sg in got if matches(w, sg)}
            if got:
                mk["segments"] = got
                kept.append(mk)
        missing = [w for w in want if w not in found]
        if missing or not kept:
            names = sorted({sg["name"] for mk in customer["markets"] for sg in (mk.get("segments") or customer.get("segments") or [])})
            raise PanelError("no segment called %s in any market. Segments: %s" % (", ".join(repr(m) for m in missing or want), ", ".join(names)))
        c["markets"] = kept
        return c
    picked = pick(customer["segments"])
    missing = [w for w in want if not any(matches(w, sg) for sg in customer["segments"])]
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


def market_customer(customer, market_name):
    """The customer profile one market's buyers come from: the shared profile with that market's overrides."""
    base = {k: v for k, v in customer.items() if k != "markets"}
    for mk in customer.get("markets") or []:
        if mk["name"] == market_name:
            merged = dict(base)
            merged.update({k: v for k, v in mk.items() if k not in ("name", "share", "count")})
            if "region" in mk and "currency" not in mk:
                merged.pop("currency", None)
            if "region" in mk and "names" not in mk:
                merged.pop("names", None)
            return merged
    return base


def deal(customer, n=100, seed=7):
    """Deal n persona cards. Same customer + n + seed = the same cards, every time.
    If every segment has a "count", those counts are used and n becomes their total.
    With "markets", buyers are dealt per market (each with its own region, currency, names, facts) and merged."""
    if customer.get("markets"):
        validate_customer(dict(customer, segments=customer.get("segments") or [{"name": "-", "income": [0, 0]}]))
        mks = customer["markets"]
        counts = [int(m["count"]) for m in mks] if all("count" in m for m in mks) else _quota(mks, n)
        cards = []
        for k, (mk, cnt) in enumerate(zip(mks, counts)):
            if cnt <= 0:
                continue
            sub = market_customer(customer, mk["name"])
            segs = sub.get("segments") or []
            if segs and all("count" in x for x in segs):  # the market's headcount wins; its segments keep their mix
                tot = float(sum(int(x["count"]) for x in segs)) or 1.0
                sub["segments"] = [dict({k2: v for k2, v in x.items() if k2 != "count"}, share=int(x["count"]) / tot) for x in segs]
            for c in _deal_one(sub, cnt, seed * 1000 + k):
                c["market"] = mk["name"]
                cards.append(c)
        for i, c in enumerate(cards):
            c["id"] = "P%03d" % (i + 1)
        return cards
    return _deal_one(customer, n, seed)


def _deal_one(customer, n, seed):
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
    dim_facts = {(dim["name"], v["name"]): v.get("facts") or [] for dim in customer.get("dimensions") or [] for v in dim["values"]}
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

    roles = _spread(customer["roles"], n, rng) if customer.get("roles") else [None] * n
    bias_opt = customer.get("biases", True)
    bias_pool = list(BIASES) if bias_opt is True else (list(bias_opt) if isinstance(bias_opt, list) else [])
    biases = [bias_pool[i % len(bias_pool)] for i in range(n)] if bias_pool else [""] * n
    rng.shuffle(biases)

    skeptic = float(customer.get("skeptic_share", SKEPTIC_SHARE))
    open_ids = set(rng.sample(range(n), int(round(n * max(0.0, min(1.0, skeptic))))))
    cards = []
    for i in range(n):
        s, b = segs[i], behs[i]
        lo, hi = float(s["income"][0]), float(s["income"][1])
        # A segment's own roles win, so a housing society has a secretary and a shop has an owner.
        seg_role = None
        if s.get("roles"):
            opts = s["roles"]
            tot = sum(float(o.get("share", 1)) for o in opts) or 1.0
            x, acc = rng.random() * tot, 0.0
            for o in opts:
                acc += float(o.get("share", 1))
                if x <= acc:
                    seg_role = dict(o)
                    break
            seg_role = seg_role or dict(opts[-1])
            if not seg_role.get("cares"):
                seg_role["cares"] = next((r.get("cares", "") for r in customer.get("roles") or [] if r["name"] == seg_role["name"]), "")
        # A segment's own age range wins, so students are young and senior managers are older, as in real life.
        seg_age = rng.randint(int(min(s["age"])), int(max(s["age"]))) if s.get("age") else None
        cards.append({
            "id": "P%03d" % (i + 1),
            "name": pick_name(genders[i]),
            "age": seg_age if seg_age is not None else (rng.randint(int(ages[i]["range"][0]), int(ages[i]["range"][1])) if ages[i] else rng.randint(int(age[0]), int(age[1]))),
            "gender": genders[i]["name"] if genders[i] else "",
            "age_group": _age_group_for(customer, seg_age) if seg_age is not None else (ages[i]["name"] if ages[i] else ""),
            "traits": {dn: vals[i]["name"] for dn, vals in dims},
            "trait_facts": [f["text"] for f in s.get("facts") or []] + [f["text"] for dn, vals in dims for f in dim_facts.get((dn, vals[i]["name"]), [])],
            "language": langs[i]["name"] if langs[i] else (customer.get("language") or ""),
            "segment": s["name"],
            "household": (s.get("income_is") or customer.get("income_is")) == "household",
            "income": int(round(rng.uniform(lo, hi), -3)),
            "behaviour": b["name"],
            "behaviour_how": b.get("how", ""),
            "objection": "" if i in open_ids else objections[rng.randrange(len(objections))],
            "habit": habits[rng.randrange(len(habits))] if habits else "",
            "reviews": reviews_for(b),
            "bias": biases[i],
            "role": seg_role["name"] if seg_role else (roles[i]["name"] if roles[i] else ""),
            "role_cares": seg_role.get("cares", "") if seg_role else (roles[i].get("cares", "") if roles[i] else ""),
            "region": (region_of(customer) and (customer.get("region") or customer.get("locale") or "").strip().upper()) or "",
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


def counts_to_shares(customer):
    """Turn fixed headcounts (markets and segments) into shares, so a requested panel size keeps the mix."""
    c = json.loads(json.dumps(customer))
    for key in ("markets", "segments"):
        items = c.get(key) or []
        if items and all("count" in x for x in items):
            tot = float(sum(int(x["count"]) for x in items)) or 1.0
            for x in items:
                x["share"] = int(x.pop("count")) / tot
    for mk in c.get("markets") or []:
        segs = mk.get("segments") or []
        if segs and all("count" in x for x in segs):
            tot = float(sum(int(x["count"]) for x in segs)) or 1.0
            for x in segs:
                x["share"] = int(x.pop("count")) / tot
    return c


def init(d, customer_path, pitch_path, n=100, seed=None, only=None, scale=False):
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
    if scale:
        customer = counts_to_shares(customer)
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
{name}, {age}{gender_part}. {segment}. {income_line}.{where_line}
How you buy: {behaviour}. {behaviour_how}
{habit_line}{traits_line}{bias_line}{objection_line}
You are one of these people: {target}.
These facts are context about one specific person's life, not a script. Act as this individual would, never as a stereotype of any group.
=== END ===
{market_block}
=== WHAT IS BEING OFFERED (you see it for the first time, the way a passer-by or a scroller would) ===
{pitch}
=== END ===

Before you answer, picture the real moment: you are busy, you have other options, and spending money means not spending it on something else. Like any careful shopper, check what the offer tells you about: {checks}. Where it leaves something unclear that matters to you, that is a real reason to hesitate. Decide as {name} would, with {name}'s money, habits and doubts, in a normal week. Do not be agreeable. Do not invent facts about the business beyond what is written above.{language_line}

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
  "questions_before_buying": [1 to 4 practical questions you would need answered before paying, each as {{"question": "in your own words", "topic": one of {topics}}}],
  "if_bought_stars": imagine you bought it and it was exactly as described: the star rating you would give, 1 to 5,
  "if_bought_review": "the one-line review you would honestly write, in your own voice",
  "recommend": still imagining you bought it and it was as described: how likely you would be to recommend it to a friend, 0 to 10,
  "after_purchase": what you would most likely do afterwards, one of {after},
  "price_currency": "{price_cur}",
  "price_too_cheap": the price at which it would seem too cheap to be any good (a number),
  "price_cheap": the price at which it would feel like a bargain (a number),
  "price_expensive": the price at which it starts to feel expensive but you might still buy (a number),
  "price_too_expensive": the price at which you would not buy it at all (a number)
  (give all four prices in {price_cur})
}}
"""


def _b2b(brief, c, cust):
    """Turn a consumer brief into a business-buyer brief: a role at a company, a budget, approvals and ROI."""
    cur = _currency(cust)
    budget = ("Your company can spend about %s%s a year on purchases like this" % (cur, _money(c["income"], cust))
              if c["income"] > 0 else "There is no set budget for this; any spend must be argued for")
    role = c.get("role") or "the person who decides purchases like this"
    who = "%s, %d%s. Your role: %s. Your business: %s. %s." % (c["name"], c["age"], (", %s" % c["gender"]) if c.get("gender") else "",
                                                                 role, c["segment"], budget)
    old_who = brief.split("=== WHO YOU ARE ===\n", 1)[1].split("\n", 1)[0]
    brief = brief.replace(old_who, who + ((" You work in %s." % cust["where"]) if cust.get("where") else ""), 1)
    if c.get("role_cares"):
        brief = brief.replace("How you buy: ", "What matters most to you in your job: %s\nHow your company buys: " % c["role_cares"], 1)
    else:
        brief = brief.replace("How you buy: ", "How your company buys: ", 1)
    brief = brief.replace("You are a simulated buyer on a consumer panel. A founder wants to know, before spending any money, whether real people like you would buy.",
                          "You are a simulated business buyer on a panel. A founder wants to know, before spending any money, whether businesses like yours would buy.", 1)
    brief = brief.replace("(you see it for the first time, the way a passer-by or a scroller would)",
                          "(it reaches you the way a sales pitch, a WhatsApp message or a cold email would)", 1)
    brief = brief.replace("you are busy, you have other options, and spending money means not spending it on something else.",
                          "you are busy, you have other suppliers, and the money comes from a business budget you must justify.", 1)
    brief = brief.replace("Like any careful shopper, check what the offer tells you about: " + "; ".join(PRACTICAL_CHECKS),
                          "Like any careful business buyer, check what the offer tells you about: " + "; ".join(B2B_CHECKS), 1)
    brief = brief.replace("with %s's money, habits and doubts, in a normal week." % c["name"],
                          "for the business, with its budget, its approvals and its risks, in a normal working week.", 1)
    brief = brief.replace("how many times you would buy in the first month (0 if you would not buy)",
                          "how many units or orders your business would place in the first month (0 if you would not buy)", 1)
    brief = brief.replace("You are one of these people:", "Your business is one of these:", 1)
    return brief


def _content(brief, c, cust):
    """Turn an offer brief into a feed brief: would they stop, engage, click, and does it make them want to buy?"""
    platform = cust.get("platform") or "your social media feed"
    brief = brief.replace("=== WHAT IS BEING OFFERED (you see it for the first time, the way a passer-by or a scroller would) ===",
                          "=== WHAT APPEARS IN YOUR FEED on %s (between posts from friends and creators you follow) ===" % platform, 1)
    brief = brief.replace("=== WHAT IS BEING OFFERED (it reaches you the way a sales pitch, a WhatsApp message or a cold email would) ===",
                          "=== WHAT APPEARS IN YOUR FEED on %s (between posts from people and brands you follow) ===" % platform, 1)
    i = brief.find("Before you answer, picture the real moment:")
    j = brief.find("Do not be agreeable.", i)
    if i >= 0 and j > i:
        brief = brief[:i] + ("Picture the real moment: you are scrolling quickly, half paying attention, and you give most posts less than "
                             "two seconds. Most posts get scrolled past. Decide what %s would really do, then whether it makes you "
                             "want what it promotes. " % c["name"]) + brief[j:]
    brief = brief.replace('  "intent": 1 to 5', ('  "stops_scrolling": true or false (would this make you stop and look for more than two seconds?),\n'
                                                   '  "engagement": one of "none" / "like" / "comment" / "share" / "save" / "follow" (the one thing you would most likely do),\n'
                                                   '  "clicks": true or false (would you tap through, visit the profile or link, or send a message?),\n'
                                                   '  "intent": 1 to 5'), 1)
    brief = brief.replace('"buys": true only if intent is 4 or 5, else false', '"buys": true only if intent is 4 or 5 (you would actually go and buy or enquire), else false', 1)
    brief = brief.replace('"reason": "why, in one or two sentences, in your own voice"',
                          '"reason": "why you stopped or scrolled past, and why you would or would not act, in one or two sentences, in your own voice"', 1)
    return brief


def write_briefs(d, wave=WAVE):
    state, cards = load_state(d)
    target = state["customer"]["target"]
    todo = []
    top = state["customer"]
    price_cur = (top.get("price_currency") or _currency(top)).strip()
    for c in cards:
        out = _path(d, "answers", c["id"] + ".json")
        if _answer_ok(out, c["id"]) is None:
            continue
        cust = market_customer(top, c["market"]) if c.get("market") else top
        brief = BRIEF.format(price_cur=price_cur, after=" / ".join('"%s"' % x for x in AFTER), checks="; ".join(PRACTICAL_CHECKS),
                             topics=" / ".join('"%s"' % t for t in TOPIC_NAMES),
                             bias_line=("How you tend to decide: %s\n" % BIASES[c["bias"]]) if c.get("bias") in BIASES else "",pitch=state["pitch"], target=target, out=os.path.abspath(out),
                             habit_line=("Your day: %s.\n" % c["habit"]) if c.get("habit") else "",
                             cur=_currency(cust),
                             gender_part=(", %s" % c["gender"]) if c.get("gender") else "",
                             traits_line="".join("Your %s: %s.\n" % (k, v) for k, v in (c.get("traits") or {}).items()),
                             language_line=_language_line(c.get("language", "")),
                             reason_en_line=("\n  \"reason_en\": \"the same reason translated into English\","
                                             if _foreign(c.get("language", "")) else ""),
                             market_block=_market_block(cust, c), income_line=("%s about %s%s a year" % ("Your household earns" if c.get("household") else "You earn",
                                                     _currency(cust), _money(c["income"], cust))) if c["income"] > 0
                             else "You have no income of your own (you live on family support, savings or a stipend)",
                             where_line=(" You live in %s." % cust["where"]) if cust.get("where") else "",
                             objection_line=('The first thing that comes to mind when you hear an offer like this: "%s"' % c["objection"])
                             if c.get("objection") else "Nobody has told you what to doubt. React the way you really would.",
                             reasons=" / ".join(REASONS), **c)
        if (cust.get("mode") or top.get("mode")) == "b2b":
            brief = _b2b(brief, c, cust)
        if (cust.get("test") or top.get("test")) == "content":
            brief = "\n".join(l for l in brief.split("\n") if not re.match(r'\s*"(if_bought_stars|if_bought_review|recommend|after_purchase)"', l))
            brief = _content(brief, c, cust)
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
    if "if_bought_stars" in a and (isinstance(a["if_bought_stars"], bool) or a["if_bought_stars"] not in (1, 2, 3, 4, 5)):
        return "'if_bought_stars' must be 1 to 5"
    if "recommend" in a and (not isinstance(a["recommend"], int) or isinstance(a["recommend"], bool) or a["recommend"] not in range(11)):
        return "'recommend' must be a whole number 0 to 10"
    if "after_purchase" in a and a["after_purchase"] not in AFTER:
        return "'after_purchase' must be one of %s" % ", ".join(AFTER)
    if "stops_scrolling" in a and not isinstance(a["stops_scrolling"], bool):
        return "'stops_scrolling' must be true or false"
    if "clicks" in a and not isinstance(a["clicks"], bool):
        return "'clicks' must be true or false"
    if "engagement" in a and a["engagement"] not in ENGAGEMENT:
        return "'engagement' must be one of %s" % ", ".join(ENGAGEMENT)
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
    reg = (customer.get("region") or customer.get("locale") or "").strip().upper()
    reg = {"GB": "UK"}.get(reg, reg)
    if customer.get("region_facts", True) and reg in REGION_FACTS:
        facts = [f["text"] for f in REGION_FACTS[reg]] + facts
    allrev = m.get("reviews") or []
    seen = [allrev[i] for i in card.get("reviews") or [] if i < len(allrev)]
    local = card.get("trait_facts") or []
    if not facts and not seen and not local:
        return ""
    out = ["", "=== WHAT YOU ALREADY KNOW (real, sourced facts about your market, and real reviews) ==="]
    if facts:
        out.append("How people around you pay, save and buy:")
        out += ["- %s" % f for f in facts]
    if local:
        out.append("About where you live and how people like you spend:")
        out += ["- %s" % f for f in local[:6]]
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
    """6.5, "6.50", "₹2,50,000", "$9.99/mo", "Rs. 199" and "1.299,00 €" all work."""
    if not isinstance(v, str):
        return _num(v)
    t = re.sub(r"^[^0-9]*", "", v.strip())      # drop "Rs. ", "$", "₹" in front
    t = re.match(r"[0-9.,]*", t).group(0).rstrip(".,")
    if not t:
        return None
    if "," in t and "." in t:                   # the later separator is the decimal point
        dec = "," if t.rfind(",") > t.rfind(".") else "."
        t = t.replace("." if dec == "," else ",", "").replace(",", ".")
    elif "," in t:                              # 2,50,000 / 1,299 are thousands; 6,50 is a decimal
        t = t.replace(",", "") if len(t.rsplit(",", 1)[1]) == 3 else t.replace(",", ".")
    elif t.count(".") > 1:                      # 1.299.000
        t = t.replace(".", "")
    return _num(t)

def _format_for(customer):
    """How to group digits for money in the price currency (lakhs if that currency is the rupee)."""
    pc = (customer.get("price_currency") or _currency(customer)).strip()
    for code, reg in REGIONS.items():
        if reg["currency"].strip() == pc:
            return {"region": code}
    return {k: customer[k] for k in ("region", "locale") if k in customer}


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
    # Per market when there are several, because incomes in different currencies cannot share bands.
    cur = _currency(state["customer"])
    by_mk = {}
    for r in rows:
        by_mk.setdefault(r.get("market", ""), []).append(r)
    for mk, rs in by_mk.items():
        mc = market_customer(state["customer"], mk) if mk else state["customer"]
        mcur = _currency(mc)
        incomes = sorted(r["income"] for r in rs)
        cut1, cut2 = incomes[len(incomes) // 3], incomes[2 * len(incomes) // 3]
        pre = ("%s: " % mk) if mk else ""
        for r in rs:
            r["income_band"] = pre + (("under %s%s" % (mcur, _money(cut1, mc))) if r["income"] < cut1 else (
                ("%s%s and up" % (mcur, _money(cut2, mc))) if r["income"] >= cut2 else
                "%s%s to %s%s" % (mcur, _money(cut1, mc), mcur, _money(cut2, mc))))

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
    if realistic is not None:  # the raw rate is the upper bound, so the realistic estimate never goes above it
        realistic = min(realistic, sum(1 for r in rated if r["intent"] >= 4) / float(len(rated)))
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
        "price_currency": (state["customer"].get("price_currency") or _currency(state["customer"])).strip(),
        "customer_for_format": _format_for(state["customer"]),
        "intent_counts": intent_counts, "intent_answers": len(rated), "intent_weights": weights, "realistic_rate": realistic, "currency": cur,
        "unprompted": [(r["id"], r["unprompted_doubt"]) for r in rows if (r.get("unprompted_doubt") or "").strip()],
        "by_market": group("market") if any(r.get("market") for r in rows) else [],
        "by_bias": group("bias") if any(r.get("bias") for r in rows) else [],
        "by_role": group("role") if any(r.get("role") for r in rows) else [],
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
    questions = []
    for r in rows:
        qs = r.get("questions_before_buying")
        if isinstance(qs, str):
            qs = [qs]
        for q in qs or []:
            topic = None
            if isinstance(q, dict):
                topic = q.get("topic") if q.get("topic") in TOPIC_NAMES else None
                q = q.get("question")
            if isinstance(q, str) and q.strip():
                questions.append((r["id"], q.strip(), topic))
    topics = {}
    for pid, q, topic in questions:
        if topic is None:  # older answers: sort by keywords
            low = q.lower()
            topic = next((t for t, words in QUESTION_TOPICS if any(w in low for w in words)), "other")
        topics.setdefault(topic, []).append((pid, q))
    res["questions"] = [{"topic": t, "count": len(v), "examples": [q for _, q in v[:4]], "ids": [i for i, _ in v[:4]]}
                        for t, v in sorted(topics.items(), key=lambda kv: -len(kv[1]))]
    trait_names = sorted({k for r in rows for k in (r.get("traits") or {})})
    keep = ("id", "name", "age", "gender", "age_group", "segment", "role", "behaviour", "bias", "language", "market", "traits",
            "income_band", "buys", "intent", "reason_code", "reason", "reason_en", "objection", "unprompted_doubt",
            "would_change_my_mind", "purchases_first_month", "questions_before_buying")
    buyers = []
    for r in rows:
        b = {k: r.get(k) for k in keep if r.get(k) not in (None, "")}
        b["buys"] = r["buys"]
        mc = market_customer(state["customer"], r["market"]) if r.get("market") else state["customer"]
        b["income_txt"] = ("budget %s%s a year" if (mc.get("mode") or state["customer"].get("mode")) == "b2b" else "%s%s a year") % (_currency(mc), _money(r["income"], mc))
        n_rev = len(r.get("reviews") or [])
        b["reviews_read"] = "none" if n_rev == 0 else str(n_rev)
        buyers.append(b)
    res["buyers"] = buyers
    res["trait_names"] = trait_names
    res["practical"] = practical(state, rows, res)
    res["test"] = state["customer"].get("test", "offer")
    if res["test"] == "content":
        n = float(len(rows))
        res["content"] = {"platform": state["customer"].get("platform", ""),
                          "stop_rate": sum(1 for r in rows if r.get("stops_scrolling") is True) / n,
                          "click_rate": sum(1 for r in rows if r.get("clicks") is True) / n,
                          "engagement": {e: sum(1 for r in rows if r.get("engagement") == e) for e in ENGAGEMENT},
                          "answered": sum(1 for r in rows if "stops_scrolling" in r)}
    rec = [r["recommend"] for r in rows if isinstance(r.get("recommend"), int) and not isinstance(r.get("recommend"), bool)]
    stars = [r["if_bought_stars"] for r in rows if r.get("if_bought_stars") in (1, 2, 3, 4, 5)]
    if rec or stars:
        reviews = [(r["id"], r["if_bought_stars"], r.get("if_bought_review", "")) for r in rows
                   if r.get("if_bought_stars") in (1, 2, 3, 4, 5) and (r.get("if_bought_review") or "").strip()]
        res["after"] = {
            "nps": round(100.0 * (sum(1 for x in rec if x >= 9) - sum(1 for x in rec if x <= 6)) / len(rec)) if rec else None,
            "promoters": sum(1 for x in rec if x >= 9), "passives": sum(1 for x in rec if 7 <= x <= 8),
            "detractors": sum(1 for x in rec if x <= 6), "answers": len(rec),
            "avg_stars": (sum(stars) / float(len(stars))) if stars else None,
            "stars": {str(k): sum(1 for x in stars if x == k) for k in range(1, 6)},
            "actions": {a: sum(1 for r in rows if r.get("after_purchase") == a) for a in AFTER},
            "best_reviews": [x for x in sorted(reviews, key=lambda t: -t[1]) if x[1] >= 4][:3],
            "worst_reviews": [x for x in sorted(reviews, key=lambda t: t[1]) if x[1] <= 3][:3]}
    res["audit"] = audit(state, rows, res)
    res["sources"] = _sources(state["customer"])
    return res


def results_md(res):
    pct = lambda v: "%.0f%%" % (v * 100)
    if res.get("audit"):
        a = res["audit"]
        head = ["# Buyer panel: %s" % res["business"], "", "**Score: %d / 100 (%s).** %s See audit.md." % (a["score"], a["grade"], a["verdict"]), ""]
        head += ["- %s" % x for x in a["easy"]] + [""]
    else:
        head = []
    L = head[:-1] if head else ["# Buyer panel: %s" % res["business"], ""]
    if head:
        L.append("")
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
                 % (res.get("price_currency", "$"), _price_text(res["price"], res), res.get("price_currency", "$"),
                    _money(res["revenue_first_month_per_100_reached"], res.get("customer_for_format") or {})))
    tables = [("By segment", res["by_segment"]), ("By buying behaviour", res["by_behaviour"]), ("By income", res["by_income"])]
    if res.get("by_market"):
        tables.insert(0, ("By market", res["by_market"]))
    if res.get("by_role"):
        tables.insert(1 if res.get("by_market") else 0, ("By role", res["by_role"]))
    if res.get("by_bias"):
        tables.append(("By how they decide (bias)", res["by_bias"]))
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
    if res.get("questions"):
        L += ["", "## Questions buyers need answered before paying", "",
              "Answer these on your page, in your FAQ and at checkout.", ""]
        for qd in res["questions"]:
            L.append("- **%s** (%d): %s" % (qd["topic"], qd["count"], " · ".join('"%s"' % q.replace("|", "/") for q in qd["examples"][:2])))
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


ACTIONS = {
    "price": "Test a lower entry point (smaller pack, first-month offer, EMI or instalments) and show the price next to what they pay today.",
    "trust": "Add proof before asking for money: named specs, real reviews, a guarantee or free trial, a face behind the brand.",
    "habit": "Give one easy reason to switch: a free first try, or fit it into a routine they already have.",
    "need": "These buyers do not have the problem. Narrow the target to the groups that do buy, and stop spending on the rest.",
    "convenience": "Remove effort: delivery, location, the payment method they already use, fewer steps to buy.",
    "quality": "Let them try it: samples, demos, proof of quality from people they believe.",
    "timing": "Keep them for later: a waitlist, a reminder, a seasonal launch.",
    "values": "Check what they care about against your message and how the product is made.",
    "other": "Read their own words below and look for a pattern.",
}


def _median(vals):
    vals = sorted(v for v in vals if v is not None)
    if not vals:
        return None
    m = len(vals) // 2
    return vals[m] if len(vals) % 2 else (vals[m - 1] + vals[m]) / 2.0


GRADES = [(80, "Strong", "Buyers want this. Fix the small gaps and test it with real customers."),
          (60, "Promising", "There is real interest. Fix the top objections and test again."),
          (40, "Needs work", "Interest is weak. Change the offer, price or target customer before you spend."),
          (0, "Weak", "Most buyers would not act. Rethink the idea, the customer or the price.")]


def audit(state, rows, res):
    """The audit: one score out of 100 with a transparent breakdown, a plain summary and a detailed summary.
    The score is a guide for comparing versions of your idea, not a forecast."""
    n = float(len(rows))
    rated = [r for r in rows if r.get("intent") in (1, 2, 3, 4, 5)]
    mean_intent = (sum(r["intent"] for r in rated) / len(rated)) if rated else (1 + 4 * res["buy_rate"])
    parts = []
    if res.get("test") == "content":
        ct = res["content"]
        engaged = 1 - (ct["engagement"].get("none", 0) / n) if ct["answered"] else 0.0
        parts.append({"name": "Stops the scroll", "points": round(40 * ct["stop_rate"]), "max": 40,
                      "why": "%d%% of buyers would stop and look" % round(100 * ct["stop_rate"])})
        parts.append({"name": "Engagement", "points": round(20 * engaged), "max": 20,
                      "why": "%d%% would like, comment, share, save or follow" % round(100 * engaged)})
        parts.append({"name": "Makes them act", "points": round(40 * (0.5 * (mean_intent - 1) / 4.0 + 0.5 * ct["click_rate"])), "max": 40,
                      "why": "average interest %.1f out of 5 after seeing it; %d%% would click through" % (mean_intent, round(100 * ct["click_rate"]))})
    else:
        price = res.get("price")
        fit = None
        if price is not None:
            judged = [r for r in rows if _num(r.get("price_too_expensive")) is not None
                      and (r.get("price_currency") or res.get("price_currency")) == res.get("price_currency")]
            if judged:
                fit = sum(1 for r in judged if price < _num(r["price_too_expensive"])) / float(len(judged))
        trust = sum(1 for r in rows if r.get("reason_code") == "trust") / n
        demand_max = 60 if fit is not None else 80
        # half how keen they are on average, half how many actually said yes
        demand = 0.5 * (mean_intent - 1) / 4.0 + 0.5 * res["buy_rate"]
        parts.append({"name": "Demand", "points": round(demand_max * demand), "max": demand_max,
                      "why": "average interest %.1f out of 5; %d%% said yes" % (mean_intent, round(100 * res["buy_rate"]))})
        if fit is not None:
            parts.append({"name": "Price fit", "points": round(20 * fit), "max": 20,
                          "why": "%d%% of buyers find your price below their 'too expensive' point" % round(100 * fit)})
        parts.append({"name": "Trust", "points": round(20 * (1 - trust)), "max": 20,
                      "why": "%d%% hold back mainly because they do not trust it yet" % round(100 * trust)})
    score = int(sum(p["points"] for p in parts))
    grade, verdict = next((g, v) for cut, g, v in GRADES if score >= cut)

    P = res["practical"]
    easy = []
    if res.get("test") == "content":
        ct = res["content"]
        easy.append("%d%% of buyers would stop scrolling for this, and %d%% would click through." % (round(100 * ct["stop_rate"]), round(100 * ct["click_rate"])))
    real = res.get("realistic_rate")
    if res["buys"] == 0:
        easy.append("None of the %d buyers said they would buy yet." % len(rows))
    else:
        easy.append("About %d%% of these buyers would realistically buy, and at most %d%% in the most hopeful reading." % (
            round(100 * (real if real is not None else res["buy_rate"])), round(100 * res["buy_rate"])))
    if P.get("best_group"):
        easy.append("Your best customers: %s (%d%% said yes)." % (P["best_group"]["group"], round(100 * P["best_group"]["rate"])))
    else:
        easy.append("No customer group said yes yet, so fix the offer before you target anyone.")
    if P.get("fix_first"):
        f = P["fix_first"][0]
        easy.append("The biggest thing holding people back is %s (%d of %d buyer%s)." % (f["reason"], f["buyers"], len(rows), "" if len(rows) == 1 else "s"))
    for pv in P.get("prices") or []:
        if res.get("price") is not None and pv["currency"] == res.get("price_currency") and pv.get("too_expensive") is not None:
            pr = res["price"]
            where = ("above what most buyers would pay" if pr >= pv["too_expensive"] else
                     "on the expensive side" if pv.get("expensive") is not None and pr > pv["expensive"] else
                     "in the range buyers accept")
            easy.append("Your price is %s; buyers see %s%s as a bargain and %s%s as too expensive." % (
                where, pv["currency"], _num_txt(pv["bargain"]), pv["currency"], _num_txt(pv["too_expensive"])))
            break
    if res.get("questions"):
        easy.append("The question buyers ask most is about %s: answer it on your page and in your pitch." % res["questions"][0]["topic"])
    af = res.get("after")
    if af and af.get("avg_stars") is not None:
        easy.append("If it works as promised, buyers expect to rate it %.1f stars on average, with a recommendation score (NPS) of %s." % (
            af["avg_stars"], ("%+d" % af["nps"]) if af.get("nps") is not None else "not given"))

    detailed = []
    detailed.append({"title": "Score breakdown", "lines": ["%s: %d of %d (%s)" % (p["name"], p["points"], p["max"], p["why"]) for p in parts]})
    groups = []
    for title, key in (("Market", "by_market"), ("Role", "by_role"), ("Segment", "by_segment"), ("Age group", "by_age_group"),
                       ("Gender", "by_gender"), ("Buying behaviour", "by_behaviour")):
        rs = [g for g in res.get(key) or [] if g[1] >= 3]
        if len(rs) >= 2:
            groups.append("%s: strongest %s (%d%%), weakest %s (%d%%)" % (title, rs[0][0], round(100 * rs[0][2]), rs[-1][0], round(100 * rs[-1][2])))
    if groups:
        detailed.append({"title": "Who responds best and worst", "lines": groups})
    if P.get("fix_first"):
        detailed.append({"title": "What to fix, in order", "lines": ["%s (%d buyer%s): %s" % (f["reason"], f["buyers"], "" if f["buyers"] == 1 else "s", f["do"]) for f in P["fix_first"]]})
    if res.get("questions"):
        detailed.append({"title": "Questions to answer before buyers will commit",
                         "lines": ["%s (%d): e.g. \"%s\"" % (q["topic"], q["count"], q["examples"][0]) for q in res["questions"][:6]]})
    if af:
        lines = ["Would recommend it (9-10): %d · passive (7-8): %d · would not (0-6): %d. NPS = %% recommending minus %% not = %s." % (
            af["promoters"], af["passives"], af["detractors"], ("%+d" % af["nps"]) if af.get("nps") is not None else "-")]
        top_act = sorted(af["actions"].items(), key=lambda kv: -kv[1])
        if top_act and top_act[0][1]:
            lines.append("After buying, most would: " + ", ".join("%s (%d)" % kv for kv in top_act if kv[1]))
        lines += ['%d stars: "%s"' % (s_, t) for _, s_, t in af["best_reviews"][:2] + af["worst_reviews"][:2]]
        detailed.append({"title": "Reviews they would leave and word of mouth", "lines": lines})
    if res.get("unprompted"):
        detailed.append({"title": "Doubts you had not listed", "lines": ['"%s"' % t for _, t in res["unprompted"][:5]]})
    detailed.append({"title": "Next steps", "lines": [
        "Fix the top 1 or 2 issues above and answer the top questions in your pitch.",
        "Run the panel again on the new pitch and compare the two (panel.py compare).",
        "Then test with real people: a page with a price, a waitlist or a pre-order from 10 to 20 real customers."]})
    return {"score": score, "grade": grade, "verdict": verdict, "parts": parts, "easy": easy, "detailed": detailed,
            "note": "The score compares versions of your idea on these simulated buyers. It is not a sales forecast."}


def _num_txt(v):
    return "{:,.0f}".format(v) if v is not None and v >= 100 else ("%g" % v if v is not None else "-")


def audit_md(res):
    a = res["audit"]
    L = ["# Audit: %s" % res["business"], "",
         "## Score: %d / 100 (%s)" % (a["score"], a["grade"]), "", a["verdict"], "", "*%s*" % a["note"], "",
         "## In plain words", ""]
    L += ["- %s" % x for x in a["easy"]]
    for sec in a["detailed"]:
        L += ["", "## %s" % sec["title"], ""] + ["- %s" % x for x in sec["lines"]]
    return "\n".join(L) + "\n"


def sales_kit_brief(res):
    """What the sales kit must answer, straight from the panel. Claude turns it into founder/panel/sales-kit.md."""
    L = ["# Sales kit inputs: %s" % res["business"], "",
         "Write `sales-kit.md` from this: honest answers only, and mark anything the founder must fill in as [fill in].", "",
         "## Objections, most common first", ""]
    for code, n, quotes, ids in res["why_not"]:
        L.append("- **%s** (%d buyers): %s" % (code, n, " · ".join('"%s"' % q for q in quotes)))
    if res.get("questions"):
        L += ["", "## Questions buyers ask before paying", ""]
        for q in res["questions"]:
            L.append("- **%s** (%d): %s" % (q["topic"], q["count"], " · ".join('"%s"' % x for x in q["examples"][:3])))
    if res.get("flip"):
        L += ["", "## What would turn a no into a yes", ""] + ["- %s" % f for f in res["flip"][:10]]
    L += ["", "## Write these sections", "",
          "1. Short answers to each objection (2 lines each, no invented facts).",
          "2. WhatsApp replies: 5 ready-to-send replies to the most common questions.",
          "3. FAQ for the website: 8 to 10 questions and answers.",
          "4. A 60-second sales call script: opener, 2 questions to ask, the pitch, handling the top 2 objections, the close.",
          "5. Three changes to the offer itself that would remove objections (e.g. trial, guarantee, payment option)."]
    return "\n".join(L) + "\n"


def practical(state, rows, res):
    """Plain next steps from the answers: what to fix first, who to target, what price to test."""
    no = [r for r in rows if not r["buys"]]
    steps = []
    for code, n, _, _ in res["why_not"][:3]:
        steps.append({"reason": code, "buyers": n, "share": n / float(len(rows)), "do": ACTIONS.get(code, ACTIONS["other"])})
    best = None
    for title, key in (("market", "by_market"), ("role", "by_role"), ("segment", "by_segment"), ("age group", "by_age_group"),
                       ("gender", "by_gender"), ("behaviour", "by_behaviour")):
        for k, n, r in res.get(key) or []:
            if n >= 5 and r > 0 and (best is None or r > best["rate"]):
                best = {"group": "%s: %s" % (title, k), "rate": r, "buyers": n}
    prices = {}
    top_cur = (state["customer"].get("price_currency") or _currency(state["customer"])).strip()
    for r in rows:
        vals = [_num(r.get(k)) for k in ("price_too_cheap", "price_cheap", "price_expensive", "price_too_expensive")]
        if all(v is not None for v in vals):
            prices.setdefault((r.get("price_currency") or top_cur).strip(), []).append(vals)
    price_view = []
    for cur, vs in prices.items():
        med = [_median([v[i] for v in vs]) for i in range(4)]
        price_view.append({"currency": cur, "answers": len(vs), "too_cheap": med[0], "bargain": med[1],
                           "expensive": med[2], "too_expensive": med[3]})
    return {"fix_first": steps, "best_group": best, "prices": price_view,
            "flip_top": res["flip"][:5]}


def _sources(customer):
    """Every fact buyers were shown, with its link, for the report."""
    out, seen = [], {}
    custs = [customer] + [market_customer(customer, mk["name"]) for mk in customer.get("markets") or []]
    for c in custs:
        reg = {"GB": "UK"}.get((c.get("region") or c.get("locale") or "").strip().upper(), "")
        reg = reg or (c.get("region") or c.get("locale") or "").strip().upper()
        facts = (REGION_FACTS.get(reg, []) if c.get("region_facts", True) else []) + list((c.get("market") or {}).get("facts") or [])
        facts = facts + [dict(f, region=("%s: %s" % (dim["name"], v["name"]))) for dim in c.get("dimensions") or []
                         for v in dim["values"] for f in v.get("facts") or []]
        facts = facts + [dict(f, region=sg["name"]) for sg in c.get("segments") or [] for f in sg.get("facts") or []]
        for f in facts:
            key = f["text"]
            label = f.get("region") or (REGIONS.get(reg, {}).get("label", reg) if reg else "")
            if key not in seen:
                seen[key] = {"region": label, "text": f["text"], "source": f.get("source", "")}
                out.append(seen[key])
            elif label and label not in seen[key]["region"].split("; "):
                seen[key]["region"] += "; " + label
    return out


def _esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


REPORT = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Buyer panel: __TITLE__</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#171a21;--sub:#5d6471;--line:#e4e7ec;--acc:#3451d1;--acc2:#3451d1;--yes:#0b7a66;--no:#b4441b}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 "Geist",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink);-webkit-font-smoothing:antialiased}
header{background:#fff;border-bottom:1px solid var(--line);color:var(--ink);padding:28px 20px 64px}
header h1{margin:0 auto;max-width:1060px;font-size:clamp(22px,3vw,30px);letter-spacing:-.025em;line-height:1.2;font-weight:700}header .sub{color:var(--sub);font-size:14px;margin:8px auto 0;max-width:1060px}
main{max-width:1100px;margin:0 auto;padding:0 18px 40px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:-40px 0 16px}
.kpi{border-radius:14px;padding:16px 18px;background:#fff;border:1px solid var(--line);color:var(--ink);box-shadow:0 1px 2px rgba(23,26,33,.05)}
.kpi:nth-child(1){border-top:3px solid var(--acc)}
.kpi .l{font-size:13px;color:var(--sub);font-weight:500}.kpi .v{font-size:30px;font-weight:700;letter-spacing:-.02em;font-variant-numeric:tabular-nums}.kpi .s{font-size:13px;color:var(--sub)}
.note{background:#fdf4dc;border:1px solid #f1dfa8;color:#5c4300;border-radius:10px;padding:10px 14px;font-size:14px;margin-bottom:16px}
.tabs{display:flex;gap:4px;flex-wrap:wrap;margin:8px 0 16px;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:5;border-bottom:1px solid var(--line)}
.tabs button{border:0;background:transparent;border-radius:8px;padding:8px 12px;cursor:pointer;font:500 14px inherit;font-family:inherit;color:var(--sub)}
.tabs button:hover{color:var(--ink);background:#fff}
.tabs button.on{background:var(--ink);color:#fff}
section{display:none}section.on{display:block}
.box{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin-bottom:12px}
.box h2{font-size:18px;margin:0 0 12px;letter-spacing:-.01em}.box h3{font-size:14px;margin:18px 0 6px;color:var(--ink);font-weight:600}
.row{display:grid;grid-template-columns:minmax(130px,34%) 1fr 64px;gap:12px;align-items:center;padding:6px 8px;border-radius:8px;cursor:pointer}
.row:hover{background:#f6f7f9}.bar{background:#eef0f3;border-radius:999px;height:12px;overflow:hidden}.fill{height:100%;border-radius:999px}
.thin{color:#7d8390;font-size:12.5px}.step{display:grid;grid-template-columns:38px 1fr;gap:12px;margin:12px 0;align-items:start}
.num{width:30px;height:30px;border-radius:50%;background:var(--ink);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:14px}
.filters{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px}
select,input,button.sm{font:inherit;padding:7px 10px;border:1px solid #d3d8df;border-radius:8px;background:#fff;color:var(--ink)}
.buyer{border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:8px 0;background:#fff}
.buyer summary{cursor:pointer;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.tag{font-size:12.5px;border-radius:999px;padding:2px 10px;background:#f1f3f6;color:#3b414d}.tag.yes{background:#e5f3ef;color:#075a4b}.tag.no{background:#fbece5;color:#8f3414}
blockquote{margin:6px 0;padding:8px 12px;border-left:3px solid #d3d8df;background:#f6f7f9;border-radius:0 8px 8px 0;font-size:14px}
table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid var(--line);padding:8px;text-align:left;vertical-align:top}th{color:var(--sub);font-weight:500;font-size:13px}
a{color:var(--acc);text-underline-offset:3px}.count{font-weight:700}.chip{display:inline-block;background:#eef1fd;color:#2a3fa8;border-radius:8px;padding:2px 10px;font-weight:600;font-size:13px}
.price{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:10px 0}.price div{border-radius:10px;padding:10px;text-align:center;color:#fff;font-weight:600}
.price small{display:block;font-weight:400;opacity:.9}
@media(max-width:600px){.row{grid-template-columns:1fr 70px}.row .bar{grid-column:1/3;grid-row:2}.price{grid-template-columns:repeat(2,1fr)}}
</style></head><body>
<header><h1>Buyer panel: __TITLE__</h1><div class="sub">Seed __SEED__ · simulated buyers, not customers · click any bar to filter the buyer list</div></header>
<main>
<div class="kpis" id="kpis"></div>
<div class="note">This is research, not a forecast. AI buyers lean agreeable, so read the raw buy rate as a ceiling. Use the reasons and doubts to fix the offer, then confirm with real people (a waitlist, a pre-sale, a price on a page) before you spend.</div>
<div class="tabs" id="tabs"></div>
<section id="t-audit"></section><section id="t-plan"></section><section id="t-who"></section><section id="t-why"></section><section id="t-faq"></section><section id="t-reviews"></section><section id="t-buyers"></section><section id="t-price"></section><section id="t-facts"></section>
</main>
<script>
const R = __DATA__;
const B = R.buyers;
const pct = v => v == null ? "–" : Math.round(v * 100) + "%";
const esc = t => String(t == null ? "" : t).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const el = id => document.getElementById(id);
const color = r => `hsl(${Math.round(r*140)},75%,${r<.5?55:45}%)`;
let filter = {};

function kpis(){
  const k = [];
  if (R.realistic_rate != null) k.push(["Realistic estimate", pct(R.realistic_rate), "weighted by how sure buyers were"]);
  k.push(["Raw buy rate", pct(R.buy_rate), "ceiling · 90% range " + pct(R.buy_rate_interval_90[0]) + "–" + pct(R.buy_rate_interval_90[1])]);
  if (R.money) k.push(["First-month revenue", R.money, "per 100 people who see the offer"]);
  k.push(["Buyers", R.answered, R.buys + " buy · " + R.passes + " pass"]);
  el("kpis").innerHTML = k.map(x => `<div class="kpi"><div class="l">${esc(x[0])}</div><div class="v">${esc(x[1])}</div><div class="s">${esc(x[2])}</div></div>`).join("");
}

const TABS = [["audit","Score & summary"],["plan","What to do next"],["who","Who buys"],["why","Why not"],["faq","Questions to answer"],["reviews","Reviews they'd leave"],["buyers","Every buyer"],["price","Price"],["facts","Facts used"]];
function tabs(){
  el("tabs").innerHTML = TABS.map(([id,t],i) => `<button data-t="${id}" class="${i? "":"on"}">${t}</button>`).join("");
  el("t-audit").classList.add("on");
  el("tabs").onclick = e => { const id = e.target.dataset.t; if(!id) return; show(id); };
}
function show(id){
  document.querySelectorAll(".tabs button").forEach(b => b.classList.toggle("on", b.dataset.t === id));
  document.querySelectorAll("section").forEach(s => s.classList.toggle("on", s.id === "t-" + id));
}

function audit(){
  const A = R.audit; if (!A) { el("t-audit").innerHTML = "<div class='box'>No audit in this report.</div>"; return; }
  const col = A.score >= 80 ? "#0b7a66" : A.score >= 60 ? "#4d7c0f" : A.score >= 40 ? "#b45309" : "#b4441b";
  const deg = Math.round(A.score * 3.6);
  let h = `<div class="box" style="display:grid;grid-template-columns:150px 1fr;gap:18px;align-items:center">
    <div style="width:140px;height:140px;border-radius:50%;background:conic-gradient(${col} ${deg}deg,#eef0f3 0);display:flex;align-items:center;justify-content:center">
      <div style="width:108px;height:108px;border-radius:50%;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center"><div style="font-size:34px;font-weight:800;color:${col}">${A.score}</div><div class="thin">out of 100</div></div></div>
    <div><div class="chip" style="font-size:15px">${esc(A.grade)}</div><p style="font-size:17px;margin:8px 0">${esc(A.verdict)}</p><p class="thin">${esc(A.note)}</p></div></div>`;
  if (R.content) { const C = R.content; h += `<div class="box"><h2>Content results${C.platform?" · "+esc(C.platform):""}</h2><div class="price"><div style="background:#3451d1"><small>Stop scrolling</small>${pct(C.stop_rate)}</div><div style="background:#6b4fd8"><small>Click through</small>${pct(C.click_rate)}</div>${Object.entries(C.engagement).filter(e => e[0] !== "none").sort((a,b) => b[1]-a[1]).slice(0,2).map(([k,v]) => `<div style="background:#2563eb"><small>${esc(k)}</small>${v}</div>`).join("")}</div></div>`; }
  h += '<div class="box"><h2>In plain words</h2><ul>' + A.easy.map(x => `<li style="margin:6px 0">${esc(x)}</li>`).join("") + "</ul></div>";
  h += '<div class="box"><h2>How the score is made</h2>' + A.parts.map(p => `<div class="row" style="cursor:default"><div>${esc(p.name)} <span class="thin">${esc(p.why)}</span></div><div class="bar"><div class="fill" style="width:${Math.round(p.points/p.max*100)}%;background:${color(p.points/p.max)}"></div></div><div class="count">${p.points}/${p.max}</div></div>`).join("") + "</div>";
  h += '<div class="box"><h2>Detailed summary</h2>' + A.detailed.filter(s => s.title !== "Score breakdown").map(s => `<h3>${esc(s.title)}</h3><ul>` + s.lines.map(x => `<li>${esc(x)}</li>`).join("") + "</ul>").join("") + "</div>";
  el("t-audit").innerHTML = h;
}

function plan(){
  const P = R.practical; let h = '<div class="box"><h2>Fix these first</h2>';
  if (!P.fix_first.length) h += "<p>No one passed. Run a bigger panel before trusting that.</p>";
  P.fix_first.forEach((s,i) => { h += `<div class="step"><div class="num">${i+1}</div><div><b>${esc(s.reason)}</b> · ${s.buyers} buyer${s.buyers==1?"":"s"} (${pct(s.share)})<br>${esc(s.do)}</div></div>`; });
  h += "</div>";
  if (!P.best_group) h += '<div class="box"><h2>Who to sell to first</h2><p>No group said yes yet. Fix the top reasons above, change the pitch, and run the panel again (compare both versions with <b>panel.py compare</b>).</p></div>';
  if (P.best_group) h += `<div class="box"><h2>Who to sell to first</h2><p><b>${esc(P.best_group.group)}</b>: ${pct(P.best_group.rate)} of ${P.best_group.buyers} buyers said yes. Start your marketing here.</p></div>`;
  if (P.flip_top.length) h += '<div class="box"><h2>What would turn a no into a yes</h2>' + P.flip_top.map(f => `<blockquote>${esc(f)}</blockquote>`).join("") + "</div>";
  if (R.unprompted.length) h += '<div class="box"><h2>Doubts you did not think of</h2><p class="thin">Buyers raised these on their own. Add the repeat ones to your objection list.</p>' + R.unprompted.slice(0,10).map(u => `<blockquote>${esc(u[1])} <span class="thin">(${esc(u[0])})</span></blockquote>`).join("") + "</div>";
  h += '<div class="box"><h2>Then test it for real</h2><ol><li>Put the fixed offer on a one-page site or a WhatsApp/Instagram post with a real price.</li><li>Ask for a small deposit or a waitlist sign-up, not "would you buy?".</li><li>Talk to 10 real people from the best group above. Compare their objections with this panel.</li></ol></div>';
  el("t-plan").innerHTML = h;
}

function groupsOf(rows, key){
  const m = {}; rows.forEach(r => { const k = r[key] || "(not set)"; (m[k] = m[k] || []).push(r); });
  return Object.entries(m).map(([k,v]) => [k, v.length, v.filter(x => x.buys).length / v.length]).sort((a,b) => b[2]-a[2]);
}
const DIMS = [["market","Market"],["role","Role"],["segment","Segment / category"],["income_band","Income"],["gender","Gender"],["age_group","Age group"],["behaviour","Buying behaviour"],["bias","How they decide"],["language","Language"],["reviews_read","Reviews read"]];
function who(){
  let h = "";
  const dims = DIMS.concat(R.trait_names.map(t => ["trait:" + t, t]));
  dims.forEach(([key, title]) => {
    const g = groupsOf(B.map(b => Object.assign({}, b, key.startsWith("trait:") ? {[key]: (b.traits||{})[key.slice(6)]} : {})), key);
    if (g.length < 2 && key !== "segment") return;
    h += `<div class="box"><h2>${esc(title)}</h2>` + g.map(([k,n,r]) => `<div class="row" data-k="${esc(key)}" data-v="${esc(k)}"><div>${esc(k)} <span class="thin">(${n}${n<8?", thin":""})</span></div><div class="bar"><div class="fill" style="width:${Math.max(3,Math.round(r*100))}%;background:${color(r)}"></div></div><div class="count">${pct(r)}</div></div>`).join("") + "</div>";
  });
  el("t-who").innerHTML = h;
  el("t-who").onclick = e => { const row = e.target.closest(".row"); if(!row) return; filter = {[row.dataset.k]: row.dataset.v}; show("buyers"); buyers(); };
}

function why(){
  let h = "";
  [["Why they pass", R.why_not], ["Why they buy", R.why_yes]].forEach(([t, list]) => {
    if (!list.length) return;
    h += `<div class="box"><h2>${t}</h2>` + list.map(([code,n,quotes,ids]) => `<h3>${esc(code)} · ${n} buyer${n==1?"":"s"}</h3>` + quotes.map((q,i) => `<blockquote>${esc(q)} <span class="thin">(${esc(ids[i])})</span></blockquote>`).join("")).join("") + "</div>";
  });
  el("t-why").innerHTML = h;
}

function buyers(){
  const dims = DIMS.concat(R.trait_names.map(t => ["trait:" + t, t]));
  const val = (b,k) => k.startsWith("trait:") ? (b.traits||{})[k.slice(6)] : b[k];
  let h = '<div class="box"><div class="filters">';
  dims.forEach(([k,t]) => {
    const opts = [...new Set(B.map(b => val(b,k) == null || val(b,k) === "" ? "(not set)" : String(val(b,k))))].sort();
    if (opts.length < 2) return;
    h += `<select data-k="${esc(k)}"><option value="">${esc(t)}: all</option>` + opts.map(o => `<option ${filter[k]==o?"selected":""}>${esc(o)}</option>`).join("") + "</select>";
  });
  h += `<select data-k="buys_txt"><option value="">Answer: all</option><option ${filter.buys_txt=="buys"?"selected":""}>buys</option><option ${filter.buys_txt=="passes"?"selected":""}>passes</option></select>`;
  h += `<input id="q" placeholder="Search words" value="${esc(filter.q||"")}"><button class="sm" id="clr">Clear</button></div>`;
  const shown = B.filter(b => Object.entries(filter).every(([k,v]) => !v || (k === "q" ? JSON.stringify(b).toLowerCase().includes(v.toLowerCase()) : k === "buys_txt" ? (v === "buys") === b.buys : String(val(b,k) == null || val(b,k) === "" ? "(not set)" : val(b,k)) === v)));
  const yes = shown.filter(b => b.buys).length;
  h += `<p><b>${shown.length}</b> buyers shown · <b>${shown.length ? Math.round(yes/shown.length*100) : 0}%</b> buy</p>`;
  h += shown.map(b => `<details class="buyer"><summary><b>${esc(b.name)}</b> <span class="thin">${esc(b.id)}</span><span class="tag ${b.buys?"yes":"no"}">${b.buys?"buys":"passes"}${b.intent?" · "+b.intent+"/5":""}</span>${b.market?`<span class="tag">${esc(b.market)}</span>`:""}<span class="tag">${esc(b.age)}${b.gender?", "+esc(b.gender):""}</span><span class="tag">${esc(b.segment)}</span><span class="tag">${esc(b.income_txt)}</span></summary>
    <table><tr><td>Buys like</td><td>${esc(b.behaviour)}</td></tr><tr><td>Decides by</td><td>${esc(b.bias||"–")}</td></tr>${b.language?`<tr><td>Language</td><td>${esc(b.language)}</td></tr>`:""}<tr><td>Reviews read</td><td>${esc(b.reviews_read)}</td></tr>
    ${(b.questions_before_buying||[]).length?`<tr><td>Questions before paying</td><td>${(Array.isArray(b.questions_before_buying)?b.questions_before_buying:[b.questions_before_buying]).map(q => esc(typeof q === "object" && q ? q.question : q)).join("<br>")}</td></tr>`:""}
    <tr><td>Reason (${esc(b.reason_code)})</td><td>${esc(b.reason)}${b.reason_en?`<br><span class="thin">${esc(b.reason_en)}</span>`:""}</td></tr><tr><td>Main doubt</td><td>${esc(b.objection||"–")}</td></tr><tr><td>Doubt nobody planted</td><td>${esc(b.unprompted_doubt||"–")}</td></tr><tr><td>Would change their mind</td><td>${esc(b.would_change_my_mind||"–")}</td></tr></table></details>`).join("");
  el("t-buyers").innerHTML = h + "</div>";
  el("t-buyers").querySelectorAll("select").forEach(s => s.onchange = () => { filter[s.dataset.k] = s.value; buyers(); });
  el("q").onchange = e => { filter.q = e.target.value; buyers(); };
  el("clr").onclick = () => { filter = {}; buyers(); };
}

function faq(){
  let h = '<div class="box"><h2>Questions buyers need answered before they pay</h2><p class="thin">Put the answers on your page, in your FAQ, on WhatsApp replies and at checkout. Every unanswered question is a reason to wait.</p>';
  if (!R.questions || !R.questions.length) h += "<p>No questions recorded (older answer format).</p>";
  (R.questions||[]).forEach(q => { h += `<h3>${esc(q.topic)} <span class="chip">${q.count}</span></h3>` + q.examples.map((x,i) => `<blockquote>${esc(x)} <span class="thin">(${esc(q.ids[i])})</span></blockquote>`).join(""); });
  h += '<h3>Checklist for your page</h3><ul><li>Total price with every fee shown up front</li><li>The payment methods your buyers already use</li><li>Delivery or start time, in plain words</li><li>Refund, return and cancel policy in one line</li><li>Who you are, and how to reach you</li><li>What happens to their data</li></ul></div>';
  el("t-faq").innerHTML = h;
}

function verdict(p){
  if (R.price == null || p.currency !== R.price_currency) return "";
  const v = +R.price, f = x => p.currency + Math.round(x).toLocaleString();
  let msg, col;
  if (p.too_expensive != null && v >= p.too_expensive) { msg = `Your price ${esc(R.price_txt)} is at or above where most buyers say "too expensive" (${f(p.too_expensive)}). Test a lower entry price.`; col = "#fbece5"; }
  else if (p.expensive != null && v > p.expensive) { msg = `Your price ${esc(R.price_txt)} feels expensive to most buyers (above ${f(p.expensive)}). It needs strong proof or a cheaper first step.`; col = "#fdf4dc"; }
  else if (p.too_cheap != null && v <= p.too_cheap) { msg = `Your price ${esc(R.price_txt)} looks too cheap to trust. Raising it may sell more.`; col = "#fdf4dc"; }
  else { msg = `Your price ${esc(R.price_txt)} sits inside the range buyers accept.`; col = "#e5f3ef"; }
  return `<p style="background:${col};border-radius:10px;padding:10px"><b>Verdict:</b> ${msg}</p>`;
}

function reviews(){
  const A = R.after; if (!A) { el("t-reviews").innerHTML = "<div class='box'><p>No after-purchase answers in this panel (older answer format).</p></div>"; return; }
  const nc = A.nps == null ? "#94a3b8" : A.nps >= 30 ? "#0b7a66" : A.nps >= 0 ? "#b45309" : "#b4441b";
  let h = `<div class="box"><h2>If they bought it and it worked as promised</h2><div class="price">
    <div style="background:#b45309"><small>Average stars</small>${A.avg_stars != null ? A.avg_stars.toFixed(1) + " " : "–"}</div>
    <div style="background:${nc}"><small>Recommendation (NPS)</small>${A.nps != null ? (A.nps > 0 ? "+" : "") + A.nps : "–"}</div>
    <div style="background:#0b7a66"><small>Would recommend (9-10)</small>${A.promoters}</div><div style="background:#b4441b"><small>Would not (0-6)</small>${A.detractors}</div></div>
    <p class="thin">NPS = % scoring 9-10 minus % scoring 0-6, from -100 to +100. These are simulated expectations, not real reviews: never publish them as reviews.</p></div>`;
  h += '<div class="box"><h2>Stars they expect to give</h2>' + [5,4,3,2,1].map(k => { const n = A.stars[String(k)] || 0, tot = Object.values(A.stars).reduce((a,b) => a+b, 0) || 1;
    return `<div class="row" style="cursor:default"><div>${"".repeat(k)}</div><div class="bar"><div class="fill" style="width:${Math.round(n/tot*100)}%;background:${color((k-1)/4)}"></div></div><div class="count">${n}</div></div>`; }).join("") + "</div>";
  h += '<div class="box"><h2>What they would do after buying</h2>' + Object.entries(A.actions).sort((a,b) => b[1]-a[1]).map(([k,n]) => `<div class="row" style="cursor:default"><div>${esc(k)}</div><div class="bar"><div class="fill" style="width:${Math.round(n/(R.answered||1)*100)}%;background:#3451d1"></div></div><div class="count">${n}</div></div>`).join("") + "</div>";
  h += '<div class="box"><h2>The reviews they would write</h2><h3>Best</h3>' + (A.best_reviews.map(r => `<blockquote>${"".repeat(r[1])} ${esc(r[2])} <span class="thin">(${esc(r[0])})</span></blockquote>`).join("") || "<p class='thin'>None.</p>")
    + '<h3>Worst</h3>' + (A.worst_reviews.map(r => `<blockquote>${"".repeat(r[1])} ${esc(r[2])} <span class="thin">(${esc(r[0])})</span></blockquote>`).join("") || "<p class='thin'>None.</p>") + "</div>";
  el("t-reviews").innerHTML = h;
}

function price(){
  const P = R.practical.prices; let h = '<div class="box"><h2>What buyers would pay</h2>';
  if (!P.length) h += "<p>No complete price answers.</p>";
  P.forEach(p => {
    const f = v => v == null ? "–" : p.currency + Math.round(v).toLocaleString();
    h += `<p class="thin">Middle answer of ${p.answers} buyers, in ${esc(p.currency)}</p><div class="price"><div style="background:#94a3b8"><small>Too cheap to trust</small>${f(p.too_cheap)}</div><div style="background:#0b7a66"><small>A bargain</small>${f(p.bargain)}</div><div style="background:#b45309"><small>Getting expensive</small>${f(p.expensive)}</div><div style="background:#b4441b"><small>Too expensive</small>${f(p.too_expensive)}</div></div><p><b>Price to test:</b> between ${f(p.bargain)} and ${f(p.expensive)}. Above ${f(p.too_expensive)} most of these buyers walk away.</p>${verdict(p)}`;
  });
  h += '<p class="thin">For the full price analysis run founder-pricing\'s van_westendorp.py on the answers folder.</p></div>';
  el("t-price").innerHTML = h;
}

function facts(){
  let h = '<div class="box"><h2>Facts every buyer was shown</h2>';
  if (!R.sources.length) h += "<p>None. Add a market block or set a region to ground buyers in real data.</p>";
  h += R.sources.map(s => `<p>${s.region?`<span class="tag">${esc(s.region)}</span> `:""}${esc(s.text)} ${s.source?`<a href="${esc(s.source)}" target="_blank" rel="noopener">source</a>`:'<b style="color:#b4441b">no source</b>'}</p>`).join("");
  el("t-facts").innerHTML = h + "</div>";
}
kpis(); tabs(); audit(); plan(); who(); why(); faq(); reviews(); buyers(); price(); facts();
</script></body></html>
"""


def results_html(res):
    """One self-contained, interactive page: next steps, who buys (click to filter), why not, every buyer,
    price, and the facts buyers were shown with their sources. Opens in any browser, no internet needed."""
    data = dict(res)
    data["money"] = None
    if res.get("revenue_first_month_per_100_reached") is not None:
        data["money"] = "%s%s" % (res.get("price_currency", "$"), _money(res["revenue_first_month_per_100_reached"],
                                                                   res.get("customer_for_format") or {}))
    if res.get("price") is not None:
        data["price_txt"] = "%s%s" % (res.get("price_currency", "$"), _price_text(res["price"], res))
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return (REPORT.replace("__TITLE__", _esc(res["business"])).replace("__SEED__", _esc(res["seed"]))
            .replace("__DATA__", blob))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default=os.path.join("founder", "panel"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init")
    i.add_argument("--customer", required=True)
    i.add_argument("--pitch", required=True)
    i.add_argument("--n", type=int, default=None, help="number of buyers (default 100, or the headcounts in customer.json)")
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
            asked = a.quick or a.size or a.n is not None
            n = SIZES["small"] if a.quick else SIZES[a.size] if a.size else (a.n if a.n is not None else 100)
            cards = init(a.dir, a.customer, a.pitch, n, a.seed, a.only, scale=bool(asked))
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
            base_dir = os.path.dirname(out) or "."
            with open(os.path.join(base_dir, "audit.md"), "w", encoding="utf-8") as fh:
                fh.write(audit_md(res))
            with open(os.path.join(base_dir, "sales-kit-brief.md"), "w", encoding="utf-8") as fh:
                fh.write(sales_kit_brief(res))
            html = os.path.splitext(out)[0] + ".html"
            with open(html, "w", encoding="utf-8") as fh:
                fh.write(results_html(res))
            print("%d buy · %d pass (%.0f%%). Score %d/100 (%s). Wrote %s, %s, audit.md and sales-kit-brief.md"
                  % (res["buys"], res["passes"], res["buy_rate"] * 100, res["audit"]["score"], res["audit"]["grade"], out, html))
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
