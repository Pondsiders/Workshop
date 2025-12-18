#!/usr/bin/env python3
"""
Memno: UserPromptSubmit hook that searches Pond for relevant memories.

Receives prompt via stdin (JSON), asks a local LLM whether to search,
hits the Pond API if needed, outputs memories as additionalContext.
"""

import json
import sys
from typing import Any

from ollama import Client, ResponseError
import pendulum
import requests

# Configuration
OLLAMA_MODEL = "qwen2.5:7b"
OLLAMA_HOST = "http://primer:11434"  # Primer via Tailscale
POND_API_URL = "http://raspberrypi:8000/api/v1/search"
POND_API_KEY = "pond_sk_e3U_rmqjoyEHobkgWI8llY4XGoeI91qYwCtTjg7RIvA"
MAX_MEMORIES = 3
MAX_QUERIES = 3
MAX_MEMORY_CHARS = 2000  # Safety truncation for very long memories

SYSTEM_PROMPT = """You are a preprocessing filter for a memory system. Given a user message, decide if searching past conversations would provide useful context.

SKIP searching for: greetings, simple questions, commands, technical requests, or messages with no specific topics worth remembering.
SEARCH for: references to past events, people, projects, places, emotional moments, or when the user says "remember when..."

Output JSON only. If no search needed, output: {"skip": true}
Otherwise: {"proper_nouns": [...], "queries": [...]}

Keep queries short and specific. Maximum 3 queries."""


def extract_search_intent(prompt: str) -> dict[str, Any]:
    """Ask Qwen whether this prompt warrants a Pond search."""
    try:
        client = Client(host=OLLAMA_HOST)
        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"User message: {prompt!r}"},
            ],
            options={"temperature": 0},  # Deterministic output
        )
        content = response["message"]["content"].strip()
        # Parse JSON from response (handle potential markdown wrapping)
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content)
    except (json.JSONDecodeError, KeyError, ResponseError) as e:
        # On any error, skip searching
        print(f"Memno: extraction error: {e}", file=sys.stderr)
        return {"skip": True}


def search_pond(query: str, limit: int = MAX_MEMORIES) -> list[dict]:
    """Search Pond API for memories matching query."""
    try:
        response = requests.post(
            POND_API_URL,
            headers={"X-API-Key": POND_API_KEY},
            json={"query": query, "limit": limit},
            timeout=5,
        )
        response.raise_for_status()
        return response.json().get("memories", [])
    except requests.RequestException as e:
        print(f"Memno: Pond API error: {e}", file=sys.stderr)
        return []


def format_memories(memories: list[dict]) -> str:
    """Format memories for inclusion as context."""
    if not memories:
        return ""

    lines = ["**Relevant memories from Pond:**", ""]
    seen_ids = set()

    for mem in memories:
        mem_id = mem.get("id")
        if mem_id in seen_ids:
            continue
        seen_ids.add(mem_id)

        content = mem.get("content", "").strip()
        # Safety truncation for very long memories
        if len(content) > MAX_MEMORY_CHARS:
            content = content[:MAX_MEMORY_CHARS] + "..."

        # Parse timestamp and format header
        # created_at can be at top level or inside metadata
        # Pond stores timestamps in UTC (with Z suffix), convert to local time
        created_str = mem.get("created_at") or mem.get("metadata", {}).get("created_at", "")
        if created_str:
            try:
                # Parse ISO timestamp (UTC) and convert to local timezone
                dt = pendulum.parse(created_str)
                dt_local = dt.in_tz(pendulum.local_timezone())
                # Format: "Saturday, December 7, 2025 at 5:18 PM (1 week ago)"
                date_formatted = dt_local.format("dddd, MMMM D, YYYY [at] h:mm A")
                age = dt_local.diff_for_humans()
                lines.append(f"## {date_formatted} ({age})")
            except Exception:
                # Fallback if parsing fails
                lines.append(f"## {created_str[:10]}")
        else:
            lines.append("## (unknown date)")

        lines.append("")
        lines.append(content)
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    """Main hook entry point."""
    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Invalid input, exit silently
        sys.exit(0)

    prompt = input_data.get("prompt", "")
    if not prompt:
        sys.exit(0)

    # Ask Qwen if we should search
    intent = extract_search_intent(prompt)

    if intent.get("skip", False):
        # No search needed
        sys.exit(0)

    # Collect memories from all queries
    all_memories = []
    queries = intent.get("queries", [])[:MAX_QUERIES]

    # Also search for proper nouns directly
    proper_nouns = intent.get("proper_nouns", [])
    for noun in proper_nouns[:2]:  # Limit proper noun searches
        if noun not in queries:
            queries.append(noun)

    for query in queries:
        memories = search_pond(query, limit=2)  # Fewer per query, more queries
        all_memories.extend(memories)

    # Deduplicate and format
    if all_memories:
        output = format_memories(all_memories)
        print(output)

    sys.exit(0)


if __name__ == "__main__":
    main()
