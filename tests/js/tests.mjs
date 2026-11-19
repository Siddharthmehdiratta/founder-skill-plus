// Assumption tests: run with `node tests/js/tests.mjs`
import assert from "node:assert/strict";
import { planTests, nextStep } from "../../site/src/lib/tests.ts";
import { IDEA_QS } from "../../site/src/lib/idea.ts";

// every question can produce a test, and every test is complete
const all = planTests(Object.fromEntries(IDEA_QS.map((q) => [q.id, 0])));
assert.equal(all.length, IDEA_QS.length);
assert.ok(all.every((t) => t.assume && t.how && t.pass && t.fail && t.cost), "every test states the pass and the fail up front");
assert.ok(all.every((t) => t.risk === 3));

// a question answered at full confidence needs no test
const sure = planTests(Object.fromEntries(IDEA_QS.map((q) => [q.id, 3])));
assert.equal(sure.length, 0);

// riskiest first
const mixed = planTests({ who: 3, pain: 1, source: 2, now: 0, pay: 2, reach: 0, trust: 3, margin: 1, repeat: 2, speed: 3 });
assert.deepEqual(mixed.slice(0, 2).map((t) => t.id).sort(), ["now", "reach"], "the two unknowns come first");
assert.ok(!mixed.some((t) => ["who", "trust", "speed"].includes(t.id)));
assert.ok(mixed.every((t, i, xs) => i === 0 || xs[i - 1].risk >= t.risk), "sorted by risk");

// an answer in the founder's own words is unverified, so it is treated as unknown rather than as a pass
const own = planTests({ ...Object.fromEntries(IDEA_QS.map((q) => [q.id, 3])), pay: "other" });
assert.equal(own.length, 1); assert.equal(own[0].id, "pay"); assert.equal(own[0].risk, 3);

// the pay test changes with the evidence the founder already has
assert.match(planTests({ pay: 0 }).find((t) => t.id === "pay").how, /Do not build the product/);
assert.match(planTests({ pay: 2 }).find((t) => t.id === "pay").how, /strangers/);

// next step: one at a time, and a failure outranks everything else
const t = planTests({ who: 0, pain: 0, pay: 0 });
assert.equal(nextStep(t, {}).kind, "run");
assert.equal(nextStep(t, {}).test.id, t[0].id, "the first open test is the next step, not all of them");
assert.equal(nextStep(t, { [t[0].id]: { id: t[0].id, outcome: "pass", note: "" } }).test.id, t[1].id);
assert.equal(nextStep(t, { [t[1].id]: { id: t[1].id, outcome: "fail", note: "" } }).kind, "stop");
// unclear is never treated as a pass
const un = nextStep(t, Object.fromEntries(t.map((x) => [x.id, { id: x.id, outcome: "unclear", note: "" }])));
assert.equal(un.kind, "redo");
assert.match(un.line, /not a pass/);
// all passed
assert.equal(nextStep(t, Object.fromEntries(t.map((x) => [x.id, { id: x.id, outcome: "pass", note: "" }]))).kind, "done");

console.log("tests.mjs ok");
