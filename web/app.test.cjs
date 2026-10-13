const test = require("node:test");
const assert = require("node:assert/strict");
const { evaluateDemo } = require("./app.js");

function sample(overrides = {}) {
  return { task_id: "TEST-1", target_identifier: "SPECIMEN-1",
    primary_metric: 10, secondary_metric: 3, status_descriptor: "NOMINAL",
    is_critical_flag: false, ...overrides };
}

test("routine sample has no alerts", () => {
  const result = evaluateDemo(sample());
  assert.equal(result.overall_urgency, "ROUTINE");
  assert.equal(result.total_alerts, 0);
});

test("exact thresholds are not exceeded", () => {
  assert.equal(evaluateDemo(sample({primary_metric: 25, secondary_metric: 12})).total_alerts, 0);
});

test("multiple warnings elevate status", () => {
  const result = evaluateDemo(sample({
    primary_metric: 25.1, secondary_metric: 12.1, status_descriptor: "DISCORDANT"
  }));
  assert.equal(result.total_alerts, 3);
  assert.equal(result.overall_urgency, "ELEVATED_RISK");
});

test("explicit critical flag triggers critical urgency", () => {
  assert.equal(evaluateDemo(sample({is_critical_flag: true})).overall_urgency, "CRITICAL_STAT_PANIC");
});

test("validation rejects missing/invalid numbers and non-synthetic IDs", () => {
  assert.throws(() => evaluateDemo(sample({primary_metric: ""})));
  assert.throws(() => evaluateDemo(sample({secondary_metric: "Infinity"})));
  assert.throws(() => evaluateDemo(sample({task_id: "john@example.org"})));
  assert.throws(() => evaluateDemo(sample({is_critical_flag: "false"})));
});
