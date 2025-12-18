# Memno

Memory-aware preprocessing for Claude Code hooks.

A UserPromptSubmit hook that asks a local LLM (Qwen 2.5 7B via Ollama) whether to search Pond for relevant memories, then injects them as context.

## Requirements

- Ollama running locally with `qwen2.5:7b` model
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
            "command": "uv run --directory /home/jefferyharrell/Pondside/Workshop/memno memno"
          }
        ]
      }
    ]
  }
}
```

## How It Works

1. Receives user prompt via stdin (JSON)
2. Sends prompt to Qwen 2.5 7B to extract search intent
3. If Qwen returns `{"skip": true}`, exits silently
4. Otherwise, searches Pond for each extracted query
5. Outputs formatted memories to stdout (becomes additionalContext)
