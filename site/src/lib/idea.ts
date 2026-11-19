/* Idea Checker: ten questions founders skip. It scores the answers picked from the list.
   An answer written in the founder's own words cannot be scored fairly, so it is left out of the score and passed to Claude instead. */
export type IdeaQ = { id: string; q: string; opts: [string, number][]; weak: string; why: string };
export const IDEA_QS: IdeaQ[] = [
  { id: "who", q: "Who exactly is the customer?", opts: [["A group I can name and find", 3], ["A broad group, like students", 1], ["Everyone", 0], ["I'm not sure", 0]], weak: "Pick one narrow group you could meet this week, such as hostel students in Pune. Sell to them first.", why: "A named group is easier to reach, and their words go straight into your pitch." },
  { id: "pain", q: "How often do they feel the problem?", opts: [["Every day", 3], ["Every week", 2], ["Now and then", 1], ["I'm not sure", 0]], weak: "Talk to 5 target customers this week. Ask when they last had the problem.", why: "Frequent problems are easier to sell solutions for." },
  { id: "source", q: "How did you find this problem?", opts: [["Customers asked me for it", 3], ["I have it myself", 2], ["I watched others struggle", 2], ["It's a guess", 0]], weak: "Find 3 people who have the problem and watch how they deal with it today.", why: "A problem people bring to you is stronger evidence than one you imagine for them." },
  { id: "now", q: "What do they use today?", opts: [["A messy workaround", 3], ["Nothing, they put up with it", 2], ["A free tool", 1], ["A paid product they like", 0]], weak: "Name one thing you do clearly better than the free or paid option, and lead with it.", why: "A messy workaround shows demand. A good free option is the hardest rival." },
  { id: "pay", q: "Has anyone paid or pre-paid yet?", opts: [["Yes, several", 3], ["One or two", 2], ["They said they would", 1], ["Not yet", 0]], weak: "Put a price on a page, or take a small pre-order, before you build more.", why: "Saying yes is free. Paying is the real signal." },
  { id: "reach", q: "Can you reach 100 target customers this month?", opts: [["Yes, I know where they are", 3], ["Probably, through ads", 1], ["Through friends only", 1], ["I don't know how", 0]], weak: "Pick one channel, such as a community, a group or a marketplace, and list 100 names there.", why: "An idea you cannot put in front of people cannot be tested." },
  { id: "trust", q: "Why would a stranger trust you?", opts: [["Reviews or proof already", 3], ["A known name or partner", 2], ["A guarantee or free trial", 2], ["Nothing yet", 0]], weak: "Add one piece of proof: a guarantee, a free first try, or a named early customer.", why: "Trust is one of the three parts of the Founder Plus score." },
  { id: "margin", q: "After costs, do you keep money on each sale?", opts: [["Yes, most of the price", 3], ["Some", 2], ["Very little", 1], ["I haven't worked it out", 0]], weak: "Write down every cost per sale. If the margin is thin, test a higher price on the AI panel.", why: "Growth on a thin margin burns cash faster." },
  { id: "repeat", q: "Will a customer buy again?", opts: [["Yes, regularly", 3], ["Sometimes", 2], ["Once only", 1], ["I'm not sure", 0]], weak: "Look for a reason to return: a refill, a subscription, or a second product.", why: "Repeat buyers cost nothing to win a second time." },
  { id: "speed", q: "How soon can you show a first version?", opts: [["I already have one", 3], ["Under a month", 2], ["1 to 3 months", 1], ["Longer, or not sure", 0]], weak: "Cut the first version down to one feature you can show in two weeks.", why: "The sooner people can try it, the sooner you learn." },
];
export type IdeaAnswers = Record<string, number | "other">;

export function scoreIdea(a: IdeaAnswers) {
  const picked = IDEA_QS.filter((q) => typeof a[q.id] === "number");
  const own = IDEA_QS.filter((q) => a[q.id] === "other");
  const score = picked.length ? Math.round((picked.reduce((s, q) => s + (a[q.id] as number), 0) / (picked.length * 3)) * 100) : null;
  const weak = picked.filter((q) => (a[q.id] as number) <= 1);
  const label = score === null ? "Answer the questions" : score >= 75 ? "Strong start" : score >= 50 ? "Promising, test the gaps" : "Early: test before you spend";
  return { score, label, weak, own, answered: picked.length + own.length, scored: picked.length };
}
