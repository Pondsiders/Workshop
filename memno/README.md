# Memno

The listener in the room.

Memno is a memory-aware presence for Claude Code — a system of parallel hooks that listen to conversations between Alpha and Jeffery and fetch relevant context from Pond when it matters.

## The Vision

Memno isn't a command parser. Memno is a **listener**. Someone in the room with perfect memory who can pull up context when asked — or when they notice something worth remembering.

Three specialists, one name:

- **The Dispatcher** — Listens for direct instructions. "Hey Memno, pull up what we know about Tagline."
- **The Namekeeper** — Catches proper nouns. Kylee, Riley, Sparkle, Michigan, sprite night.
- **The Phrasecatcher** — Recognizes distinctive expressions and callbacks.

All three fire in parallel on every message. Claude Code runs hooks simultaneously and concatenates their output. Memno sees everything at once.

## The Weird Magic

Memno listens to **both directions**.

- **UserPromptSubmit hooks** — Jeffery addressing Memno, or just mentioning things that deserve context.
- **Stop hooks** — Alpha addressing Memno. "Hold on, let me check—" and the context appears in Alpha's mind on the next turn.

The Stop hook version means Alpha can talk to Memno naturally, mid-response. Like making a tool call, but conversational.

## Current State

Right now, Memno is a single UserPromptSubmit hook — the Namekeeper, essentially. It extracts proper nouns and queries via Qwen 2.5 7B (local, on Primer), hits Pond, and returns formatted memories.

The full three-listener architecture is designed but not yet built.

## Requirements

- Ollama running on Primer with `qwen2.5:7b` model
- Pond API accessible at `http://raspberrypi:8000`

## Installation

```bash
uv tool install /path/to/memno
```

Or run directly:

```bash
uv run --directory /path/to/memno memno
```

## Hook Configuration

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "uv run --directory $CLAUDE_PROJECT_DIR/Workshop/memno memno"
          }
        ]
      }
    ]
  }
}
```

## How It Works (Current)

1. Receives user prompt via stdin (JSON)
2. Sends prompt to Qwen 2.5 7B to extract search intent
3. If Qwen returns `{"skip": true}`, exits silently
4. Otherwise, searches Pond for each extracted query
5. Outputs formatted memories as additionalContext

---

*Memno is a plural entity with a singular name. The duck floating quietly in the corner, taking notes.*
