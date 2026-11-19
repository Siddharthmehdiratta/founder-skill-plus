// Idea Checker scoring: run with `node tests/js/idea.mjs`
import assert from "node:assert/strict";
import { IDEA_QS, scoreIdea } from "../../site/src/lib/idea.ts";
assert.equal(IDEA_QS.length, 10);
for (const q of IDEA_QS) { assert.equal(q.opts.length, 4, q.id); assert.ok(q.opts.some(([, v]) => v === 3), q.id); assert.ok(q.weak && q.why); }
assert.equal(scoreIdea({}).score, null);
const all = (v) => Object.fromEntries(IDEA_QS.map((q) => [q.id, v]));
assert.equal(scoreIdea(all(3)).score, 100); assert.equal(scoreIdea(all(3)).label, "Strong start"); assert.equal(scoreIdea(all(0)).score, 0); assert.equal(scoreIdea(all(0)).weak.length, 10);
let r = scoreIdea({ who: 3, pain: 0 }); assert.equal(r.score, 50); assert.equal(r.weak.length, 1); assert.equal(r.label, "Promising, test the gaps");
r = scoreIdea({ who: 3, pain: "other", pay: "other" }); assert.equal(r.score, 100, "own-word answers are not scored"); assert.equal(r.own.length, 2); assert.equal(r.answered, 3); assert.equal(r.scored, 1);
r = scoreIdea(all("other")); assert.equal(r.score, null); assert.equal(r.answered, 10);
console.log("all Idea Checker checks passed");
