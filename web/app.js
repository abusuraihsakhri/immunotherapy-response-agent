"use strict";

// Synthetic, deterministic demonstration of the repository's agents/workers.py.
// This is not a clinically validated response predictor or an HMAC audit service.
(function () {
  const STATUS_WORDS = ["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"];

  function evaluateDemo(payload) {
    if (!payload || typeof payload !== "object") throw new Error("An input object is required.");
    const task = String(payload.task_id || "");
    const target = String(payload.target_identifier || "");
    if (!/^[A-Za-z0-9_-]{1,128}$/.test(task) || !/^[A-Za-z0-9_-]{1,128}$/.test(target)) {
      throw new Error("Use short synthetic IDs containing only letters, digits, _ or -.");
    }
    const primary = Number(payload.primary_metric);
    const secondary = Number(payload.secondary_metric);
    if (payload.primary_metric === "" || payload.secondary_metric === "" ||
        !Number.isFinite(primary) || !Number.isFinite(secondary)) {
      throw new Error("Metrics must be finite numbers.");
    }
    if (typeof payload.is_critical_flag !== "boolean") {
      throw new Error("Critical flag must be a boolean.");
    }
    const status = String(payload.status_descriptor || "NOMINAL").toUpperCase();
    if (status.length > 256) throw new Error("Status descriptor is too long.");
    const alerts = [];
    if (primary > 25) {
      alerts.push({ worker: "InvariantQCWorker", urgency: "ELEVATED_RISK",
        summary: "Primary metric exceeds demo threshold (>25)." });
    }
    if (payload.is_critical_flag || secondary > 12) {
      alerts.push({ worker: "SafetyEscalationWorker",
        urgency: payload.is_critical_flag ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
        summary: "Synthetic critical flag is set or secondary metric exceeds demo threshold (>12)." });
    }
    if (STATUS_WORDS.some(word => status.includes(word))) {
      alerts.push({ worker: "ProtocolConformanceWorker", urgency: "ELEVATED_RISK",
        summary: "Status contains a configured demonstration flag word." });
    }
    const critical = alerts.some(a => a.urgency === "CRITICAL_STAT_PANIC");
    const elevated = alerts.length > 0;
    return {
      mode: "LOCAL_DEMONSTRATION",
      clinical_validation: "NONE — do not use for treatment decisions",
      task_id: task,
      target_identifier: target,
      overall_urgency: critical ? "CRITICAL_STAT_PANIC" : elevated ? "ELEVATED_RISK" : "ROUTINE",
      integrity_status: critical ? "RECALIBRATION_REQUIRED" : elevated ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
      total_alerts: alerts.length,
      alerts,
      thresholds: { primary_exceeds: 25, secondary_exceeds: 12 },
      note: "This is a rules demonstration, not a biomarker assay interpretation or prediction."
    };
  }

  if (typeof module !== "undefined" && module.exports) module.exports = { evaluateDemo };

  if (typeof document === "undefined") return;
  const form = document.getElementById("audit-form");
  const output = document.getElementById("output");
  const caption = document.getElementById("result-caption");
  const runs = document.getElementById("runs");
  const lastState = document.getElementById("last-state");
  const save = document.getElementById("save");
  let lastResult = null;
  let count = 0;

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    try {
      const payload = {
        task_id: document.getElementById("task_id").value.trim(),
        target_identifier: document.getElementById("target_identifier").value.trim(),
        primary_metric: document.getElementById("primary_metric").value,
        secondary_metric: document.getElementById("secondary_metric").value,
        status_descriptor: document.getElementById("status_descriptor").value,
        is_critical_flag: document.getElementById("is_critical_flag").checked
      };
      lastResult = evaluateDemo(payload);
      count += 1;
      runs.textContent = String(count);
      lastState.textContent = lastResult.overall_urgency;
      caption.textContent = "Local rules evaluated. No data was submitted to a server.";
      output.textContent = JSON.stringify(lastResult, null, 2);
      save.disabled = false;
    } catch (error) {
      lastResult = null;
      save.disabled = true;
      caption.textContent = "Validation error. Correct the inputs and run again.";
      output.textContent = error.message;
    }
  });

  document.getElementById("clear").addEventListener("click", function () {
    output.textContent = "No evaluation yet.";
    caption.textContent = "Run the synthetic example to see which demo rules trigger.";
    lastState.textContent = "Not run";
    lastResult = null;
    save.disabled = true;
  });
  save.addEventListener("click", function () {
    if (!lastResult) return;
    const blob = new Blob([JSON.stringify(lastResult, null, 2) + "\n"], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "immunotherapy-demo-result.json";
    link.click();
    URL.revokeObjectURL(url);
  });
}());
