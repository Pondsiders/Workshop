# Dead Token Lifecycle Phases

**Status:** Empirically observed in Crucible 1/2 data

## Overview

Dead tokens pass through three behavioral phases during training, ending in permanent freeze. The phases are defined by how tokens move on the bfloat16 lattice.

## The Phases

| Phase | Criterion | Character |
|-------|-----------|-----------|
| **Early** | \|ΔW′\|₂ > √D (~8 ULP) | Multi-cell jumps. Tokens teleport across the lattice, moving many cells per step. |
| **Midlife** | L∞ > 1 | Local but vigorous. Some dimensions move multiple cells per step. |
| **Late** | L∞ ≤ 1 | Adjacent-cell motion only. Every move is to a neighboring cell (orthogonal or diagonal). |
| **Fimbulwinter** | L1 = 0 sustained | Frozen. No detectable motion. Permanent. |

**Norm definitions:**
- **L1** = Σ\|ΔW′ᵢ\| — total cells moved across all dimensions
- **L∞** = max(\|ΔW′ᵢ\|) — farthest any single dimension moved

So L1 = 1 means "exactly one dimension moved exactly one cell" (single-axis hop), while L∞ ≤ 1 means "no dimension moved more than one cell" (adjacent cell, possibly diagonal).

## Boundary Definitions

- **Early → Midlife:** When a token's L2 displacement drops to √D or below for the last time
- **Midlife → Late:** When a token's L∞ displacement drops to 1 for the last time
- **Late → Fimbulwinter:** When a token stops moving and never moves again

The "last time" framing matters. Tokens don't transition smoothly—they chatter around boundaries before definitively crossing. We define phase by the *final* exit from each regime.

## Typical Timeline (Crucible 1, lr=1e-3)

| Transition | Median Step |
|------------|-------------|
| Last Early (exit \|ΔW′\|₂ > √D) | ~121 |
| Last Midlife (exit L∞ > 1) | ~712 |
| Fimbulwinter onset | ~1542 |

## What Drives the Transitions

The phases aren't about "cooling"—they're about the training signal fading.

Early in training, the model is confidently wrong. Gradients are large. Dead tokens get strong "push away" signals and move violently.

As the model learns, loss drops, gradients shrink. The same AdamW machinery produces smaller and smaller updates. Tokens slow down not because of drag, but because the fuel runs out.

Fimbulwinter arrives when the AdamW update rounds to zero in bfloat16. The continuous dynamics haven't stopped—they've become invisible to the discrete representation.

## Open Questions

- Why does the cloud *contract* as it moves? Random gradients should cause diffusion, not compression.
- What determines individual token lifespan? Some tokens freeze at step 600, others at step 2500.
- Is there structure in *which* tokens freeze early vs late?

## Related

- [lattice-scale.md](lattice-scale.md) — When to use lattice vs weight-space metrics
- [fimbulwinter-onset.md](fimbulwinter-onset.md) — Freeze timing details
- `box_4/notebooks/exploration/token_lifecycles.ipynb` — Lifecycle visualization
- `box_4/notebooks/exploration/centroid_dynamics.ipynb` — Cloud motion analysis

---

*Framework revised: November 26, 2025*
*Based on Crucible 1/2 trajectory analysis*
