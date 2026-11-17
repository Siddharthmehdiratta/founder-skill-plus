---
name: founder-consumer
description: >-
  The consumer panel. Spins up a swarm of buyer sub-agents (default 100, --quick
  for 20) trained on the user's target customer, each with a different income,
  age, buying behaviour and objection, shows every one the same pitch, and runs
  the business through 100 buyer scenarios to see who buys, who doesn't, and why.
  Tallies the answers into buy rates by segment, the reasons people pass in their
  own words, what would flip a no, and price answers for founder-pricing. Use when
  the user says "would people buy this", "test it on customers", "run the
  consumer panel", "simulate buyers", "who is my customer", or "validate demand".
argument-hint: "[--size small|medium|large | --n 100 | --quick] [--only \"Category A,Category B\"] [--seed S]"
---

# founder-consumer

The craziest part of the pack. Instead of guessing whether people will buy, you
ask a hundred of them, each one a sub-agent playing a specific buyer drawn from
your target customer. You are the moderator. You never answer for a buyer.

What the user typed after `/founder-consumer`: `$ARGUMENTS`

## The tool

All bookkeeping goes through `panel.py` in this skill's folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/panel.py" <command>
```

Below, `PANEL` means exactly that. If the path is not expanded, use the base
directory Claude Code printed for this skill. State lives in `founder/panel/`.

## Step 1: the target customer

Write `founder/customer.json` (shape: `customer.example.json` in this folder):

- `business`, and `target`: who the customer is, in one specific line.
- `segments`: 2 to 4 groups with a `share` and an `income` range [low, high].
- `behaviours`: 4 to 8 buying behaviours with a `share` and a `how` line
  (daily regular, deal hunter, reads every review, loyal to a competitor...).
- `objections`: the 4 to 8 doubts this kind of buyer really has.
- `habits` (optional): everyday context lines that make a buyer concrete.

Ground it in something real. Use what the user knows about their customers, and
if `/founder-competitors` ran, the complaints in `founder/competitors.md`. If the
user has real customer data (interviews, reviews, survey answers), prefer it to
your guesses and say which parts are guesses. Show the user the profile in a few
lines and let them correct it before you deal: a wrong customer makes the whole
panel wrong.

### Plus fields (founder-skill-plus)

- Categories with exact headcounts: give every segment a `count` instead of a
  `share`, e.g. Category A 50, Category B 30, Category C 20. The panel is then
  exactly that big (the counts win over `--n` and `--size`), and results come
  out category by category. `--only` picks which categories to run.
- `region`: one of `IN US UK EU CN JP AE SG AU BR`. Sets the currency, number
  format (India uses lakhs: ₹13,21,000) and local first names matched to gender.
  `"locale": "IN"` still works. Your own `currency` or `names` override it.
- `languages`: a mix, e.g. `[{"name": "English", "share": 0.4}, {"name":
  "Hinglish", "share": 0.6}]`. Each buyer gets one; overrides `language`.
- `language`: e.g. `"Hindi"`, `"Mandarin Chinese"`, `"Spanish"`. Buyers answer in
  it, the way they would really talk, plus an English translation of the reason.
- `genders`: `[{"name": "female", "share": 0.5}, ...]`. Names match the gender.
- `age_groups`: `[{"name": "18-24", "range": [18, 24], "share": 0.3}, ...]`.
  Replaces `age`. Cover every age group that buys, with real shares.
- `dimensions`: any other split you have data for, e.g. diet, city tier,
  religion, ethnicity, car owned: `[{"name": "diet", "values": [{"name":
  "vegetarian", "share": 0.4}, ...]}]`. Only use splits with real shares. Every
  buyer is told to act as one person, never as a stereotype of a group.
- `price`: the price in the pitch. Adds a money line: first-month revenue per 100
  people reached.
- `currency`: the symbol buyers see, e.g. `"₹"`. Incomes are in that currency.
- `where`: the city or area; every buyer is told they live there.
- `skeptic_share` (default 0.2): the share of buyers who get NO planted doubt.
  They react on their own, so the panel can surface doubts you did not list.
- `intent_weights`: how much of each stated intent (5 definitely ... 1 definitely
  not) turns into a real sale. Defaults 0.75 / 0.25 / 0.10 / 0 / 0 are a common
  starting rule, not a fact. Replace them once you have real sales to compare.

See `customer.india.example.json` with `pitch.india.example.md` (India,
Hinglish answers) and
`customer.world.example.json` (United States, genders, age groups, dimensions).

## Step 1b: real market facts and reviews (recommended)

Buyers react better when they know what real shoppers in that market know. Add
a `market` block to `customer.json`:

- `facts`: up to 8 short, current facts about how people in this market buy
  this kind of product (how they pay, where they hear about it, what they
  compare against, recent trends). Every buyer sees all of them.
- `reviews`: 5 to 15 real reviews of competitors or substitutes, each with
  `about`, `stars` and `text` (keep each under about 25 words; trim or
  paraphrase longer ones). Each buyer reads 0 to 2 of them; careful shoppers
  (behaviours that mention reviews, research or comparing) read 3. The results
  show whether reading reviews changed who buys.

Rules: research it now, with links. Use `/founder-competitors` output and web
search. Every fact and review needs a `source` link; `init` warns about any
without one. Never invent a fact, a statistic or a review: buyers are told these
are real. Do not hard-code how a nationality "thinks": describe the market (how
people pay, shop and compare), not a stereotype of the people.

Use `languages` (a mix with shares) instead of one `language` when buyers in the
market speak different languages, e.g. English, Hinglish and Hindi in India.

## Step 2: the pitch

Write `founder/pitch.md`: what a buyer would actually see. The product, the price,
where and how to get it, any opening offer. Three to six plain lines, no
superlatives, nothing the business cannot deliver. Every buyer sees exactly this.

## Step 3: deal and run

```bash
PANEL init --customer founder/customer.json --pitch founder/pitch.md --n 100
# pick the size: --size small (20) | medium (100) | large (250), or any --n
PANEL init --customer founder/customer.json --pitch founder/pitch.md --size small
# run only some categories:
PANEL init --customer founder/customer.json --pitch founder/pitch.md --only "Category A,Category B"
PANEL prompts
```

`init` deals the persona cards (same seed, same cards; the seed is recorded).
`prompts` writes one brief per buyer and lists them in waves of 10. For each wave,
send ONE message with one Agent tool call per buyer in that wave (the Agent tool
is called Task in older Claude Code versions):

- `subagent_type`: `general-purpose`
- `description`: `panel <id>`
- `prompt`: `Read <brief path> and follow it exactly. It is your whole brief.`

Wait for the whole wave before the next one. Claude Code runs about 10 tool calls
at once by default, so 100 buyers is 10 waves. After the last wave:

```bash
PANEL check      # lists missing or broken answers
PANEL prompts    # rewrites briefs for those only; run them once more
PANEL tally
```

If a buyer printed its JSON in its reply instead of writing the file (it happens),
file its own reply with `PANEL save <id>` and the reply on stdin; `save` refuses
anything that is not a valid answer. A buyer that fails twice is left out and
counted in the results. Never write an answer for a buyer yourself.

Before a 100-buyer run, tell the user it is 100 sub-agent calls and suggest
`--quick` (20 buyers) for a first look. Sub-agents write one file each into
`founder/panel/answers/`; in the default permission mode that is one approval per
file, so suggest accept-edits mode (Shift+Tab) for the run.

## Step 3b (optional): A/B test two pitches

The most reliable use of a simulated panel is comparing, not forecasting. Deal
pitch B to the SAME buyers (same seed and size) in a second folder:

```bash
PANEL --dir founder/panel-b init --customer founder/customer.json --pitch founder/pitch-b.md --n 100 --seed <seed of A>
# run the waves exactly as above, with --dir founder/panel-b on every command
PANEL compare founder/panel founder/panel-b
```

`compare` shows the buy rate and realistic estimate for each pitch, the change by
segment, and which buyers switched and why. Under about 10 points on 100 buyers
can be noise.

## Step 4: read it to the user

`PANEL tally` writes `founder/panel/results.md`, `results.json` and
`results.html` (a visual one-page report with a bar per group; open it in a
browser). Give the user:

1. The headline: "40 buy · 60 pass", the buy rate with its 90% range, and the
   realistic estimate (weighted intent). Lead with the realistic estimate.
2. Who buys and who doesn't: the rows that differ most across segment,
   behaviour, income, gender, age group and any dimension. Give the money line.
3. Why they pass: the top three reasons with one quote each, as written.
4. What would flip a no: the most repeated answers.
4b. Doubts nobody planted: the repeat ones go into `customer.json` objections
    for the next run.
5. One sentence on what to change before spending money, and which skill does it
   (pricing, offer, marketing).

## Honest limits, say them once

These are simulated buyers. They are good at surfacing objections, segments and
wording you had not thought of, and bad at predicting real conversion: language
models lean agreeable, so treat the buy rate as an upper bound. Confirm the big
calls with real people (a waitlist, a pre-sale, a landing page with a price)
before signing anything. Do not present panel quotes as customer testimonials.

## The brief every buyer gets

`panel.py` fills the card into a fixed template (see `BRIEF` in the script): who
the buyer is (name, age, gender and age group if set, segment, income, buying
behaviour, a habit, any dimensions, and the doubt that comes to mind, or none for
open buyers), the pitch word for word, an instruction not to be agreeable, not to
invent facts and not to act as a stereotype, the answer language if set, and the
exact JSON to write: intent 1 to 5, buys (true only for 4 or 5), purchases in the
first month, a reason code, the reason in their own voice (plus `reason_en` in
English when the language is not English), their main objection, a doubt nobody
mentioned (`unprompted_doubt`), what would change their mind, and four price
answers (too cheap, a bargain, getting expensive, too expensive). Never edit a
brief for one buyer.

## Output

`founder/customer.json`, `founder/pitch.md`, `founder/panel/` (cards, briefs,
answers, results). Next: `/founder-pricing` reads the price answers,
`/founder-offer` and `/founder-marketing` read the objections.
