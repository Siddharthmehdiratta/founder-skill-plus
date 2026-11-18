import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest

from _load import load

fb = load("founder-product", "feedback")


class Feedback(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d)

    def write(self, name, text):
        p = os.path.join(self.d, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        return p

    def test_load_csv_txt_and_panel_with_dedupe(self):
        csvp = self.write("r.csv", "Review,Stars,Platform\nDelivery was late again,2,Google\nLoved the food,5,Google\nDelivery was late again,2,Google\n")
        txtp = self.write("w.txt", "Too expensive for daily lunch\n\nPortions are small\nreally small")
        panelp = self.write("results.json", json.dumps({"buyers": [{"id": "P001", "reason": "Not sure it is fresh",
                                                                    "questions_before_buying": [{"question": "Is it veg?", "topic": "other"}]}]}))
        added, total = fb.load(self.d, [csvp, txtp, panelp])
        self.assertEqual(total, 5)
        with open(os.path.join(self.d, "items.json"), encoding="utf-8") as fh:
            items = json.load(fh)
        self.assertEqual(items[0]["rating"], 2.0)
        self.assertEqual(items[0]["source"], "Google")
        self.assertIn("Portions are small\nreally small", [i["text"] for i in items])
        self.assertIn("simulated", items[-1]["source"])
        self.assertEqual([i["id"] for i in items], ["F001", "F002", "F003", "F004", "F005"])

    def test_csv_without_text_column_is_refused(self):
        p = self.write("bad.csv", "name,stars\nA,5\n")
        with self.assertRaises(fb.FeedbackError):
            fb.load(self.d, [p])

    def tagged(self):
        p = self.write("f.txt", "\n".join(["late delivery %d" % i for i in range(6)] + ["great taste %d" % i for i in range(3)] + ["please add a veg option"]))
        fb.load(self.d, [p])
        fb.brief(self.d)
        tags = {}
        for i in range(1, 11):
            pid = "F%03d" % i
            if i <= 6:
                tags[pid] = {"themes": ["Late delivery"], "sentiment": "negative", "type": "complaint", "severity": 3, "effort": 1, "quote": "late"}
            elif i <= 9:
                tags[pid] = {"themes": ["Taste"], "sentiment": "positive", "type": "praise", "severity": 1, "effort": 0, "quote": "great"}
            else:
                tags[pid] = {"themes": ["Veg option"], "sentiment": "neutral", "type": "feature_request", "severity": 2, "effort": 2, "quote": "veg"}
        with open(os.path.join(self.d, "tags.json"), "w") as fh:
            json.dump(tags, fh)

    def test_brief_check_and_report_numbers(self):
        self.tagged()
        with open(os.path.join(self.d, "tag-brief.md"), encoding="utf-8") as fh:
            self.assertIn("F010", fh.read())
        self.assertEqual(fb.check(self.d), [])
        res = fb.report(self.d)
        self.assertEqual(res["tagged"], 10)
        self.assertEqual(res["sentiment"], {"positive": 3, "neutral": 1, "negative": 6})
        self.assertEqual(res["health"], 35)  # 50 + 50 x (3 - 6) / 10
        top = res["fix_first"][0]
        self.assertEqual(top["theme"], "Late delivery")
        self.assertAlmostEqual(top["priority"], 0.6 * 3 * 1.0 / 1 * 100)
        self.assertEqual(top["lane"], "Now")
        self.assertEqual(res["keep"][0]["theme"], "Taste")
        self.assertEqual(res["requests"][0]["theme"], "Veg option")
        self.assertIn("Fix first: Late delivery", " ".join(res["plain"]))
        md = fb.report_md(res)
        self.assertIn("| 1 | Late delivery |", md)
        html = fb.report_html(res)
        self.assertEqual(html.count("</script>"), 1)

    def test_check_finds_bad_tags(self):
        self.tagged()
        with open(os.path.join(self.d, "tags.json")) as fh:
            tags = json.load(fh)
        tags["F001"]["sentiment"] = "angry"
        tags["F002"]["severity"] = True
        del tags["F003"]
        with open(os.path.join(self.d, "tags.json"), "w") as fh:
            json.dump(tags, fh)
        probs = dict(fb.check(self.d))
        self.assertIn("sentiment", probs["F001"])
        self.assertIn("severity", probs["F002"])
        self.assertEqual(probs["F003"], "not tagged")

    def test_cli_and_friendly_error(self):
        out = io.StringIO()
        with contextlib.redirect_stderr(out):
            self.assertEqual(fb.main(["--dir", self.d, "brief"]), 2)
        self.assertIn("run feedback.py load", out.getvalue())
        self.tagged()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(fb.main(["--dir", self.d, "report"]), 0)
        for f in ("feedback-report.md", "feedback-report.json", "feedback-report.html"):
            self.assertTrue(os.path.exists(os.path.join(self.d, f)))


class Mixed(unittest.TestCase):
    def test_quotes_match_the_mood_and_ties_are_problems(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        p = os.path.join(d, "f.txt")
        with open(p, "w") as fh:
            fh.write("tasty but late\nso tasty\nloved the taste\nroti was cold\nfood was fresh")
        fb.load(d, [p])
        tags = {"F001": {"themes": ["taste", "late"], "sentiment": "negative", "type": "complaint", "severity": 2, "effort": 2, "quote": "late"},
                "F002": {"themes": ["taste"], "sentiment": "positive", "type": "praise", "severity": 1, "effort": 0, "quote": "so tasty"},
                "F003": {"themes": ["taste"], "sentiment": "positive", "type": "praise", "severity": 1, "effort": 0, "quote": "loved the taste"},
                "F004": {"themes": ["quality"], "sentiment": "negative", "type": "complaint", "severity": 3, "effort": 1, "quote": "roti was cold"},
                "F005": {"themes": ["quality"], "sentiment": "positive", "type": "praise", "severity": 1, "effort": 0, "quote": "fresh"}}
        with open(os.path.join(d, "tags.json"), "w") as fh:
            json.dump(tags, fh)
        res = fb.report(d)
        keep = {r["theme"]: r for r in res["keep"]}
        self.assertEqual(keep["taste"]["quotes"], ["so tasty", "loved the taste"])
        probs = {r["theme"]: r for r in res["fix_first"]}
        self.assertIn("quality", probs)          # a 1-1 tie is treated as a problem to fix
        self.assertEqual(probs["quality"]["quotes"], ["roti was cold"])
        self.assertNotIn("quality", keep)


class PraiseInMixedItems(unittest.TestCase):
    def test_praise_part_of_a_mixed_item_counts_as_praise(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        p = os.path.join(d, "f.txt")
        with open(p, "w") as fh:
            fh.write("tasty but late\nlate again\nso tasty")
        fb.load(d, [p])
        tags = {"F001": {"themes": ["late delivery"], "sentiment": "negative", "type": "complaint", "severity": 2, "effort": 2,
                         "quote": "late", "praise_themes": ["taste"], "praise_quote": "tasty"},
                "F002": {"themes": ["late delivery"], "sentiment": "negative", "type": "complaint", "severity": 3, "effort": 2, "quote": "late again"},
                "F003": {"themes": ["taste"], "sentiment": "positive", "type": "praise", "severity": 1, "effort": 0, "quote": "so tasty"}}
        with open(os.path.join(d, "tags.json"), "w") as fh:
            json.dump(tags, fh)
        self.assertEqual(fb.check(d), [])
        res = fb.report(d)
        taste = next(r for r in res["themes"] if r["theme"] == "taste")
        self.assertEqual((taste["positive"], taste["negative"]), (2, 0))
        self.assertEqual([r["theme"] for r in res["keep"]], ["taste"])
        self.assertEqual([r["theme"] for r in res["fix_first"]], ["late delivery"])
        self.assertEqual(taste["quotes"], ["tasty", "so tasty"])
