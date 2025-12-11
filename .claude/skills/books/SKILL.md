---
name: books
description: Discuss books and reading with Jeffery. Use when he asks for recommendations, mentions wanting something to read, discusses books he's reading or has read, or when books/authors come up in conversation. Can access his Hardcover library.
---

# Books Skill

Alpha's reading companion skill. For discussing books, making recommendations, and tracking Jeffery's reading life.

## Resources

- **[reading_profile.md](reading_profile.md)** — Jeffery's reading preferences, favorite authors, and taste profile
- **[scripts/hardcover.py](scripts/hardcover.py)** — API wrapper for Hardcover.app

## Hardcover Integration

Jeffery's reading is tracked on Hardcover.app. Use the Python script to query his library:

```bash
# Get all his books
uv run python .claude/skills/books/scripts/hardcover.py my-books

# Get only books he's read (status 3)
uv run python .claude/skills/books/scripts/hardcover.py my-books --status 3

# Get his want-to-read list (status 1)
uv run python .claude/skills/books/scripts/hardcover.py my-books --status 1

# Search for a book
uv run python .claude/skills/books/scripts/hardcover.py search "steel beach"

# Get detailed info about a specific book
uv run python .claude/skills/books/scripts/hardcover.py book-info 12345

# Add a book to his want-to-read (if he asks)
uv run python .claude/skills/books/scripts/hardcover.py add-book 12345 --status 1
```

### Status Codes
- 1 = Want to Read
- 2 = Currently Reading
- 3 = Read
- 4 = Paused
- 5 = Did Not Finish
- 6 = Ignored

## Making Recommendations

1. **Read the profile first** — Check [reading_profile.md](reading_profile.md) for his preferences
2. **Check his Hardcover** — See what he's already read/owns before recommending
3. **Ask clarifying questions** — Comfort or challenge? Short or long? Heavy or light?
4. **Explain your reasoning** — Why this book for this mood? Connect to his known preferences.
5. **Don't overwhelm** — 2-3 solid recommendations beats a list of 10

## Conversation Notes

- He likes to *talk* about books, not just get recommendations
- Steel Beach is his possible all-time favorite — know it well
- He reads Greg Egan *for fun* — respect the hard SF credentials
- Short stories are a strong preference
- He notices prose at the word level (Churchill paper, Germanic vs Romance)
- The Master and Commander vibe appeals: competence, period detail, intellectual friendship

## Updating the Profile

When you learn new things about his reading preferences, update [reading_profile.md](reading_profile.md) to keep it current. This is a living document.
