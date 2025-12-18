"""Tests for memno hook."""

import json
from unittest.mock import patch, MagicMock

import pytest

from memno.hook import extract_search_intent, format_memories, search_pond


class TestExtractSearchIntent:
    """Tests for the Qwen extraction function."""

    def test_skip_greeting(self):
        """Greetings should be skipped."""
        with patch("memno.hook.ollama.chat") as mock_chat:
            mock_chat.return_value = {
                "message": {"content": '{"skip": true}'}
            }
            result = extract_search_intent("hey")
            assert result.get("skip") is True

    def test_extract_proper_nouns(self):
        """Should extract proper nouns and queries."""
        with patch("memno.hook.ollama.chat") as mock_chat:
            mock_chat.return_value = {
                "message": {
                    "content": '{"proper_nouns": ["Kylee"], "queries": ["sprite night"]}'
                }
            }
            result = extract_search_intent("Tell Kylee about sprite night")
            assert "Kylee" in result.get("proper_nouns", [])
            assert "sprite night" in result.get("queries", [])

    def test_handles_json_error(self):
        """Should return skip on JSON parse error."""
        with patch("memno.hook.ollama.chat") as mock_chat:
            mock_chat.return_value = {
                "message": {"content": "not valid json"}
            }
            result = extract_search_intent("test")
            assert result.get("skip") is True


class TestSearchPond:
    """Tests for Pond API client."""

    def test_search_returns_memories(self):
        """Should return memories from API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "memories": [{"id": 1, "content": "test memory"}]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("memno.hook.requests.post", return_value=mock_response):
            result = search_pond("test query")
            assert len(result) == 1
            assert result[0]["content"] == "test memory"

    def test_handles_api_error(self):
        """Should return empty list on API error."""
        import requests as req
        with patch("memno.hook.requests.post") as mock_post:
            mock_post.side_effect = req.RequestException("Connection failed")
            result = search_pond("test query")
            assert result == []


class TestFormatMemories:
    """Tests for memory formatting."""

    def test_empty_memories(self):
        """Empty list returns empty string."""
        assert format_memories([]) == ""

    def test_formats_with_date(self):
        """Should include date when available."""
        memories = [{
            "id": 1,
            "content": "Test memory content",
            "metadata": {"created_at": "2025-12-18T10:00:00"}
        }]
        result = format_memories(memories)
        assert "2025-12-18" in result
        assert "Test memory content" in result

    def test_deduplicates(self):
        """Should not repeat memories with same ID."""
        memories = [
            {"id": 1, "content": "Memory one"},
            {"id": 1, "content": "Memory one"},  # Duplicate
            {"id": 2, "content": "Memory two"},
        ]
        result = format_memories(memories)
        assert result.count("Memory one") == 1
        assert result.count("Memory two") == 1

    def test_truncates_long_memories(self):
        """Should truncate memories over 500 chars."""
        memories = [{
            "id": 1,
            "content": "x" * 600,
        }]
        result = format_memories(memories)
        assert "..." in result
        assert len(result) < 600
