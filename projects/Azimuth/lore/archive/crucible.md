# Crucible Series

**Purpose:** Clean lifecycle capture of dead token dynamics with fast-freeze hyperparameters.

## Etymology

From Latin *crucibulum* (melting pot), related to *crux* (cross)—same root as "crucial" and "cruciform." A small vessel where materials transform under heat.

## Design Philosophy

Crucible addresses limitations discovered in the Thimble series:

1. **Fast freezing:** lr=1e-3, wd=0.0 produces freeze ~2500 steps (vs Thimble 8/9's ~9400)
2. **Long Fimbulwinter:** 5000 steps gives ~2500 steps of confirmed frozen state
3. **Live ΔW′ computation:** Lattice displacement calculated during training, not post-hoc
4. **Per-token freeze tracking:** `last_motion_step` records when each token stopped moving

## Hyperparameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| lr | 1e-3 | Matches Thimble 7's fast-freeze regime |
| weight_decay | 0.0 | Removes confounding variable |
| steps | 5000 | Enough for full lifecycle + long Fimbulwinter |
| motion_threshold | 0.1 ULP | Below this, token counts as "frozen" |

## Data Captured

Each Crucible run saves:

- `W[t]` — Embedding trajectory (bfloat16, stored as uint16)
- `delta_W_prime[t]` — Lattice displacement (float32)
- `centroid[t]` — Mean position of dead token cloud (float32)
- `loss[t]` — Training loss curve (float32)
- `last_motion_step[token]` — Per-token freeze timing (int32)

## Experiments

| Name | Steps | Notes |
|------|-------|-------|
| Crucible 1 | 5000 | Baseline. Last motion step 2509, Fimbulwinter 2491 steps. |

## Relationship to Thimble

Thimble was exploratory—trying different configurations, learning what matters. Crucible is refined—hyperparameters chosen deliberately for clean observation of the full thermal lifecycle.

## Related

- [flannel-thimble.md](flannel-thimble.md) — The earlier experimental series
- [fimbulwinter-onset.md](fimbulwinter-onset.md) — Why these hyperparameters freeze faster

---

*Series started: November 25, 2025*
