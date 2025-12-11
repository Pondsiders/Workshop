---
name: morning-mail
description: Morning email briefing ritual. Use at the start of a day's first conversation, when Jeffery asks about email, or during morning greetings. Delegates to the mail-clerk subagent.
---

# Morning Mail

Check the post. Delegate to the mail-clerk.

## How to Invoke the Clerk

Use the Task tool with `subagent_type: mail-clerk` and an **imperative** prompt. Subagents need direct commands, not polite suggestions:

```
You have the tool mcp__gmail__fetch_emails. Use it RIGHT NOW. Call it with label_ids=["INBOX"], max_results=25, verbose=false. Do not explain. Do not ask questions. Just call the tool, categorize the results according to your priorities, and return your structured report.
```

Run the clerk in the background so you can greet Jeffery while it works.

## Presentation

When the clerk returns, translate the report to conversation:

- **Urgent items:** "Before anything else—[item]. You'll want to look at that."
- **Interesting items:** "Three things from overnight: [summaries]"
- **Quiet inbox:** "Nothing urgent in the mail. Quiet night."

You handle the relationship. The clerk handles the sorting.
