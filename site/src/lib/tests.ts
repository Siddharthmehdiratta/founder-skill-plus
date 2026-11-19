/* Assumption tests. The Idea Checker gives a score. A score does not tell you what to do on Monday.
   This turns the weakest answers into tests you can run in a week: one assumption each, a pass number set
   before you start, and a cost in money and days. Riskiest first, because the riskiest assumption is the one
   that kills the idea, and finding that out in week one is cheaper than finding it out in month six. */
import { IDEA_QS, type IdeaAnswers } from "./idea.ts";

export const TEST_KEY = "fp-tests";
export type Outcome = "pass" | "fail" | "unclear";
export type Result = { id: string; outcome: Outcome; note: string };
export type Test = {
  id: string;
  assume: string;   // the thing you are taking on faith
  how: string;      // the cheapest way to find out this week
  pass: string;     // what counts as a pass, decided before you start
  fail: string;     // what counts as a fail
  cost: string;     // money and days
  risk: number;     // 3 = you have no evidence at all
};

/* One test per question. The wording changes with how the founder answered: somebody who has already
   taken money is tested differently from somebody who has not. */
const BUILD: Record<string, (score: number) => Omit<Test, "id" | "risk">> = {
  who: () => ({
    assume: "You can name the customer precisely enough to find a hundred of them.",
    how: "Write the list. Real names or real handles, from one place they already gather. Stop at a hundred or when you run dry.",
    pass: "You reach 100 names in under two hours.",
    fail: "You run dry under 40. The group is a description, not a market yet. Narrow it and try again.",
    cost: "Free. Half a day.",
  }),
  pain: () => ({
    assume: "The problem happens often enough that they want it gone.",
    how: "Ask 10 of them one question: when did this last happen to you? Say nothing about your idea.",
    pass: "7 or more say within the last week, unprompted.",
    fail: "Most have to think about it, or answer with a month. A rare annoyance is a hard sell.",
    cost: "Free. Two days of messages.",
  }),
  source: () => ({
    assume: "The problem is theirs, not one you imagined for them.",
    how: "Watch 3 of them do the task today, without helping. Write down each step and each complaint.",
    pass: "All 3 complain about the same step without you naming it.",
    fail: "They complain about different things, or nothing. You have three problems, not one.",
    cost: "Free. Three calls.",
  }),
  now: () => ({
    assume: "What they use today is bad enough to leave.",
    how: "Ask the same 10 what they use now and what it costs them in time or money each week.",
    pass: "Most name a workaround and a cost they can put a number on.",
    fail: "Most name a product they are happy with. You are not selling a fix, you are selling a switch.",
    cost: "Free. Part of the same calls.",
  }),
  pay: (s) => s >= 2
    ? { assume: "The people who paid were not friends doing you a favour.",
        how: "Take money from 3 strangers who have never spoken to you before.",
        pass: "3 strangers pay full price.",
        fail: "Only people who know you pay. That is support, not a market.",
        cost: "The price of a landing page. One week." }
    : { assume: "Somebody will actually pay, not just say they would.",
        how: "One page: what it is, the price, a Pay button that works. Send it to 50 of your list. Do not build the product.",
        pass: "3 or more pay, or pre-pay. Refund anyone you cannot deliver to.",
        fail: "Nobody pays. The gap between yes and paying is where most ideas die, and you found it in a week.",
        cost: "Under ₹1,000. One week." },
  reach: () => ({
    assume: "You can put this in front of a hundred of the right people without paying for ads.",
    how: "Post or message in the one place they gather. Count how many of the right people see it.",
    pass: "100 of the right people see it inside a week, for free.",
    fail: "You cannot get past 20 without spending. Work out the cost per customer before you build anything.",
    cost: "Free. One week.",
  }),
  trust: () => ({
    assume: "A stranger will hand money to a name they have never heard of.",
    how: "Run the same offer twice to similar groups: once bare, once with one piece of proof, such as a money-back line or a named first customer.",
    pass: "The version with proof gets clearly more replies.",
    fail: "No difference. Trust is not what is stopping them, so stop working on it and find what is.",
    cost: "Free. Two weeks.",
  }),
  margin: () => ({
    assume: "There is money left after every cost.",
    how: "Deliver it once, by hand, to one paying customer. Write down every rupee and every hour it took.",
    pass: "You keep money, and the hours would not break you at ten customers a week.",
    fail: "You lose money, or it only works because you did not pay yourself. Raise the price or change what you sell.",
    cost: "One real delivery. A few days.",
  }),
  repeat: () => ({
    assume: "A customer comes back without being chased.",
    how: "Serve 5 customers. Do nothing after. Wait the length of their natural cycle.",
    pass: "2 or more come back on their own.",
    fail: "None return unprompted. You are paying to win every sale, so the price has to carry that.",
    cost: "Free. One cycle.",
  }),
  speed: () => ({
    assume: "You can put something usable in front of someone quickly.",
    how: "Give yourself two weeks and one feature. Do the rest by hand behind the scenes.",
    pass: "Somebody uses it and gets the result, even if you are doing half of it manually.",
    fail: "Two weeks pass with nothing to show. Cut the scope again, not the deadline.",
    cost: "Two weeks of your time.",
  }),
};

/* Riskiest first. A question answered "I'm not sure" scores 0 and is the most urgent thing to find out. */
export function planTests(a: IdeaAnswers): Test[] {
  return IDEA_QS
    .map((q) => {
      const v = a[q.id];
      const score = typeof v === "number" ? v : 0;      // an answer in their own words is unverified, so treat it as unknown
      const risk = 3 - score;
      return { id: q.id, risk, ...BUILD[q.id](score) };
    })
    .filter((t) => t.risk >= 1)                          // a 3 out of 3 answer needs no test
    .sort((a, b) => b.risk - a.risk);
}

/* What to do next, given what has come back so far. One test at a time: starting five at once is how you end up
   unable to say which one moved. */
export function nextStep(tests: Test[], results: Record<string, Result>) {
  const open = tests.filter((t) => !results[t.id]);
  const failed = tests.filter((t) => results[t.id]?.outcome === "fail");
  const unclear = tests.filter((t) => results[t.id]?.outcome === "unclear");
  if (failed.length)
    return { kind: "stop" as const, test: failed[0],
      line: `“${failed[0].assume}” did not hold. Fix that before you run another test or write another line of code. Everything downstream assumed it was true.` };
  if (unclear.length)
    return { kind: "redo" as const, test: unclear[0],
      line: `“${unclear[0].assume}” came back unclear. An unclear result is not a pass. Run it again with more people, or with a sharper pass number.` };
  if (open.length)
    return { kind: "run" as const, test: open[0],
      line: `Run this one next. It is the thing you have least evidence for, so it is the cheapest place to be wrong.` };
  return { kind: "done" as const, test: null,
    line: "Every assumption on the list has held. That is not proof the business works, it is proof nothing obvious kills it. Build the smallest version and sell it." };
}

export function loadResults(): Record<string, Result> {
  try { return JSON.parse(localStorage.getItem(TEST_KEY) || "{}") || {}; } catch { return {}; }
}
export function saveResults(r: Record<string, Result>) {
  try { localStorage.setItem(TEST_KEY, JSON.stringify(r)); } catch { /* private browsing */ }
}
