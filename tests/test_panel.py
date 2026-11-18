import contextlib
import io
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
        with contextlib.redirect_stdout(io.StringIO()):
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
            with contextlib.redirect_stdout(io.StringIO()):
                panel.main(["--dir", pd, "init", "--customer", example("founder-consumer", "customer.example.json"),
                            "--pitch", example("founder-consumer", "pitch.example.md"), "--size", size, "--seed", "1"])
            self.assertEqual(panel.load_state(pd)[0]["n"], want)


class MarketAndReport(unittest.TestCase):
    """Language mix, real market facts and reviews per buyer, and the HTML report."""
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d)
        c = customer()
        c["languages"] = [{"name": "English", "share": 0.5}, {"name": "Hindi", "share": 0.5}]
        c["behaviours"] = [{"name": "Reads every review", "share": 0.5, "how": "Checks reviews first."},
                           {"name": "Impulse buyer", "share": 0.5, "how": "Buys on the spot."}]
        c["market"] = {"facts": [{"text": "Most people pay by UPI.", "source": "https://example.org/a"}],
                       "reviews": [{"about": "X", "stars": 2, "text": "Too sweet.", "source": "https://example.org/r1"},
                                   {"about": "Y", "stars": 5, "text": "Loved it.", "source": "https://example.org/r2"},
                                   {"about": "Z", "stars": 3, "text": "Okay.", "source": ""}]}
        self.c = c
        self.cp = os.path.join(self.d, "c.json")
        with open(self.cp, "w", encoding="utf-8") as fh:
            json.dump(c, fh)
        self.pd = os.path.join(self.d, "p")
        panel.init(self.pd, self.cp, example("founder-consumer", "pitch.example.md"), n=40, seed=3)

    def cards(self):
        return panel.load_state(self.pd)[1]

    def test_language_mix_and_translation_only_for_non_english(self):
        cards = self.cards()
        self.assertEqual(sum(1 for c in cards if c["language"] == "Hindi"), 20)
        panel.write_briefs(self.pd)
        for c in cards:
            with open(os.path.join(self.pd, "briefs", c["id"] + ".md"), encoding="utf-8") as fh:
                b = fh.read()
            self.assertEqual("reason_en" in b, c["language"] == "Hindi")

    def test_careful_shoppers_read_three_reviews_and_see_facts(self):
        cards = self.cards()
        for c in cards:
            if c["behaviour"] == "Reads every review":
                self.assertEqual(len(c["reviews"]), 3)
            else:
                self.assertLessEqual(len(c["reviews"]), 2)
        panel.write_briefs(self.pd)
        careful = next(c for c in cards if c["behaviour"] == "Reads every review")
        with open(os.path.join(self.pd, "briefs", careful["id"] + ".md"), encoding="utf-8") as fh:
            b = fh.read()
        self.assertIn("Most people pay by UPI.", b)
        self.assertIn('2/5 review about X: "Too sweet."', b)

    def test_unsourced_items_are_flagged(self):
        self.assertEqual(panel.unsourced(self.c), ["1 market reviews have no 'source' link. Buyers are told these are"
                                                   " real: add links, or remove them."])

    def test_bad_market_is_refused(self):
        with self.assertRaises(panel.PanelError):
            panel.deal(dict(self.c, market={"reviews": [{"stars": 3}]}))

    def test_tally_groups_and_html_report(self):
        for i, c in enumerate(self.cards()):
            intent = 5 if c["reviews"] else 2
            a = {"id": c["id"], "intent": intent, "buys": intent >= 4, "reason_code": "need", "reason": "r </script><b>",
                 "purchases_first_month": 1 if intent >= 4 else 0}
            with open(os.path.join(self.pd, "answers", c["id"] + ".json"), "w") as fh:
                json.dump(a, fh)
        res = panel.tally(self.pd)
        groups = dict((k, r) for k, n, r in res["by_reviews_read"])
        self.assertEqual(groups["read no reviews"], 0.0)
        self.assertTrue(res["by_language"])
        html = panel.results_html(res)
        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        self.assertEqual(html.count("</script>"), 1)  # a buyer's text cannot close the script early
        self.assertIn('"reviews_read": "3"', html)
        self.assertIn("What to do next", html)
        self.assertEqual(res["practical"]["fix_first"][0]["reason"], "need")
        self.assertTrue(res["practical"]["best_group"])


class Markets(unittest.TestCase):
    """Mixed panels: buyers from several markets, each with its own region, currency, money and facts."""
    def world(self, **extra):
        c = customer()
        c.update({"region": "US", "markets": [
            {"name": "India", "region": "IN", "count": 30, "segments": [{"name": "Salaried", "share": 1, "income": [600000, 1500000]}]},
            {"name": "Europe", "region": "EU", "count": 20},
            {"name": "USA", "region": "US", "count": 10}]})
        c.update(extra)
        return c

    def test_counts_regions_and_ids(self):
        cards = panel.deal(self.world(), seed=2)
        self.assertEqual(len(cards), 60)
        self.assertEqual([c["id"] for c in cards][:2], ["P001", "P002"])
        self.assertEqual(sum(1 for c in cards if c["market"] == "India"), 30)
        india = [c for c in cards if c["market"] == "India"]
        self.assertTrue(all(c["region"] == "IN" and c["segment"] == "Salaried" for c in india))
        self.assertTrue(all(600000 <= c["income"] <= 1500000 for c in india))

    def test_briefs_use_each_markets_currency_and_facts_and_one_price_currency(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        cp = os.path.join(d, "c.json")
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(self.world(), fh)
        panel.init(d, cp, example("founder-consumer", "pitch.example.md"), seed=2)
        panel.write_briefs(d)
        cards = panel.load_state(d)[1]
        ind = next(c for c in cards if c["market"] == "India")
        eu = next(c for c in cards if c["market"] == "Europe")
        with open(os.path.join(d, "briefs", ind["id"] + ".md"), encoding="utf-8") as fh:
            bi = fh.read()
        with open(os.path.join(d, "briefs", eu["id"] + ".md"), encoding="utf-8") as fh:
            be = fh.read()
        self.assertIn("\u20b9", bi)
        self.assertIn("UPI", bi)
        self.assertIn("\u20ac", be)
        self.assertIn("euro area", be)
        self.assertIn('"price_currency": "$"', bi)
        self.assertIn("How you tend to decide:", bi)

    def test_tally_bands_per_market_and_groups(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        cp = os.path.join(d, "c.json")
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(self.world(), fh)
        panel.init(d, cp, example("founder-consumer", "pitch.example.md"), seed=2)
        for c in panel.load_state(d)[1]:
            with open(os.path.join(d, "answers", c["id"] + ".json"), "w") as fh:
                json.dump({"id": c["id"], "intent": 5 if c["market"] == "India" else 1,
                           "buys": c["market"] == "India", "reason_code": "price", "reason": "x"}, fh)
        res = panel.tally(d)
        mk = dict((k, r) for k, n, r in res["by_market"])
        self.assertEqual(mk["India"], 1.0)
        self.assertEqual(mk["Europe"], 0.0)
        self.assertTrue(all(k.split(":")[0] in ("India", "Europe", "USA") for k, n, r in res["by_income"]))
        self.assertTrue(res["by_bias"])

    def test_biases_spread_and_can_be_limited_or_off(self):
        cards = panel.deal(customer(), 20, 1)
        self.assertEqual(len({c["bias"] for c in cards}), len(panel.BIASES))
        only = panel.deal(dict(customer(), biases=["anchoring"]), 10, 1)
        self.assertEqual({c["bias"] for c in only}, {"anchoring"})
        self.assertEqual({c["bias"] for c in panel.deal(dict(customer(), biases=False), 5, 1)}, {""})
        with self.assertRaises(panel.PanelError):
            panel.deal(dict(customer(), biases=["mind reading"]))

    def test_every_region_fact_has_a_source(self):
        for reg, facts in panel.REGION_FACTS.items():
            for f in facts:
                self.assertTrue(f["source"].startswith("https://"), reg)


class Realism(unittest.TestCase):
    def test_segment_age_wins_and_sets_the_age_group(self):
        c = customer()
        c["segments"] = [{"name": "Student", "count": 30, "income": [0, 1000], "age": [18, 24]},
                         {"name": "Executive", "count": 20, "income": [9000, 9999], "age": [40, 55]}]
        c["age_groups"] = [{"name": "young", "range": [18, 30], "share": 0.5}, {"name": "older", "range": [31, 70], "share": 0.5}]
        for x in panel.deal(c, seed=3):
            if x["segment"] == "Student":
                self.assertTrue(18 <= x["age"] <= 24)
                self.assertEqual(x["age_group"], "young")
            else:
                self.assertTrue(40 <= x["age"] <= 55)
                self.assertEqual(x["age_group"], "older")

    def test_practical_checks_and_questions_reach_the_report(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        panel.init(d, example("founder-consumer", "customer.example.json"), example("founder-consumer", "pitch.example.md"), n=3, seed=1)
        panel.write_briefs(d)
        with open(os.path.join(d, "briefs", "P001.md"), encoding="utf-8") as fh:
            self.assertIn("refunds, cancelling", fh.read())
        qs = [["Is there a delivery fee?"], "Can I get a refund?",
              [{"question": "\u8c01\u5728\u7ecf\u8425\uff1f", "topic": "who is behind it"}, ""]]
        for i, q in enumerate(qs, 1):
            with open(os.path.join(d, "answers", "P%03d.json" % i), "w") as fh:
                json.dump({"id": "P%03d" % i, "intent": 2, "buys": False, "reason_code": "trust", "reason": "x",
                           "questions_before_buying": q}, fh)
        res = panel.tally(d)
        topics = {q["topic"] for q in res["questions"]}
        self.assertEqual(topics, {"price, fees and discounts", "refunds, cancelling, free trial", "who is behind it"})
        self.assertIn("Questions buyers need answered", panel.results_md(res))
        panel.write_briefs(d)  # brief lists the topic names
        self.assertEqual(len(panel.TOPIC_NAMES), len(panel.QUESTION_TOPICS) + 1)


class SizeWithCounts(unittest.TestCase):
    def test_size_scales_headcounts_and_keeps_the_mix(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        for args, want in (([], 100), (["--size", "small"], 20), (["--n", "50"], 50)):
            pd = os.path.join(d, "x%d" % want)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                panel.main(["--dir", pd, "init", "--customer", example("founder-consumer", "customer.world.example.json"),
                            "--pitch", example("founder-consumer", "pitch.world.example.md"), "--seed", "1"] + args)
            cards = panel.load_state(pd)[1]
            self.assertEqual(len(cards), want)
            india = sum(1 for c in cards if c["market"] == "India")
            self.assertAlmostEqual(india / float(want), 0.4, delta=0.05)


class ReviewFixes2(unittest.TestCase):
    """Second pre-publish review: each finding pinned by a test."""
    def world(self):
        with open(example("founder-consumer", "customer.world.example.json"), encoding="utf-8") as fh:
            return json.load(fh)

    def test_price_formats(self):
        for txt, want in (("Rs. 199", 199.0), ("1.299,00 \u20ac", 1299.0), ("\u20b92,50,000", 250000.0),
                          ("$9.99/mo", 9.99), ("6,50", 6.5), ("1,299", 1299.0), ("1.299.000", 1299000.0), ("abc", None)):
            self.assertEqual(panel._price_num(txt), want, txt)

    def test_only_works_inside_markets(self):
        c = panel.pick_segments(self.world(), "student")
        cards = panel.deal(c, seed=1)
        self.assertEqual({x["segment"] for x in cards}, {"Student"})
        self.assertEqual(len(cards), 100)
        with self.assertRaises(panel.PanelError):
            panel.pick_segments(self.world(), "Astronaut")

    def test_duplicate_market_names_are_refused(self):
        c = self.world()
        c["markets"][1]["name"] = "india"
        with self.assertRaises(panel.PanelError):
            panel.deal(c)

    def test_market_count_wins_over_segment_counts(self):
        c = self.world()
        for m in c["markets"]:
            for sg in m["segments"]:
                sg.pop("share", None)
                sg["count"] = 5
        cards = panel.deal(c, seed=1)
        self.assertEqual(sum(1 for x in cards if x["market"] == "India"), 40)

    def test_money_is_in_the_price_currency(self):
        c = dict(customer(), region="IN", price=249, price_currency="\u20b9")
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        cp = os.path.join(d, "c.json")
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(dict(c, markets=[{"name": "Pune", "region": "IN", "count": 4}, {"name": "NYC", "region": "US", "count": 2}]), fh)
        panel.init(d, cp, example("founder-consumer", "pitch.example.md"), seed=1)
        for x in panel.load_state(d)[1]:
            with open(os.path.join(d, "answers", x["id"] + ".json"), "w") as fh:
                json.dump({"id": x["id"], "intent": 5, "buys": True, "reason_code": "need", "reason": "y", "purchases_first_month": 1}, fh)
        res = panel.tally(d)
        md = panel.results_md(res)
        self.assertIn("at \u20b9249", md)
        self.assertNotIn("at $249", md)

    def test_no_income_reads_naturally(self):
        c = customer()
        c["segments"] = [{"name": "Student", "count": 2, "income": [0, 0]}]
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        cp = os.path.join(d, "c.json")
        with open(cp, "w") as fh:
            json.dump(c, fh)
        panel.init(d, cp, example("founder-consumer", "pitch.example.md"), seed=1)
        panel.write_briefs(d)
        with open(os.path.join(d, "briefs", "P001.md"), encoding="utf-8") as fh:
            b = fh.read()
        self.assertIn("no income of your own", b)
        self.assertNotIn("$0 a year", b)


class B2BAndTemplates(unittest.TestCase):
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def template(self, name):
        with open(os.path.join(self.ROOT, "docs", "templates", name + ".json"), encoding="utf-8") as fh:
            return json.load(fh)

    def test_every_template_deals_and_is_listed(self):
        with open(os.path.join(self.ROOT, "docs", "templates", "index.json"), encoding="utf-8") as fh:
            index = json.load(fh)
        self.assertGreaterEqual(len(index), 10)
        for t in index:
            c = self.template(t["id"])
            self.assertTrue(c["_pitch"].strip(), t["id"])
            self.assertEqual(c.get("mode", "b2c"), t["mode"])
            cards = panel.deal(c, 30, 1)
            self.assertEqual(len(cards), 30, t["id"])
            for x in cards:
                seg = next(sg for sg in c["segments"] if sg["name"] == x["segment"])
                self.assertTrue(seg["age"][0] <= x["age"] <= seg["age"][1], t["id"])

    def test_b2b_brief_and_tally_by_role(self):
        c = self.template("security-cctv")
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        cp, pp = os.path.join(d, "c.json"), os.path.join(d, "pitch.md")
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(c, fh, ensure_ascii=False)
        with open(pp, "w", encoding="utf-8") as fh:
            fh.write(c["_pitch"])
        panel.init(d, cp, pp, n=12, seed=4)
        panel.write_briefs(d)
        cards = panel.load_state(d)[1]
        with open(os.path.join(d, "briefs", "P001.md"), encoding="utf-8") as fh:
            b = fh.read()
        for phrase in ("simulated business buyer", "Your role: ", "Your business: ", "a year on purchases like this",
                       "careful business buyer", "units or orders", "with its budget, its approvals"):
            self.assertIn(phrase, b)
        self.assertNotIn("consumer panel", b)
        for x in cards:
            with open(os.path.join(d, "answers", x["id"] + ".json"), "w") as fh:
                json.dump({"id": x["id"], "intent": 4 if x["role"] == "Owner" else 2, "buys": x["role"] == "Owner",
                           "reason_code": "price", "reason": "x",
                           "questions_before_buying": [{"question": "What does the AMC cost after year one?",
                                                        "topic": "contract, invoice, AMC and payment terms"}]}, fh)
        res = panel.tally(d)
        roles = dict((k, r) for k, n, r in res["by_role"])
        self.assertEqual(roles["Owner"], 1.0)
        self.assertEqual(res["questions"][0]["topic"], "contract, invoice, AMC and payment terms")
        self.assertTrue(all(b["income_txt"].startswith("budget ") for b in res["buyers"]))

    def test_bad_mode_is_refused(self):
        with self.assertRaises(panel.PanelError):
            panel.deal(dict(customer(), mode="b2x"))


class SegmentRoles(unittest.TestCase):
    def test_roles_follow_the_business_type(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "docs", "templates", "security-cctv.json"), encoding="utf-8") as fh:
            c = json.load(fh)
        allowed = {sg["name"]: {r["name"] for r in sg["roles"]} for sg in c["segments"]}
        cards = panel.deal(c, 200, 3)
        for x in cards:
            self.assertIn(x["role"], allowed[x["segment"]])
            self.assertTrue(x["role_cares"])
        self.assertTrue(any(x["role"] == "Society secretary" for x in cards))


class AuditContentSalesKit(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d)

    def run_panel(self, cust, answer):
        cp = os.path.join(self.d, "c.json")
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(cust, fh)
        panel.init(self.d, cp, example("founder-consumer", "pitch.example.md"), n=10, seed=2)
        panel.write_briefs(self.d)
        for i, x in enumerate(panel.load_state(self.d)[1]):
            with open(os.path.join(self.d, "answers", x["id"] + ".json"), "w") as fh:
                json.dump(answer(i, x), fh)
        return panel.tally(self.d)

    def test_audit_score_parts_and_plain_summary(self):
        res = self.run_panel(dict(customer(), price=6.5), lambda i, x: {
            "id": x["id"], "intent": 5 if i < 5 else 2, "buys": i < 5, "reason_code": "price" if i >= 5 else "need",
            "reason": "r", "price_too_cheap": 2, "price_cheap": 4, "price_expensive": 7, "price_too_expensive": 9})
        a = res["audit"]
        self.assertEqual([p["name"] for p in a["parts"]], ["Demand", "Price fit", "Trust"])
        self.assertEqual(sum(p["max"] for p in a["parts"]), 100)
        self.assertEqual(a["score"], sum(p["points"] for p in a["parts"]))
        self.assertTrue(0 <= a["score"] <= 100)
        self.assertTrue(any("realistically buy" in x for x in a["easy"]))
        self.assertIn("Score:", panel.audit_md(res))
        self.assertIn("Sales kit inputs", panel.sales_kit_brief(res))
        self.assertLessEqual(res["realistic_rate"], res["buy_rate"])

    def test_realistic_never_exceeds_raw(self):
        res = self.run_panel(customer(), lambda i, x: {"id": x["id"], "intent": 3, "buys": False, "reason_code": "trust", "reason": "r"})
        self.assertEqual(res["realistic_rate"], 0.0)
        self.assertTrue(any("None of the 10 buyers" in x for x in res["audit"]["easy"]))

    def test_content_mode_brief_metrics_and_score(self):
        c = dict(customer(), test="content", platform="Instagram reel")
        res = self.run_panel(c, lambda i, x: {"id": x["id"], "stops_scrolling": i < 6, "engagement": "save" if i < 3 else "none",
                                                 "clicks": i < 2, "intent": 4 if i < 2 else 2, "buys": i < 2,
                                                 "reason_code": "need", "reason": "r"})
        with open(os.path.join(self.d, "briefs", "P001.md"), encoding="utf-8") as fh:
            b = fh.read()
        self.assertIn("WHAT APPEARS IN YOUR FEED on Instagram reel", b)
        self.assertIn('"stops_scrolling"', b)
        self.assertNotIn("Like any careful shopper", b)
        self.assertAlmostEqual(res["content"]["stop_rate"], 0.6)
        self.assertAlmostEqual(res["content"]["click_rate"], 0.2)
        self.assertEqual(res["content"]["engagement"]["save"], 3)
        self.assertEqual([p["name"] for p in res["audit"]["parts"]], ["Stops the scroll", "Engagement", "Makes them act"])

    def test_bad_content_fields_are_reported(self):
        path = os.path.join(self.d, "x.json")
        with open(path, "w") as fh:
            json.dump({"id": "P001", "buys": False, "reason_code": "need", "reason": "r", "engagement": "dance"}, fh)
        self.assertIn("engagement", panel._answer_ok(path, "P001"))
        with self.assertRaises(panel.PanelError):
            panel.deal(dict(customer(), test="video"))


class WebsiteDataInSync(unittest.TestCase):
    def test_builder_data_matches_the_tool(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "docs", "panel-data.json"), encoding="utf-8") as fh:
            d = json.load(fh)
        self.assertEqual(d["facts"], panel.REGION_FACTS)
        self.assertEqual(d["biases"], panel.BIASES)
        self.assertEqual(d["checks"], panel.PRACTICAL_CHECKS)
        self.assertEqual(d["b2b_checks"], panel.B2B_CHECKS)


class TiersAndAfterPurchase(unittest.TestCase):
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def presets(self):
        with open(os.path.join(self.ROOT, "docs", "presets.json"), encoding="utf-8") as fh:
            return json.load(fh)

    def test_presets_are_sourced_and_deal(self):
        P = self.presets()
        c = customer()
        c["region"] = "IN"
        c["income_is"] = P["india_income_tiers"]["income_is"]
        c["segments"] = P["india_income_tiers"]["segments"]
        c["dimensions"] = [P["india_city_tiers"]["dimension"]]
        self.assertEqual(panel.unsourced(c), [])
        cards = panel.deal(c, 60, 2)
        self.assertEqual(len({x["segment"] for x in cards}), 4)
        x = next(x for x in cards if x["traits"]["city tier"].startswith("Tier 4"))
        self.assertTrue(any("Rural Indians" in f for f in x["trait_facts"]))
        self.assertTrue(all(k.get("source", "").startswith("https://") for key in ("india_city_tiers", "uk_london")
                            for v in P[key]["dimension"]["values"] for k in v["facts"]))

    def test_brief_says_household_and_shows_local_facts(self):
        P = self.presets()
        c = customer()
        c.update({"region": "IN", "income_is": "household", "segments": P["india_income_tiers"]["segments"],
                  "dimensions": [P["india_city_tiers"]["dimension"]]})
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        cp = os.path.join(d, "c.json")
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(c, fh, ensure_ascii=False)
        panel.init(d, cp, example("founder-consumer", "pitch.example.md"), n=8, seed=1)
        panel.write_briefs(d)
        with open(os.path.join(d, "briefs", "P001.md"), encoding="utf-8") as fh:
            b = fh.read()
        self.assertIn("Your household earns about \u20b9", b)
        self.assertIn("About where you live and how people like you spend:", b)
        self.assertIn("if_bought_stars", b)
        res_sources = panel._sources(c)
        self.assertTrue(any("Tier 1" in s_["region"] for s_ in res_sources))

    def test_after_purchase_nps_and_reviews(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        panel.init(d, example("founder-consumer", "customer.example.json"), example("founder-consumer", "pitch.example.md"), n=10, seed=1)
        for i, x in enumerate(panel.load_state(d)[1]):
            a = {"id": x["id"], "intent": 4 if i < 3 else 2, "buys": i < 3, "reason_code": "price", "reason": "r",
                 "if_bought_stars": 5 if i < 4 else 2, "if_bought_review": "great" if i < 4 else "meh",
                 "recommend": 10 if i < 4 else (8 if i < 6 else 3), "after_purchase": "tell friends" if i < 4 else "say nothing"}
            with open(os.path.join(d, "answers", x["id"] + ".json"), "w") as fh:
                json.dump(a, fh)
        res = panel.tally(d)
        af = res["after"]
        self.assertEqual(af["nps"], 0)  # 4 promoters, 2 passives, 4 detractors
        self.assertAlmostEqual(af["avg_stars"], 3.2)
        self.assertEqual(af["actions"]["tell friends"], 4)
        self.assertEqual(af["best_reviews"][0][1], 5)
        self.assertTrue(any("NPS" in x for x in res["audit"]["easy"]))
        bad = os.path.join(d, "answers", "P001.json")
        with open(bad, "w") as fh:
            json.dump({"id": "P001", "buys": False, "reason_code": "price", "reason": "r", "recommend": 11}, fh)
        self.assertIn("recommend", panel._answer_ok(bad, "P001"))


class PresetNamesWorkInTheBuilder(unittest.TestCase):
    def test_no_commas_in_group_value_names(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "docs", "presets.json"), encoding="utf-8") as fh:
            P = json.load(fh)
        for key in ("india_city_tiers", "uk_london"):
            for v in P[key]["dimension"]["values"]:
                self.assertNotIn(",", v["name"], v["name"])  # the builder separates values with commas
