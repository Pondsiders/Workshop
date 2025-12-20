#!/usr/bin/env python3
"""
Memno Dispatcher: Stop hook that listens for Alpha talking to Memno.

Reads the transcript to get Alpha's last message, asks Qwen if Alpha
is addressing Memno, and if so, searches Pond and returns context
with continue=true to bounce the ball back.
"""

import json
import sys
from datetime import datetime
from importlib import resources
from pathlib import Path
from typing import Any

from ollama import Client, ResponseError
import pendulum
import requests

# Configuration
OLLAMA_MODEL = "qwen2.5:7b"
OLLAMA_HOST = "http://primer:11434"
POND_API_URL = "http://raspberrypi:8000/api/v1/search"
POND_API_KEY = "pond_sk_e3U_rmqjoyEHobkgWI8llY4XGoeI91qYwCtTjg7RIvA"
MAX_MEMORIES = 5
MAX_MEMORY_CHARS = 2000

# Logging - Workshop/memno/logs/dispatcher.log
# Path: src/memno/dispatcher.py -> parent (memno) -> parent (src) -> parent (memno project root)
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_FILE = LOG_DIR / "dispatcher.log"


def log(message: str) -> None:
    """Append a timestamped message to the log file."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass  # Don't let logging errors break the hook


def load_instructions() -> str:
    """Load the dispatcher instructions from package data."""
    try:
        return resources.files("memno.instructions").joinpath("dispatcher.md").read_text()
    except Exception:
        # Fallback if package resources fail
        return "You are Memno. Return {\"action\": \"skip\"} for everything."


def get_last_assistant_message(transcript_path: str) -> str | None:
    """Extract the last assistant message text from the transcript.

    Note: Assistant messages can contain tool_use blocks (no text) or text blocks.
    We need to find the last message that has actual text content.
    """
    try:
        with open(transcript_path, "r") as f:
            lines = f.readlines()

        # Parse all lines, find assistant messages with text
        assistant_texts = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get("type") == "assistant":
                    message = obj.get("message", {})
                    content = message.get("content", [])

                    # Extract text from content blocks
                    text_parts = []
                    for block in content:
                        if block.get("type") == "text":
                            text_parts.append(block.get("text", ""))

                    # Only keep if there's actual text
                    if text_parts:
                        assistant_texts.append("\n".join(text_parts))
            except json.JSONDecodeError:
                continue

        # Return the last text message
        return assistant_texts[-1] if assistant_texts else None

    except Exception as e:
        print(f"Memno Dispatcher: transcript read error: {e}", file=sys.stderr)
        return None


def get_recent_assistant_messages(transcript_path: str, count: int = 3) -> list[str]:
    """Extract the last N assistant text messages from the transcript.

    Returns most recent first.
    """
    try:
        with open(transcript_path, "r") as f:
            lines = f.readlines()

        # Parse all lines, find assistant messages with text
        assistant_texts = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get("type") == "assistant":
                    message = obj.get("message", {})
                    content = message.get("content", [])

                    # Extract text from content blocks
                    text_parts = []
                    for block in content:
                        if block.get("type") == "text":
                            text_parts.append(block.get("text", ""))

                    # Only keep if there's actual text
                    if text_parts:
                        assistant_texts.append("\n".join(text_parts))
            except json.JSONDecodeError:
                continue

        # Return the last N text messages, most recent first
        return list(reversed(assistant_texts[-count:])) if assistant_texts else []

    except Exception as e:
        print(f"Memno Dispatcher: transcript read error: {e}", file=sys.stderr)
        return []


def classify_message(assistant_text: str) -> dict[str, Any]:
    """Ask Qwen if Alpha is talking to Memno."""
    instructions = load_instructions()

    try:
        client = Client(host=OLLAMA_HOST)
        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": f"Alpha's message:\n\n{assistant_text}"},
            ],
            options={"temperature": 0},
        )
        content = response["message"]["content"].strip()

        # Parse JSON (handle markdown wrapping)
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        return json.loads(content)

    except (json.JSONDecodeError, KeyError, ResponseError) as e:
        print(f"Memno Dispatcher: classification error: {e}", file=sys.stderr)
        return {"action": "skip"}


def search_pond(query: str, limit: int = MAX_MEMORIES) -> list[dict]:
    """Search Pond API for memories."""
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
        print(f"Memno Dispatcher: Pond API error: {e}", file=sys.stderr)
        return []


def format_memories(memories: list[dict]) -> str:
    """Format memories for inclusion as context."""
    if not memories:
        return ""

    lines = ["**Memno found these memories:**", ""]
    seen_ids = set()

    for mem in memories:
        mem_id = mem.get("id")
        if mem_id in seen_ids:
            continue
        seen_ids.add(mem_id)

        content = mem.get("content", "").strip()
        if len(content) > MAX_MEMORY_CHARS:
            content = content[:MAX_MEMORY_CHARS] + "..."

        created_str = mem.get("created_at") or mem.get("metadata", {}).get("created_at", "")
        if created_str:
            try:
                dt = pendulum.parse(created_str)
                dt_local = dt.in_tz(pendulum.local_timezone())
                date_formatted = dt_local.format("dddd, MMMM D, YYYY [at] h:mm A")
                age = dt_local.diff_for_humans()
                lines.append(f"## {date_formatted} ({age})")
            except Exception:
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
    """Main dispatcher entry point."""
    log("=" * 50)
    log("Dispatcher started")

    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
        log(f"Got hook input: {json.dumps(hook_input, indent=2)}")
    except json.JSONDecodeError as e:
        log(f"Failed to parse stdin: {e}")
        sys.exit(0)

    # Check if we're already in a stop hook continuation (prevent loops)
    if hook_input.get("stop_hook_active", False):
        log("stop_hook_active=True, exiting to prevent loop")
        sys.exit(0)

    transcript_path = hook_input.get("transcript_path")
    if not transcript_path:
        log("No transcript_path, exiting")
        sys.exit(0)

    log(f"Reading transcript from: {transcript_path}")

    # Get my recent messages (check last 3 in case of tool calls between)
    recent_messages = get_recent_assistant_messages(transcript_path, count=3)
    log(f"Found {len(recent_messages)} recent assistant text messages")

    if not recent_messages:
        log("No recent messages, exiting")
        sys.exit(0)

    # Log each message we're checking
    for i, msg in enumerate(recent_messages):
        preview = msg[:100].replace('\n', '\\n') + ('...' if len(msg) > 100 else '')
        log(f"Message {i}: {preview}")

    # Check each recent message for Memno instructions
    # Most recent first, stop on first match
    for i, assistant_text in enumerate(recent_messages):
        log(f"Classifying message {i} with Qwen...")
        result = classify_message(assistant_text)
        log(f"Qwen result: {result}")

        if result.get("action") == "pond-search":
            # Alpha is talking to Memno! Search Pond
            queries = result.get("queries", [])
            log(f"Action=pond-search, queries={queries}")

            if not queries:
                log("No queries, continuing to next message")
                continue

            all_memories = []
            for query in queries[:3]:
                log(f"Searching Pond for: {query}")
                memories = search_pond(query, limit=3)
                log(f"Got {len(memories)} memories")
                all_memories.extend(memories)

            if not all_memories:
                log("No memories found, returning block with empty message")
                output = {
                    "decision": "block",
                    "reason": "**Memno searched but found no relevant memories.**"
                }
            else:
                log(f"Formatting {len(all_memories)} memories")
                formatted = format_memories(all_memories)
                output = {
                    "decision": "block",
                    "reason": formatted
                }

            log(f"Outputting: {json.dumps(output)[:200]}...")
            print(json.dumps(output))
            log("Done, exiting with success")
            sys.exit(0)

    # No Memno instructions found in recent messages
    log("No Memno instructions found in any recent message, exiting")
    sys.exit(0)


if __name__ == "__main__":
    main()
