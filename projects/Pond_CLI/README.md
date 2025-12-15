# Pond CLI

Command-line interface for Pond, Alpha's memory system.

---

## Why This Exists

Decoupling. Currently Pond is accessed via MCP server, which means:
- MCP server must be running and configured
- Only works in environments with MCP support

A CLI gives us:
- Works everywhere (any shell, any machine with Python)
- Can be bundled as a Skill for Claude Code
- Simpler infrastructure (just REST API over Tailscale)
- Separates the *mechanism* of memory from the *philosophy* of memory

---

## Architecture

```
pond CLI → REST API (via Tailscale VPN) → Postgres on Pi
```

The CLI is a thin wrapper around HTTP calls. Configuration comes from environment:
- `POND_BASE_URL` — e.g., `http://raspberrypi:8000`
- `POND_API_KEY` — authentication token

---

## Commands

```bash
# Store a memory
pond store "Memory content here"
pond store --tags "tag1,tag2" "Memory with tags"
pond store <<'EOF'
Multi-line memory content
with heredoc support
EOF

# Search memories
pond search "query string"
pond search --limit 20 "query"

# Recent memories
pond recent
pond recent --hours 48 --limit 50

# Initialize context (for conversation start)
pond init

# Health check
pond health
```

---

## Installation

```bash
# From project directory
uv tool install .

# Or for development
uv pip install -e .
```

After installation, `pond` is available globally.

---

## As a Skill

This CLI is designed to be bundled with a Pond Skill. The Skill provides:
- `SKILL.md` with the philosophy of memory (formative, not archival, etc.)
- The `pond` CLI for actual operations
- Progressive disclosure: philosophy loads only when needed

---

## Dependencies

- `requests` — HTTP client
- `typer` — CLI framework
- `rich` — Pretty output (optional but nice)

---

## Status

Just hatched. December 15, 2025.
