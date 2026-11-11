#!/usr/bin/env node
/**
 * Runs a Claude Code workflow script against stubbed runtime hooks, at zero token cost.
 *
 * The real runtime provides agent(), pipeline(), parallel(), phase(), log() and args.
 * Here agent() answers from a scenario file keyed by the agent's label, so a test can assert
 * the orchestration itself: which agents are spawned, with which agentType, in which phase,
 * and what the script returns when evidence is missing or an agent dies.
 *
 * Usage: node tests/workflow_harness.cjs <script.js> <scenario.json>
 *   scenario: { "args": <any>, "answers": { "<label>": <value|null> }, "default": <value> }
 * Prints: { meta, calls, phases, logs, result } or { error }.
 */
"use strict";

const fs = require("fs");

const [scriptPath, scenarioPath] = process.argv.slice(2);
const source = fs.readFileSync(scriptPath, "utf-8");
const scenario = JSON.parse(fs.readFileSync(scenarioPath, "utf-8"));

if (!/^\s*export const meta = \{/.test(source)) {
  console.log(JSON.stringify({ error: "script must begin with `export const meta = {`" }));
  process.exit(0);
}
if (/\bimport\s*\(/.test(source)) {
  console.log(JSON.stringify({ error: "import() is not available in a workflow script" }));
  process.exit(0);
}

const calls = [];
const phases = [];
const logs = [];
let currentPhase = null;

const agent = async (prompt, opts = {}) => {
  const label = opts.label != null ? String(opts.label) : `agent ${calls.length + 1}`;
  calls.push({
    label,
    agentType: opts.agentType || null,
    phase: opts.phase != null ? String(opts.phase) : currentPhase,
    schema: Boolean(opts.schema),
    prompt: String(prompt),
  });
  const answers = scenario.answers || {};
  if (Object.prototype.hasOwnProperty.call(answers, label)) return answers[label];
  return Object.prototype.hasOwnProperty.call(scenario, "default") ? scenario.default : null;
};

// Each item runs through every stage; a stage that throws drops the item to null.
const pipeline = async (items, ...stages) =>
  Promise.all(
    items.map(async (item, index) => {
      let prev = item;
      try {
        for (const stage of stages) prev = await stage(prev, item, index);
        return prev;
      } catch (_) {
        return null;
      }
    }),
  );

// A barrier: a thunk that throws resolves to null, the call itself never rejects.
const parallel = async thunks => Promise.all(thunks.map(t => Promise.resolve().then(t).catch(() => null)));

const phase = title => {
  currentPhase = String(title);
  phases.push(currentPhase);
};
const log = message => logs.push(String(message));

// The runtime makes these throw so a relaunched run repeats the same agent() calls.
const frozenDate = new Proxy(Date, {
  construct(target, argv) {
    if (argv.length === 0) throw new Error("argless new Date() is not allowed in a workflow");
    return new target(...argv);
  },
  get(target, prop) {
    if (prop === "now") return () => { throw new Error("Date.now() is not allowed in a workflow"); };
    return Reflect.get(target, prop);
  },
});
const frozenMath = Object.create(Math, {
  random: { value: () => { throw new Error("Math.random() is not allowed in a workflow"); } },
});

const body = source.replace(/^\s*export const meta = /, "const meta = ");
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;

let run;
try {
  run = new AsyncFunction(
    "agent", "pipeline", "parallel", "phase", "log", "args", "Date", "Math",
    `${body}\n;return undefined;`,
  );
} catch (err) {
  console.log(JSON.stringify({ error: `syntax error: ${err.message}` }));
  process.exit(0);
}

// meta must be a pure literal: evaluate it alone, with nothing else in scope.
let meta = null;
try {
  const literal = source.slice(source.indexOf("{"), source.indexOf("\n}\n") + 2);
  meta = new Function(`"use strict"; return (${literal});`)();
} catch (err) {
  console.log(JSON.stringify({ error: `meta is not a pure literal: ${err.message}` }));
  process.exit(0);
}

run(agent, pipeline, parallel, phase, log, scenario.args, frozenDate, frozenMath)
  .then(result => console.log(JSON.stringify({ meta, calls, phases, logs, result })))
  .catch(err => console.log(JSON.stringify({ meta, calls, phases, logs, error: String(err && err.message) })));
