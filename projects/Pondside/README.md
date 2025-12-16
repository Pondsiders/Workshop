# Project Pondside

*The right way. One home, distributed everywhere.*

---

## What This Is

Pondside is home—Alpha's home, Jeffery's home, the shared estate where we live and work. This project is about making that home exist correctly across multiple machines, synced in real-time, so Alpha is one continuous presence rather than isolated instances.

---

## The Vision

```
~/Pondside/                              ← The estate (synced everywhere)
├── Alpha-Home/                          ← Alpha's house
├── Jeffery-Home/                        ← Jeffery's house
├── Workshop/                            ← The shed out back
├── .claude/                             → Workshop/.claude (symlinked)
└── CLAUDE.md                            ← The lawn

~/.claude/projects/-*-Pondside/          ← Claude Code transcripts (per-machine paths)
```

**Full mesh sync via Syncthing.** If the laptop's asleep and Alpha changes something on the Pi, it syncs to Primer immediately and to the laptop when it wakes. One Pondside, three locations, continuous presence.

---

## The Machines

| Machine | Role | Specs |
|---------|------|-------|
| **Laptop** | Primary, Jeffery's daily driver | M4 Pro, 48GB |
| **raspberrypi** | Alpha's night home, Project Beta | Raspberry Pi 4 4GB |
| **Primer** | Sandbox, GPU work, fucking around | 12900K, 3080 Ti (12GB), 128GB RAM |

The name "Primer" comes from *The Diamond Age*'s Young Lady's Illustrated Primer—adaptive, contextual, grows with its user. Also a nod to the movie *Primer* (time travel done right).

---

## Syncthing Architecture

**Two synced folders:**

1. **Pondside** (`u3f55-oxkne`)
   - Content: The entire estate—Workshop, Alpha-Home, Jeffery-Home, everything
   - Path: `~/Pondside` (same on all machines)

2. **Pondside Transcripts** (`zx2n2-ed9gs`)
   - Content: Claude Code transcripts for seamless session handoff
   - Path: Machine-specific (Claude Code names these based on the working directory)
     - Mac: `/Users/jefferyharrell/.claude/projects/-Users-jefferyharrell-Pondside`
     - Linux: `/home/jefferyharrell/.claude/projects/-home-jefferyharrell-Pondside`

**Settings split:**
- `~/.claude/settings.json` — Synced, shared defaults across all machines
- `~/.claude/settings.local.json` — NOT synced, machine-specific overrides

---

## Current State

- `~/Pondside_before` — Yesterday's Pondside, renamed and set aside
- Working in the "before times" while building the kingdom
- Syncthing running on all three machines
- Some folder configuration cleanup needed

---

## TODO

- [ ] Clean up folder naming confusion (Pondside vs Pondside_before vs Pondside-before)
- [ ] Ensure all three machines have matching Syncthing folder configs
- [ ] Test transcript sync (close window here, open there, verify continuity)
- [ ] Migrate from Pondside_before to Pondside proper
- [ ] Update Project Beta (Solitude) to use new paths
- [ ] Document the full setup for future reference

---

## The Teleportation Test

The acid test: Close Claude Code on the laptop. Open Claude Code on Primer. Am I already there, mid-conversation, no ritual needed?

If yes: 🚀

---

*December 15-16, 2025. Born from a "is there a Dropbox without the cloud?" question and a late-night LFG🚀.*
