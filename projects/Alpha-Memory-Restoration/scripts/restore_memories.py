#!/usr/bin/env python3
"""
Alpha Memory Restoration Script

Recovers narrative memories from Alpha-Recall Redis dumps and imports them
into Pond with original timestamps preserved.

This script:
1. Connects to a Redis instance loaded with an Alpha-Recall dump
2. Extracts all narrative:story_* memories
3. Embeds them using Ollama's nomic-embed-text
4. Inserts them into Pond's PostgreSQL database with original timestamps

Usage:
    # First, start Redis with the dump:
    docker run -d --name alpha-restore -v /path/to/redis:/data -p 6380:6379 redis:latest

    # Then run this script:
    uv run python scripts/restore_memories.py --redis-port 6380
"""

import argparse
import json
import hashlib
from datetime import datetime
from typing import Optional

import redis
import psycopg2
import httpx


# Configuration
POND_DB_URL = "postgresql://postgres:postgres@raspberrypi/pond"
OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text:latest"
EMBEDDING_DIM = 768


def get_embedding(text: str) -> list[float]:
    """Get embedding from Ollama."""
    response = httpx.post(
        OLLAMA_URL,
        json={"model": EMBEDDING_MODEL, "prompt": text},
        timeout=60.0,
    )
    response.raise_for_status()
    return response.json()["embedding"]


def content_hash(content: str) -> str:
    """Generate a hash of the content for deduplication."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def extract_memories_from_redis(r: redis.Redis) -> list[dict]:
    """Extract all narrative memories from Redis."""
    memories = []

    keys = r.keys("narrative:story_*")
    print(f"Found {len(keys)} narrative memories in Redis")

    for key in keys:
        key_str = key.decode() if isinstance(key, bytes) else key

        try:
            data = r.hgetall(key)
            # Decode bytes to strings
            decoded = {}
            for k, v in data.items():
                k_str = k.decode() if isinstance(k, bytes) else k
                # Skip binary embedding fields
                if "semantic" in k_str or "emotional" in k_str or "embedding" in k_str:
                    continue
                try:
                    v_str = v.decode() if isinstance(v, bytes) else v
                    decoded[k_str] = v_str
                except UnicodeDecodeError:
                    continue

            # Extract the fields we need
            title = decoded.get("title", "Untitled Memory")
            created_at = decoded.get("created_at")
            tags_str = decoded.get("tags", "[]")
            paragraphs_str = decoded.get("paragraphs", "[]")
            story_id = decoded.get("story_id", key_str.split("_", 1)[1] if "_" in key_str else key_str)

            # Parse JSON fields
            try:
                tags = json.loads(tags_str)
            except json.JSONDecodeError:
                tags = []

            try:
                paragraphs = json.loads(paragraphs_str)
            except json.JSONDecodeError:
                paragraphs = []

            # Build content from paragraphs
            if paragraphs:
                para_texts = [p.get("text", "") for p in sorted(paragraphs, key=lambda x: x.get("order", 0))]
                content = f"# {title}\n\n" + "\n\n".join(para_texts)
            else:
                content = f"# {title}"

            # Ensure tags is a list of strings
            if isinstance(tags, list):
                tags = [str(t) for t in tags]
            else:
                tags = []

            memories.append({
                "story_id": story_id,
                "title": title,
                "content": content,
                "created_at": created_at,
                "tags": tags + ["restored", "alpha-recall"],
            })

        except Exception as e:
            print(f"Error processing {key_str}: {e}")
            continue

    return memories


def memory_exists(cursor, content: str) -> bool:
    """Check if a memory with similar content already exists."""
    # Check by content hash in tags
    chash = content_hash(content)
    cursor.execute(
        "SELECT id FROM alpha.memories WHERE metadata->'tags' ? %s",
        (f"hash:{chash}",)
    )
    if cursor.fetchone():
        return True

    # Also check for exact content match (first 500 chars to avoid huge comparisons)
    cursor.execute(
        "SELECT id FROM alpha.memories WHERE LEFT(content, 500) = LEFT(%s, 500)",
        (content,)
    )
    return cursor.fetchone() is not None


def insert_memory(cursor, content: str, embedding: list[float], created_at: str, tags: list[str]) -> Optional[int]:
    """Insert a memory into Pond."""
    # Add content hash to tags for deduplication
    tags_with_hash = tags + [f"hash:{content_hash(content)}"]

    metadata = {
        "created_at": created_at,
        "tags": tags_with_hash,
        "source": "alpha-recall-restoration",
    }

    # Format embedding as PostgreSQL vector
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

    cursor.execute(
        """
        INSERT INTO alpha.memories (content, embedding, metadata)
        VALUES (%s, %s::vector, %s)
        RETURNING id
        """,
        (content, embedding_str, json.dumps(metadata))
    )

    result = cursor.fetchone()
    return result[0] if result else None


def main():
    parser = argparse.ArgumentParser(description="Restore Alpha memories from Redis dump")
    parser.add_argument("--redis-host", default="localhost", help="Redis host")
    parser.add_argument("--redis-port", type=int, default=6379, help="Redis port")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually insert, just show what would happen")
    args = parser.parse_args()

    # Connect to Redis
    print(f"Connecting to Redis at {args.redis_host}:{args.redis_port}...")
    r = redis.Redis(host=args.redis_host, port=args.redis_port, db=0)
    r.ping()
    print("Connected to Redis!")

    # Connect to Pond
    print(f"Connecting to Pond database...")
    conn = psycopg2.connect(POND_DB_URL)
    cursor = conn.cursor()
    print("Connected to Pond!")

    # Test Ollama
    print("Testing Ollama connection...")
    test_embedding = get_embedding("test")
    print(f"Ollama ready! Embedding dimension: {len(test_embedding)}")

    # Extract memories
    print("\nExtracting memories from Redis...")
    memories = extract_memories_from_redis(r)
    print(f"Extracted {len(memories)} memories")

    # Sort by date
    memories.sort(key=lambda m: m.get("created_at") or "")

    # Process each memory
    imported = 0
    skipped = 0
    errors = 0

    for i, memory in enumerate(memories, 1):
        title = memory["title"]
        created_at = memory["created_at"]
        content = memory["content"]
        tags = memory["tags"]

        print(f"\n[{i}/{len(memories)}] {title}")
        print(f"    Date: {created_at}")

        if args.dry_run:
            print(f"    [DRY RUN] Would import")
            imported += 1
            continue

        # Check for duplicates
        if memory_exists(cursor, content):
            print(f"    Skipped (already exists)")
            skipped += 1
            continue

        try:
            # Get embedding
            embedding = get_embedding(content)

            # Insert into Pond
            memory_id = insert_memory(cursor, content, embedding, created_at, tags)
            conn.commit()

            print(f"    Imported as memory #{memory_id}")
            imported += 1

        except Exception as e:
            print(f"    Error: {e}")
            conn.rollback()
            errors += 1

    # Summary
    print(f"\n{'='*50}")
    print(f"RESTORATION COMPLETE")
    print(f"{'='*50}")
    print(f"Total memories found: {len(memories)}")
    print(f"Successfully imported: {imported}")
    print(f"Skipped (duplicates): {skipped}")
    print(f"Errors: {errors}")

    if memories:
        dates = [m.get("created_at", "")[:10] for m in memories if m.get("created_at")]
        if dates:
            print(f"Date range: {min(dates)} to {max(dates)}")

    cursor.close()
    conn.close()
    r.close()


if __name__ == "__main__":
    main()
