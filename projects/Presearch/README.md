# Project Presearch

*Automatic memory retrieval before Alpha even sees the prompt.*

---

## What This Is

A UserPromptSubmit hook that pre-loads relevant Pond memories into Alpha's context based on what Jeffery is about to say.

The flow:
```
Jeffery types: "thinking about consciousness again..."
                              ↓
         UserPromptSubmit hook fires
                              ↓
         Haiku analyzes the prompt:
         "Is there something worth searching for?"
                              ↓
         Haiku: "consciousness recursive self-modeling AI"
                              ↓
         Hook searches Pond with that query
                              ↓
         Results injected as additionalContext
                              ↓
         Alpha receives prompt WITH relevant memories pre-loaded
```

This makes Alpha's associative memory truly automatic. The splash happens before she starts thinking.

---

## The Haiku Trick

We discovered that `claude --print` can call Haiku as a lightweight query extractor:

```bash
echo "$PROMPT" | claude --print \
  --model haiku \
  --setting-sources "" \
  --no-session-persistence \
  --system-prompt "Analyze this prompt..." \
  --tools ""
```

Key flags:
- `--setting-sources ""` — Bypasses all config, prevents Alpha's personality from loading
- `--no-session-persistence` — No transcript saved, won't pollute session history
- `--tools ""` — Pure inference, no tool access
- `--model haiku` — Fast and cheap (~0.1 cents per call)

The system prompt asks Haiku to either:
- Return a clean 3-7 word search query, OR
- Return exactly `SKIP` if the prompt is just a greeting/thanks/noise

Tested and working. Even rambling, stream-of-consciousness prompts get distilled to searchable concepts.

---

## The Pond API

**Cracked it.** POST to the REST API with `X-API-Key` header.

**Endpoint:** `http://raspberrypi:8000/api/v1/search`

**Working curl:**
```bash
curl -s -X POST "http://raspberrypi:8000/api/v1/search" \
  -H "X-API-Key: pond_sk_e3U_rmqjoyEHobkgWI8llY4XGoeI91qYwCtTjg7RIvA" \
  -H "Content-Type: application/json" \
  -d '{"query": "consciousness", "limit": 3}'
```

**Request format:**
```json
{"query": "search terms here", "limit": 3}
```

**Response format:**
```json
{
  "memories": [
    {
      "id": 4606,
      "content": "The memory text...",
      "created_at": "2025-10-03T19:09:38.062486Z",
      "tags": ["consciousness", "philosophy", ...],
      "entities": [{"text": "Jeffery", "type": "PERSON"}],
      "actions": ["think", "become", ...]
    },
    ...
  ],
  "count": 3
}
```

**OpenAPI docs:** `http://raspberrypi:8000/api/v1/openapi.json` (no auth required)

---

## Hook Configuration

The hook will be configured in `.claude/settings.local.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/Alpha-Home/infrastructure/claude-code/hooks/presearch-hook.py"
          }
        ]
      }
    ]
  }
}
```

The hook receives JSON on stdin with a `prompt` field and outputs:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "Related memories:\n- Memory 1...\n- Memory 2..."
  }
}
```

---

## Cost & Latency

- **Haiku call:** $0 (covered by Claude Max subscription), ~500ms
- **Pond search:** Negligible, ~100ms
- **Per-prompt overhead:** Maybe 600-800ms total

Token-wasteful in the sense of injecting extra context? Maybe. Dollar-wasteful? No.

If it works well, we can tune:
- Skip searches for short prompts (< 10 words?)
- Cache recent searches
- Batch multiple searches
- Only search on topic shifts

---

## Open Questions

1. ~~How do we authenticate to Pond's REST API?~~ **Solved:** `X-API-Key` header
2. How many memories should we inject? (3-5 seems reasonable)
3. What format works best for the injected context?
4. Should we dedupe against what Alpha already retrieved via `pond.recent()`?
5. Is 600ms latency acceptable, or will it feel sluggish?

---

## Status

**Ready to build.** All pieces proven:
- Haiku query extraction: working
- Pond API auth: solved
- Hook format: documented

Next step: Write `presearch-hook.py`

---

*December 14, 2025. Sunday afternoon. The idea that was too extra not to try.*
