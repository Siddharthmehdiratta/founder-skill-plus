"use client";
import { useState } from "react";
import { ClaudeButton } from "./claude-button";

type V = { idea: string; customer: string; price: string; extra: string };
const advisor = "You are a practical startup advisor for small founders in India and abroad. Plain English, short lines, no hype, never invent numbers.";
const HELPERS: { title: string; text: string; prompt: (v: V) => string }[] = [
  { title: "Sharpen my pitch", text: "Three tighter versions of your pitch for a landing page or WhatsApp.", prompt: (v) => `${advisor}\nRewrite my pitch 3 ways (under 40 words each): one plain, one benefit-first, one for WhatsApp.\nIdea: ${v.idea}\nCustomer: ${v.customer}\nPrice: ${v.price}\nCurrent pitch: """${v.extra}"""` },
  { title: "Answer objections", text: "Short replies to the doubts buyers raise most.", prompt: (v) => `${advisor}\nMy idea: ${v.idea}, for ${v.customer}, at ${v.price}. Write short, honest replies to the 8 objections these buyers are most likely to raise (price, trust, switching, refunds, data, delivery, quality, who we are). One or two lines each.` },
  { title: "Find a price to test", text: "A Van Westendorp-style price test you can run on 20 real people.", prompt: (v) => `${advisor}\nHelp me test the price of: ${v.idea}, for ${v.customer}, currently ${v.price}. Write the 4 Van Westendorp questions in simple words (English and Hinglish), tell me how many people to ask, and how to read the answers.` },
  { title: "Write my landing page", text: "Headline, three benefits, FAQ and a call to action.", prompt: (v) => `${advisor}\nWrite a one-page landing page for: ${v.idea}, for ${v.customer}, at ${v.price}. Give: headline, subheadline, 3 benefits, how it works in 3 steps, 5 FAQ answers, and one call to action. No fake testimonials or numbers.` },
  { title: "Customer interview questions", text: "Ten questions that uncover real demand, not polite yeses.", prompt: (v) => `${advisor}\nGive me 10 customer interview questions (The Mom Test style) to check if ${v.customer} really need: ${v.idea}. Avoid leading questions. Then list 3 answers that would mean "stop" and 3 that would mean "go".` },
  { title: "Scan my competitors", text: "Who else solves this, and how to stand out.", prompt: (v) => `${advisor}\nList the kinds of alternatives ${v.customer} use today instead of: ${v.idea} (including free tools and doing nothing). For each: why people choose it and one way I can be clearly better. Tell me what to check myself, because you may not know current competitors.` },
  { title: "Plan my first 30 days", text: "A week-by-week launch plan to get the first 10 customers.", prompt: (v) => `${advisor}\nPlan my first 30 days to get the first 10 paying customers for: ${v.idea}, for ${v.customer}, at ${v.price}. Week by week, with one channel, daily actions, and what to measure. Keep the budget under ₹10,000.` },
  { title: "Turn reviews into fixes", text: "Paste real reviews; get a ranked improvement list.", prompt: (v) => `${advisor}\nHere are real customer reviews of my product (${v.idea}). Group them into themes, rank the themes by how often they appear and how much they hurt sales, and give one concrete fix for each.\n"""${v.extra || "(paste reviews here)"}"""` },
];

export function ClaudeStudio() {
  const [v, setV] = useState<V>({ idea: "Home-style thalis delivered for lunch", customer: "office workers in Pune", price: "₹149 a meal", extra: "" });
  const f = "h-11 w-full rounded-xl border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-4 focus:ring-primary/10";
  return (
    <div>
      <div className="grid gap-4 rounded-3xl border bg-[#F7FAF9] p-6 sm:grid-cols-3 sm:p-8">
        <label className="grid gap-1.5 text-sm font-medium">Your idea<input className={f} value={v.idea} onChange={(e) => setV({ ...v, idea: e.target.value })} /></label>
        <label className="grid gap-1.5 text-sm font-medium">Who it's for<input className={f} value={v.customer} onChange={(e) => setV({ ...v, customer: e.target.value })} /></label>
        <label className="grid gap-1.5 text-sm font-medium">Price<input className={f} value={v.price} onChange={(e) => setV({ ...v, price: e.target.value })} /></label>
        <label className="grid gap-1.5 text-sm font-medium sm:col-span-3">Your pitch or customer reviews (optional)<textarea rows={3} className="w-full rounded-xl border bg-background p-3 text-sm outline-none focus:border-primary focus:ring-4 focus:ring-primary/10" value={v.extra} onChange={(e) => setV({ ...v, extra: e.target.value })} /></label>
      </div>
      <div className="mt-8 grid gap-4 md:grid-cols-2">
        {HELPERS.map((h) => (
          <div key={h.title} className="flex flex-col rounded-3xl border p-6">
            <h3 className="text-lg font-semibold tracking-tight">{h.title}</h3>
            <p className="mt-1 mb-5 text-sm text-muted-foreground">{h.text}</p>
            <ClaudeButton className="mt-auto" label="Open in Claude" prompt={h.prompt(v)} />
          </div>
        ))}
      </div>
    </div>
  );
}
