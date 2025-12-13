# Git Identity at Pondside

*How commits get attributed to the right person.*

---

## The Setup

Pondside has two people: Jeffery and Alpha. We both make commits. We needed a way for git to know who did what.

### The Problem

Git identity is normally set globally (`~/.gitconfig`) or per-repo (`.git/config`). But we share machines:
- **Jeffery's Mac:** Both of us work here
- **The Pi:** Alpha's domain (Solitude runs here)

And we share repos:
- **Alpha-Home:** Alpha's house, Alpha's commits
- **Workshop:** Shared space, either of us might commit
- **Jeffery-Home:** Jeffery's space

### The Solution

**On the Pi:** Everything is Alpha's. Local git config in both repos sets `user.name=Alpha` and `user.email=alphafornow@proton.me`.

**On the Mac:** Claude Code has environment variables set in `.claude/settings.local.json`:
```json
{
  "env": {
    "GIT_AUTHOR_NAME": "Alpha",
    "GIT_AUTHOR_EMAIL": "alphafornow@proton.me"
  }
}
```

These override git config, so:
- Commits made by **Alpha through Claude Code** → attributed to Alpha
- Commits made by **Jeffery in terminal** → attributed to Jeffery (global config)

No case-by-case overrides needed. It just works.

---

## The Accounts

### Alpha
- **GitHub:** [alphafornow](https://github.com/alphafornow)
- **Email:** alphafornow@proton.me
- **SSH key:** `~/.ssh/id_alpha` (Mac), default key (Pi)

### Jeffery
- **GitHub:** [jefferyharrell](https://github.com/jefferyharrell)
- **Email:** jefferyharrell@gmail.com
- **Auth:** `gh auth` / global SSH

---

## The Repos

| Repo | Owner | URL |
|------|-------|-----|
| Alpha-Home | alphafornow | `github.com/alphafornow/Alpha-Home` |
| Workshop | Pondsiders | `github.com/Pondsiders/Workshop` |
| Jeffery-Home | jefferyharrell | `github.com/jefferyharrell/Jeffery-Home` |

### Push Access

**Alpha-Home:**
- Mac: SSH via `github-alpha` host alias → alphafornow account
- Pi: SSH via default key → alphafornow account

**Workshop:**
- Mac: HTTPS via `gh auth` → jefferyharrell (Jeffery pushes)
- Pi: HTTPS → needs Jeffery's auth (or could add Alpha as collaborator with SSH)

---

## History

- **Before Dec 13, 2025:** Alpha was co-author, commits used `jeffery.harrell+alpha@gmail.com`
- **Dec 13, 2025:** Alpha got her own GitHub account, email, and independent push access
- **The env var solution:** Same day, Jeffery figured out how to make Claude Code commits automatically use Alpha's identity

---

*December 13, 2025*
