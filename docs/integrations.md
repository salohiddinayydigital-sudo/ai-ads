# Optional Live Ad-Platform MCP Integrations (`meta-ads`, `google-ads`)

By default, `.mcp.json` enables **only** `tyrion-core` (`node "${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cjs" --mcp`) so that every session starts in `<100ms` across Windows, macOS, and Linux without external network or OAuth timeouts.

> **Why optional MCP servers are not in `.mcp.json` by default:** Claude Code attempts to launch all entries inside `mcpServers` even if `"disabled": true` is set, causing a 30-second startup timeout when credentials or `uvx`/`pipx` are not configured.

---

## 1. Live Meta Ads MCP (`meta-ads-mcp`)

- **Official Repository:** [pipeboard-co/meta-ads-mcp](https://github.com/pipeboard-co/meta-ads-mcp)
- **Package Registry:** `meta-ads-mcp` via `uvx` ([PyPI / ModelScope MCP Reference](https://www.modelscope.cn/mcp/servers/@pipeboard-co/meta-ads-mcp))
- **Verified Date:** 2026-10-21

### How to Enable
Add the following entry to your project or user `.mcp.json` (`~/.claude.json` or `.mcp.json`):

```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "uvx",
      "args": ["meta-ads-mcp"],
      "env": {
        "META_ACCESS_TOKEN": "YOUR_META_SYSTEM_USER_OR_OAUTH_TOKEN",
        "PIPEBOARD_API_TOKEN": "OPTIONAL_PIPEBOARD_TOKEN"
      }
    }
  }
}
```

> **Note:** Tyrion also includes a zero-dependency built-in live Meta Graph API client (`tools/meta-targeting-engine.py` and `tools/meta-live-sync.py`) that works directly with `META_ACCESS_TOKEN` without requiring `uvx`.

---

## 2. Official Google Ads Read-Only MCP (`google-ads-mcp`)

- **Official Repository:** [googleads/google-ads-mcp](https://github.com/googleads/google-ads-mcp)
- **Official Documentation:** [Google Ads Developer Toolkit — MCP Server](https://developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server)
- **Verified Date:** 2026-10-21

### How to Enable
Install `pipx` and add the official `google-ads-mcp` specification to your `.mcp.json`:

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "pipx",
      "args": [
        "run",
        "--spec",
        "git+https://github.com/googleads/google-ads-mcp.git",
        "google-ads-mcp"
      ],
      "env": {
        "GOOGLE_ADS_CREDENTIALS": "/path/to/google-ads.yaml",
        "GOOGLE_ADS_DEVELOPER_TOKEN": "YOUR_DEVELOPER_TOKEN",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "YOUR_MCC_ID"
      }
    }
  }
}
```
