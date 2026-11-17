import json
import re
import os
import shutil
import tempfile
import unittest

from _load import load, example

panel = load("founder-consumer", "panel")


def customer():
    with open(example("founder-consumer", "customer.example.json"), encoding="utf-8") as fh:
        return json.load(fh)


class Deal(unittest.TestCase):
    def test_same_seed_same_cards(self):
        self.assertEqual(panel.deal(customer(), 100, 7), panel.deal(customer(), 100, 7))
        self.assertNotEqual(panel.deal(customer(), 100, 7), panel.deal(customer(), 100, 8))

    def test_quotas_are_exact_and_names_unique(self):
        cards = panel.deal(customer(), 100, 3)
        segs = {}
        for c in cards:
            segs[c["segment"]] = segs.get(c["segment"], 0) + 1
        self.assertEqual(segs, {"Early-career professional": 45, "Mid-career professional": 40, "High earner": 15})
        self.assertEqual(len({c["name"] for c in cards}), 100)
        self.assertEqual(cards[0]["id"], "P001")
        self.assertEqual(cards[-1]["id"], "P100")
        for c in cards:
            seg = next(s for s in customer()["segments"] if s["name"] == c["segment"])
            self.assertTrue(seg["income"][0] - 500 <= c["income"] <= seg["income"][1] + 500)
            self.assertIn(c["objection"], customer()["objections"] + [""])
        self.assertEqual(sum(1 for c in cards if c["objection"] == ""), 20)

    def test_bad_profile_is_refused(self):
        c = customer()
        del c["objections"]
        with self.assertRaises(panel.PanelError):
            panel.deal(c)


class Flow(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        panel.init(self.d, example("founder-consumer", "customer.example.json"),
                   example("founder-consumer", "pitch.example.md"), n=20, seed=5)

    def tearDown(self):
        shutil.rmtree(self.d)

    def answer(self, pid, buys, code="price", **extra):
        a = {"id": pid, "buys": buys, "reason_code": code, "reason": "because %s" % pid,
             "purchases_first_month": 4 if buys else 0, "would_change_my_mind": "" if buys else "a lower price"}
        a.update(extra)
        with open(os.path.join(self.d, "answers", pid + ".json"), "w") as fh:
            json.dump(a, fh)

    def test_briefs_carry_the_card_and_the_pitch(self):
        waves = panel.write_briefs(self.d, wave=10)
        self.assertEqual([len(w) for w in waves], [10, 10])
        with open(waves[0][0][1], encoding="utf-8") as fh:
            brief = fh.read()
        self.assertIn("Moss Matcha Bar", brief)
        self.assertIn('"id": "P001"', brief)
        self.assertIn("Do not be agreeable", brief)

    def test_answered_buyers_get_no_new_brief(self):
        self.answer("P001", True, "quality")
        ids = [j[0] for w in panel.write_briefs(self.d) for j in w]
        self.assertNotIn("P001", ids)
        self.assertEqual(len(ids), 19)

    def test_check_and_tally(self):
        for i in range(1, 21):
            pid = "P%03d" % i
            self.answer(pid, i <= 8, "quality" if i <= 8 else ("price" if i <= 15 else "habit"))
        # one broken answer: wrong reason code
        self.answer("P020", False, "vibes")
        probs = dict(panel.check(self.d))
        self.assertEqual(list(probs), ["P020"])
        res = panel.tally(self.d)
        self.assertEqual((res["buys"], res["passes"], res["answered"]), (8, 11, 19))
        self.assertEqual(res["why_not"][0][0], "price")
        self.assertEqual(res["why_not"][0][1], 7)
        self.assertEqual(res["skipped"][0][0], "P020")
        text = panel.results_md(res)
        self.assertIn("**8 buy · 11 pass**", text)
        self.assertIn("not customers", text)

    def test_save_files_a_printed_answer_and_refuses_junk(self):
        reply = 'Here is my answer:\n```json\n{"id": "P002", "buys": false, "reason_code": "price", "reason": "too much"}\n```'
        panel.save(self.d, "P002", reply)
        self.assertNotIn("P002", dict(panel.check(self.d)))
        with self.assertRaises(panel.PanelError):
            panel.save(self.d, "P003", '{"id": "P003", "buys": "maybe", "reason_code": "price", "reason": "x"}')
        self.assertEqual(dict(panel.check(self.d))["P003"], "missing")
        with self.assertRaises(panel.PanelError):
            panel.save(self.d, "P999", '{"id": "P999"}')

    def test_tally_with_no_answers_refuses(self):
        with self.assertRaises(panel.PanelError):
            panel.tally(self.d)


if __name__ == "__main__":
    unittest.main()


class Plus(unittest.TestCase):
    """Tests for the founder-skill-plus additions."""
    def setUp(self):
        self.d = tempfile.mkdtemp()
        c = customer()
        c.update({"locale": "IN", "currency": "\u20b9", "where": "Pune, Koregaon Park", "skeptic_share": 0.25})
        for s_ in c["segments"]:
            s_["income"] = [s_["income"][0] * 10, s_["income"][1] * 10]
        self.cpath = os.path.join(self.d, "c.json")
        with open(self.cpath, "w") as fh:
            json.dump(c, fh)
        self.pdir = os.path.join(self.d, "A")
        panel.init(self.pdir, self.cpath, example("founder-consumer", "pitch.example.md"), n=20, seed=5)

    def tearDown(self):
        shutil.rmtree(self.d)

    def ans(self, d, pid, intent, **x):
        a = {"id": pid, "intent": intent, "buys": intent >= 4, "reason_code": "price", "reason": "r " + pid}
        a.update(x)
        with open(os.path.join(d, "answers", pid + ".json"), "w") as fh:
            json.dump(a, fh)

    def test_indian_names_currency_and_open_cards(self):
        _, cards = panel.load_state(self.pdir)
        self.assertTrue(all(c["name"].split()[0] in panel.NAMES_IN for c in cards))
        self.assertEqual(sum(1 for c in cards if c["objection"] == ""), 5)
        panel.write_briefs(self.pdir)
        open_card = next(c for c in cards if c["objection"] == "")
        with open(os.path.join(self.pdir, "briefs", open_card["id"] + ".md"), encoding="utf-8") as fh:
            b = fh.read()
        self.assertIn("\u20b9", b)
        self.assertIn("Pune", b)
        self.assertIn("Nobody has told you what to doubt", b)
        self.assertIn("unprompted_doubt", b)

    def test_intent_must_match_buys(self):
        self.ans(self.pdir, "P001", 4, buys=False)
        self.assertIn("intent", panel._answer_ok(os.path.join(self.pdir, "answers", "P001.json"), "P001"))
        self.ans(self.pdir, "P001", 7)
        self.assertIn("1 to 5", panel._answer_ok(os.path.join(self.pdir, "answers", "P001.json"), "P001"))

    def test_realistic_rate_and_interval(self):
        intents = [5, 5, 4, 4, 4, 4, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1]
        for i, k in enumerate(intents, 1):
            self.ans(self.pdir, "P%03d" % i, k, unprompted_doubt="parking?" if i == 3 else "")
        res = panel.tally(self.pdir)
        self.assertAlmostEqual(res["buy_rate"], 6 / 20)
        # (2*0.75 + 4*0.25 + 2*0.10) / 20 = 2.7/20
        self.assertAlmostEqual(res["realistic_rate"], 2.7 / 20)
        lo, hi = res["buy_rate_interval_90"]
        self.assertTrue(lo < 0.30 < hi)
        self.assertEqual(res["unprompted"], [("P003", "parking?")])
        md = panel.results_md(res)
        self.assertIn("Realistic estimate", md)
        self.assertIn("Doubts nobody planted", md)
        self.assertIn("\u20b9", md)

    def test_compare_same_buyers(self):
        bdir = os.path.join(self.d, "B")
        panel.init(bdir, self.cpath, example("founder-consumer", "pitch.example.md"), n=20, seed=5)
        for i in range(1, 21):
            pid = "P%03d" % i
            self.ans(self.pdir, pid, 2)
            self.ans(bdir, pid, 5 if i <= 4 else 2)
        for d in (self.pdir, bdir):
            res = panel.tally(d)
            panel._write_json(os.path.join(d, "results.json"), res)
        md = panel.compare(self.pdir, bdir)
        self.assertIn("4 buyers switched to yes", md)
        self.assertNotIn("Warning", md)


class World(unittest.TestCase):
    """Regions, languages, gender, age groups, custom dimensions and the money line."""
    def make(self, **extra):
        c = customer()
        c.update(extra)
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        cp = os.path.join(d, "c.json")
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(c, fh, ensure_ascii=False)
        pd = os.path.join(d, "panel")
        panel.init(pd, cp, example("founder-consumer", "pitch.example.md"), n=40, seed=9)
        return pd

    def brief(self, pd, pid):
        panel.write_briefs(pd)
        with open(os.path.join(pd, "briefs", pid + ".md"), encoding="utf-8") as fh:
            return fh.read()

    def test_every_region_deals(self):
        for code, reg in panel.REGIONS.items():
            cards = panel.deal(dict(customer(), region=code), 150, 1)
            self.assertEqual(len({c["name"] for c in cards}), 150, code)
            self.assertEqual(panel._currency(dict(customer(), region=code)), reg["currency"])

    def test_unknown_region_is_refused(self):
        with self.assertRaises(panel.PanelError):
            panel.deal(dict(customer(), region="XX"))

    def test_gender_age_and_traits_follow_quotas(self):
        c = dict(customer(), region="US",
                 genders=[{"name": "female", "share": 0.6}, {"name": "male", "share": 0.4}],
                 age_groups=[{"name": "18-24", "range": [18, 24], "share": 0.5}, {"name": "55+", "range": [55, 75], "share": 0.5}],
                 dimensions=[{"name": "diet", "values": [{"name": "vegetarian", "share": 0.25}, {"name": "eats meat", "share": 0.75}]}])
        cards = panel.deal(c, 100, 4)
        self.assertEqual(sum(1 for x in cards if x["gender"] == "female"), 60)
        self.assertEqual(sum(1 for x in cards if x["traits"]["diet"] == "vegetarian"), 25)
        us = panel.REGIONS["US"]["names"]
        for x in cards:
            lo, hi = (18, 24) if x["age_group"] == "18-24" else (55, 75)
            self.assertTrue(lo <= x["age"] <= hi)
            base = re.sub(r" ([A-Z]\.|\d+)$", "", x["name"])
            self.assertIn(base, us["f"] if x["gender"] == "female" else us["m"])

    def test_bad_age_group_is_refused(self):
        with self.assertRaises(panel.PanelError):
            panel.deal(dict(customer(), age_groups=[{"name": "x", "range": [40, 20], "share": 1}]))

    def test_brief_carries_language_gender_traits_and_no_stereotype_line(self):
        pd = self.make(region="CN", language="Mandarin Chinese", genders=[{"name": "woman", "share": 1}],
                       dimensions=[{"name": "city tier", "values": [{"name": "tier 1", "share": 1}]}])
        b = self.brief(pd, "P001")
        self.assertIn("\u00a5", b)
        self.assertIn(", woman.", b)
        self.assertIn("Your city tier: tier 1.", b)
        self.assertIn("Mandarin Chinese", b)
        self.assertIn("reason_en", b)
        self.assertIn("never as a stereotype", b)

    def test_english_brief_has_no_translation_field(self):
        b = self.brief(self.make(region="UK", language="English"), "P001")
        self.assertNotIn("reason_en", b)
        self.assertIn("\u00a3", b)

    def test_money_line_and_group_tables(self):
        pd = self.make(region="US", price=10, genders=[{"name": "male", "share": 0.5}, {"name": "female", "share": 0.5}])
        for i in range(1, 41):
            pid = "P%03d" % i
            intent = 5 if i <= 8 else 2
            a = {"id": pid, "intent": intent, "buys": intent >= 4, "reason_code": "price", "reason": "hola",
                 "reason_en": "hello", "purchases_first_month": 3 if intent >= 4 else 0}
            with open(os.path.join(pd, "answers", pid + ".json"), "w") as fh:
                json.dump(a, fh)
        res = panel.tally(pd)
        # realistic = 8 * 0.75 / 40 = 0.15 -> 15 buyers per 100 x 3 purchases x $10 = $450
        self.assertAlmostEqual(res["revenue_first_month_per_100_reached"], 450.0)
        md = panel.results_md(res)
        self.assertIn("$450", md)
        self.assertIn("## By gender", md)
        self.assertIn("[English: hello]", md)


class ReviewFixes(unittest.TestCase):
    """Defects found in the pre-publish review, each pinned by a test."""
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d)
        panel.init(self.d, example("founder-consumer", "customer.example.json"),
                   example("founder-consumer", "pitch.example.md"), n=4, seed=2)

    def put(self, pid, obj):
        path = os.path.join(self.d, "answers", pid + ".json")
        with open(path, "w") as fh:
            json.dump(obj, fh) if not isinstance(obj, str) else fh.write(obj)
        return path

    def good(self, pid, **x):
        a = {"id": pid, "intent": 4, "buys": True, "reason_code": "price", "reason": "ok"}
        a.update(x)
        return a

    def test_list_answer_and_null_reason_are_reported_not_crashing(self):
        self.assertEqual(panel._answer_ok(self.put("P001", [self.good("P001")]), "P001"), "not a JSON object")
        self.assertIn("reason", panel._answer_ok(self.put("P002", self.good("P002", reason=None)), "P002"))
        self.assertIn("intent", panel._answer_ok(self.put("P003", self.good("P003", intent=True)), "P003"))
        self.put("P004", self.good("P004"))
        res = panel.tally(self.d)
        self.assertEqual(res["answered"], 1)

    def test_compare_skips_broken_answers_and_explains_missing_tally(self):
        b = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, b)
        panel.init(b, example("founder-consumer", "customer.example.json"),
                   example("founder-consumer", "pitch.example.md"), n=4, seed=2)
        with self.assertRaises(panel.PanelError):
            panel.compare(self.d, b)
        for d in (self.d, b):
            for i in range(1, 5):
                with open(os.path.join(d, "answers", "P%03d.json" % i), "w") as fh:
                    json.dump(self.good("P%03d" % i), fh)
            panel._write_json(os.path.join(d, "results.json"), panel.tally(d))
        self.put("P001", "oops")
        self.assertIn("Pitch A vs pitch B", panel.compare(self.d, b))

    def test_gb_alias_lowercase_and_string_price(self):
        self.assertEqual(panel._currency({"region": "gb"}), "\u00a3")
        self.assertEqual(panel._price_num("\u20b92,50,000"), 250000.0)
        self.assertEqual(panel._price_num("$6.50"), 6.5)

    def test_quick_flag_and_singular_wording(self):
        d = os.path.join(self.d, "q")
        panel.main(["--dir", d, "init", "--customer", example("founder-consumer", "customer.example.json"),
                    "--pitch", example("founder-consumer", "pitch.example.md"), "--quick", "--seed", "1"])
        self.assertEqual(len(panel.load_state(d)[1]), 20)
        self.put("P001", self.good("P001"))
        md = panel.results_md(panel.tally(self.d))
        self.assertIn("out of 1 simulated buyer.", md)

    def test_partial_intent_is_disclosed(self):
        self.put("P001", self.good("P001"))
        old = self.good("P002")
        del old["intent"]
        self.put("P002", old)
        md = panel.results_md(panel.tally(self.d))
        self.assertIn("Only 1 of the 2 answers gave an intent score", md)

    def test_indian_names_use_initials_not_numbers(self):
        c = customer()
        c.update({"region": "IN", "genders": [{"name": "male", "share": 1}]})
        names = [x["name"] for x in panel.deal(c, 100, 3)]
        self.assertEqual(len(set(names)), 100)
        self.assertFalse(any(n[-1].isdigit() for n in names))


class Sizes(unittest.TestCase):
    """Pick the panel size, exact headcounts per category, and which categories to run."""
    def cats(self):
        c = customer()
        c["segments"] = [{"name": "Category A", "count": 50, "income": [100, 200]},
                         {"name": "Category B", "count": 30, "income": [50, 100]},
                         {"name": "Category C", "count": 20, "income": [10, 50]}]
        return c

    def test_exact_counts_win_over_n(self):
        cards = panel.deal(self.cats(), n=7, seed=1)
        self.assertEqual(len(cards), 100)
        self.assertEqual(sum(1 for x in cards if x["segment"] == "Category B"), 30)

    def test_only_some_categories(self):
        c = panel.pick_segments(self.cats(), "category a, Category C")
        cards = panel.deal(c, seed=1)
        self.assertEqual(len(cards), 70)
        self.assertEqual({x["segment"] for x in cards}, {"Category A", "Category C"})
        with self.assertRaises(panel.PanelError):
            panel.pick_segments(self.cats(), "Category Z")
        c = self.cats()
        c["segments"][0]["name"] = "Category A: HNI buyers"
        self.assertEqual([x["name"] for x in panel.pick_segments(c, "category a")["segments"]], ["Category A: HNI buyers"])

    def test_mixed_count_and_share_is_refused(self):
        c = self.cats()
        del c["segments"][0]["count"]
        c["segments"][0]["share"] = 0.5
        with self.assertRaises(panel.PanelError):
            panel.deal(c)

    def test_size_presets_through_the_cli(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        for size, want in (("small", 20), ("large", 250)):
            pd = os.path.join(d, size)
            panel.main(["--dir", pd, "init", "--customer", example("founder-consumer", "customer.example.json"),
                        "--pitch", example("founder-consumer", "pitch.example.md"), "--size", size, "--seed", "1"])
            self.assertEqual(panel.load_state(pd)[0]["n"], want)
