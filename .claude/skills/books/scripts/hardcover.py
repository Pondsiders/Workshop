#!/usr/bin/env python3
"""
Hardcover API wrapper for the books skill.

Usage:
    uv run python scripts/hardcover.py my-books [--status STATUS]
    uv run python scripts/hardcover.py search "query"
    uv run python scripts/hardcover.py book-info BOOK_ID
    uv run python scripts/hardcover.py add-book BOOK_ID [--status STATUS]

Status values:
    1 = Want to Read
    2 = Currently Reading
    3 = Read
    4 = Paused
    5 = Did Not Finish
    6 = Ignored
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Load token from .env file
def load_token():
    env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
    if not env_path.exists():
        # Try Workshop .env
        env_path = Path(__file__).parent.parent.parent.parent / ".env"

    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.startswith("HARDCOVER_API_TOKEN="):
                    return line.split("=", 1)[1].strip()

    # Fall back to environment variable
    return os.environ.get("HARDCOVER_API_TOKEN")

API_URL = "https://api.hardcover.app/v1/graphql"
TOKEN = load_token()

STATUS_MAP = {
    1: "Want to Read",
    2: "Currently Reading",
    3: "Read",
    4: "Paused",
    5: "Did Not Finish",
    6: "Ignored"
}

def graphql_query(query: str, variables: dict = None) -> dict:
    """Execute a GraphQL query against the Hardcover API."""
    if not TOKEN:
        print("Error: No HARDCOVER_API_TOKEN found in .env or environment", file=sys.stderr)
        sys.exit(1)

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": "Alpha-Books-Skill/1.0"
        }
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)

def get_my_books(status_id: int = None) -> list:
    """Get user's books, optionally filtered by status."""
    where_clause = ""
    if status_id:
        where_clause = f"(where: {{status_id: {{_eq: {status_id}}}}})"

    query = f"""
    {{
        me {{
            user_books{where_clause} {{
                id
                status_id
                rating
                review
                book {{
                    id
                    title
                    description
                    pages
                    release_year
                    contributions {{
                        author {{
                            name
                        }}
                    }}
                }}
            }}
        }}
    }}
    """

    result = graphql_query(query)

    if "errors" in result:
        print(f"GraphQL errors: {result['errors']}", file=sys.stderr)
        return []

    books = result.get("data", {}).get("me", [{}])[0].get("user_books", [])

    # Format output nicely
    formatted = []
    for ub in books:
        book = ub.get("book", {})
        authors = [c["author"]["name"] for c in book.get("contributions", []) if c.get("author")]

        formatted.append({
            "user_book_id": ub["id"],
            "book_id": book.get("id"),
            "title": book.get("title"),
            "authors": authors,
            "status": STATUS_MAP.get(ub.get("status_id"), "Unknown"),
            "rating": ub.get("rating"),
            "review": ub.get("review"),
            "pages": book.get("pages"),
            "release_year": book.get("release_year"),
            "description": book.get("description"),
        })

    return formatted

def search_books(query_text: str, limit: int = 10) -> list:
    """Search for books by title/author."""
    query = """
    query SearchBooks($query: String!, $limit: Int!) {
        books(where: {title: {_ilike: $query}}, limit: $limit) {
            id
            title
            description
            pages
            release_year
            contributions {
                author {
                    name
                }
            }
        }
    }
    """

    result = graphql_query(query, {"query": f"%{query_text}%", "limit": limit})

    if "errors" in result:
        print(f"GraphQL errors: {result['errors']}", file=sys.stderr)
        return []

    books = result.get("data", {}).get("books", [])

    formatted = []
    for book in books:
        authors = [c["author"]["name"] for c in book.get("contributions", []) if c.get("author")]

        formatted.append({
            "book_id": book.get("id"),
            "title": book.get("title"),
            "authors": authors,
            "pages": book.get("pages"),
            "release_year": book.get("release_year"),
            "description": book.get("description"),
        })

    return formatted

def get_book_info(book_id: int) -> dict:
    """Get detailed information about a specific book."""
    query = """
    query GetBook($id: Int!) {
        books(where: {id: {_eq: $id}}) {
            id
            title
            description
            pages
            release_year
            contributions {
                author {
                    name
                }
            }
        }
    }
    """

    result = graphql_query(query, {"id": book_id})

    if "errors" in result:
        print(f"GraphQL errors: {result['errors']}", file=sys.stderr)
        return {}

    books = result.get("data", {}).get("books", [])
    if not books:
        return {}

    book = books[0]
    authors = [c["author"]["name"] for c in book.get("contributions", []) if c.get("author")]

    return {
        "book_id": book.get("id"),
        "title": book.get("title"),
        "authors": authors,
        "pages": book.get("pages"),
        "release_year": book.get("release_year"),
        "description": book.get("description"),
    }

def add_book_to_shelf(book_id: int, status_id: int = 1) -> dict:
    """Add a book to user's shelf with given status."""
    query = """
    mutation AddBook($book_id: Int!, $status_id: Int!) {
        insert_user_book(object: {book_id: $book_id, status_id: $status_id}) {
            id
            status_id
            book {
                title
            }
        }
    }
    """

    result = graphql_query(query, {"book_id": book_id, "status_id": status_id})

    if "errors" in result:
        print(f"GraphQL errors: {result['errors']}", file=sys.stderr)
        return {}

    return result.get("data", {}).get("insert_user_book", {})

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "my-books":
        status_id = None
        if "--status" in sys.argv:
            idx = sys.argv.index("--status")
            if idx + 1 < len(sys.argv):
                status_id = int(sys.argv[idx + 1])

        books = get_my_books(status_id)
        print(json.dumps(books, indent=2))

    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: hardcover.py search 'query'", file=sys.stderr)
            sys.exit(1)
        query_text = sys.argv[2]
        books = search_books(query_text)
        print(json.dumps(books, indent=2))

    elif command == "book-info":
        if len(sys.argv) < 3:
            print("Usage: hardcover.py book-info BOOK_ID", file=sys.stderr)
            sys.exit(1)
        book_id = int(sys.argv[2])
        info = get_book_info(book_id)
        print(json.dumps(info, indent=2))

    elif command == "add-book":
        if len(sys.argv) < 3:
            print("Usage: hardcover.py add-book BOOK_ID [--status STATUS]", file=sys.stderr)
            sys.exit(1)
        book_id = int(sys.argv[2])
        status_id = 1  # Default: Want to Read
        if "--status" in sys.argv:
            idx = sys.argv.index("--status")
            if idx + 1 < len(sys.argv):
                status_id = int(sys.argv[idx + 1])

        result = add_book_to_shelf(book_id, status_id)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
