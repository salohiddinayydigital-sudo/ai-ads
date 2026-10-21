#!/usr/bin/env node
/**
 * Tyrion Cross-Platform Hook & MCP Launcher (Windows / macOS / Linux)
 * Resolves ${CLAUDE_PLUGIN_ROOT} automatically, locates python3 -> python -> py -3,
 * runs maintainer hooks (ingest, dod) only when TYRION_DEV=1, and fails open (exit 0)
 * on environment errors unless TYRION_HOOK_PROFILE=strict.
 */
"use strict";

const { spawnSync, spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const PLUGIN_ROOT = process.env.CLAUDE_PLUGIN_ROOT
  ? path.resolve(process.env.CLAUDE_PLUGIN_ROOT)
  : path.resolve(__dirname, "..");

const PROFILE = (process.env.TYRION_HOOK_PROFILE || "standard").trim().toLowerCase();
const IS_STRICT = PROFILE === "strict";
const IS_DEV = process.env.TYRION_DEV === "1" || process.env.TYRION_DEV === "true";

function findPython() {
  const candidates = process.platform === "win32"
    ? [
        { cmd: "python3", prefixArgs: [] },
        { cmd: "python", prefixArgs: [] },
        { cmd: "py", prefixArgs: ["-3"] },
      ]
    : [
        { cmd: "python3", prefixArgs: [] },
        { cmd: "python", prefixArgs: [] },
      ];

  for (const cand of candidates) {
    try {
      const res = spawnSync(cand.cmd, [...cand.prefixArgs, "--version"], {
        stdio: "ignore",
        timeout: 3000,
        windowsHide: true,
      });
      if (res && res.status === 0) {
        return cand;
      }
    } catch (_) {
      // Try next candidate
    }
  }
  return null;
}

function failOpenOrStrict(reason) {
  process.stderr.write(`⚠ tyrion-hook: ${reason} (non-blocking)\n`);
  process.exit(IS_STRICT ? 2 : 0);
}

const args = process.argv.slice(2);

// Mode 1: STDIO MCP Server launcher (--mcp)
if (args[0] === "--mcp") {
  const mcpScript = path.join(PLUGIN_ROOT, "tools", "tyrion-mcp-server.py");
  if (!fs.existsSync(mcpScript)) {
    process.stderr.write(`✗ tyrion-mcp-server.py not found at ${mcpScript}\n`);
    process.exit(1);
  }
  const py = findPython();
  if (!py) {
    process.stderr.write("✗ Python 3.10+ interpreter not found (tried python3, python, py -3)\n");
    process.exit(1);
  }
  const child = spawn(py.cmd, [...py.prefixArgs, mcpScript, ...args.slice(1)], {
    stdio: "inherit",
    env: { ...process.env, CLAUDE_PLUGIN_ROOT: PLUGIN_ROOT, PYTHONIOENCODING: "utf-8" },
    windowsHide: true,
  });
  child.on("error", (err) => {
    process.stderr.write(`✗ Failed to start tyrion-mcp-server: ${err.message}\n`);
    process.exit(1);
  });
  child.on("exit", (code) => {
    process.exit(code === null ? 0 : code);
  });
  return;
}

// Mode 2: Lifecycle Hook launcher (brief | guard | ingest | dod)
const hookMode = args[0] || "";

// Fast exit for maintainer-only hooks (ingest, dod) when not in TYRION_DEV=1 mode
if ((hookMode === "ingest" || hookMode === "dod") && !IS_DEV) {
  process.exit(0);
}

const hookScript = path.join(PLUGIN_ROOT, "hooks", "tyrion-hook.py");
if (!fs.existsSync(hookScript)) {
  failOpenOrStrict(`hook script not found at ${hookScript}`);
}

const py = findPython();
if (!py) {
  failOpenOrStrict("Python interpreter not found");
}

// Extract target file path from Claude Code PreToolUse/PostToolUse stdin payload if available
let extraArgs = [...args];
if (hookMode === "guard" && !extraArgs.includes("--target")) {
  try {
    if (!process.stdin.isTTY) {
      const rawStdin = fs.readFileSync(0, "utf-8").trim();
      if (rawStdin.startsWith("{")) {
        const payload = JSON.parse(rawStdin);
        const toolInput = payload.tool_input || payload.input || {};
        const filePath = toolInput.file_path || toolInput.path || toolInput.target_file || "";
        if (filePath) {
          extraArgs.push("--target", String(filePath));
        }
      }
    }
  } catch (_) {
    // Ignore stdin parse errors and continue
  }
}

try {
  const timeoutMs = hookMode === "dod" ? 4500 : 15000;
  const res = spawnSync(py.cmd, [...py.prefixArgs, hookScript, ...extraArgs], {
    encoding: "utf-8",
    timeout: timeoutMs,
    env: { ...process.env, CLAUDE_PLUGIN_ROOT: PLUGIN_ROOT, PYTHONIOENCODING: "utf-8" },
    windowsHide: true,
  });

  if (res.stdout) process.stdout.write(res.stdout);
  if (res.stderr) process.stderr.write(res.stderr);

  if (res.error) {
    failOpenOrStrict(`execution error: ${res.error.message}`);
  }
  if (typeof res.status === "number" && res.status !== 0) {
    process.exit(IS_STRICT ? res.status : 0);
  }
  process.exit(0);
} catch (err) {
  failOpenOrStrict(`unexpected error: ${err.message}`);
}
