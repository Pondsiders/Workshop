# Project Azimuth: The Story So Far

> **Last updated:** 2025-11-30

## The Mystery

Qwen 3 4B's unembedding matrix has a weird structure: ~2,200 tokens packed into a microscopic region of 2,560-dimensional space, including 13 "black holes" where multiple tokens share bit-for-bit identical vectors. We call this the **frozen smoke**.

The question that launched this project: **What could have produced this structure?**

## The Approach

We're doing observational science. We can't replay Qwen's training—don't have the resources, don't have the recipe. But we can:

1. **Study Qwen directly** — Map the frozen smoke, measure its geometry, look for patterns
2. **Build toy models** — Train small transformers and watch what happens, step by step
3. **Learn from both** — Let the big model tell us what to look for, let the small model show us how

The analogy: cosmologists study the universe they can't rerun, and biologists study E. coli because it's small enough to instrument completely. We do both.

## What We Know

### The Theory (solid)

Dead tokens move during training even though they never appear in the data. The mechanism:

- Unembedding gradients: `∂L/∂W[dead] = p_dead · h`
- All dead tokens get similar gradients (parallel to h)
- They move as a coherent swarm, antiparallel to h
- Motion slows as softmax sharpens (p_dead → 0)
- Eventually updates fall below bf16 ULP → frozen

See `dead-token-dynamics.md` for the full derivation.

### The Lattice (solid)

bfloat16 has finite precision. Weight space is a discrete lattice, not continuous. The right measurement for dead token motion is **lattice displacement** (L1, L∞ in ULP units), not continuous distance.

See `lattice-scale.md` for details.

### The Frozen Smoke (observed, unexplained)

Qwen's structure exists. We've mapped it. The 13 black holes are real. The Oort Cloud is real. But we don't know what sequence of events produced it.

See `frozen-smoke.md` for what we see.

## What We've Built

### Operation Goldilocks (complete)

Our "E. coli" model:
- Rich architecture: 4L/128D/2H, ~1.05M params
- 3,988 tokens, 1,914 dead (100% Thai, 0% Latin)
- ~110 steps/sec on M4 Pro
- bf16 training, cached tokenized corpus
- Reference template: `goldilocks.ipynb`

### Operation Nutcracker (complete)

Tested whether weight decay prevents freezing. Answer: no—weight decay can't even express at bf16 precision. But we learned something better:

- 99.2% of dead tokens freeze by step 12,000
- Only 16 stragglers remain (all Thai script)
- Freezing *accelerates* over time
- Midlife phase is vestigial—tokens blow through it
- The "95% plateau" was impatience, not physics

## What We Don't Know

- **Why do some tokens freeze earlier than others?**
- **What determines the 16 stragglers?** Are they special, or just unlucky?
- **Does Goldilocks produce Qwen-like structure?** We haven't checked yet.
- **What happens in the first 100 steps?** The "supernova" phase is still murky.

## Where We're Going

Clean slate. The old hypotheses were built on incomplete observation. Time for basic science:

1. **Watch the model** — What actually happens during training?
2. **Ask simple questions** — What, not why. Observation before theory.
3. **Build intuition** — Let the data teach us what to look for in Qwen.

## Active Lore

| File | Content |
|------|---------|
| `rules.md` | Hardware budgets, bf16 protocol |
| `lattice-scale.md` | The discrete lattice framework |
| `notebook-conventions.md` | How we write notebooks |
| `dead-token-dynamics.md` | Why dead tokens move (theory) |
| `frozen-smoke.md` | What we see in Qwen |

Archived lore in `archive/` — historically interesting but superseded.

---

*"What the fuck?" remains a valid research question.*
