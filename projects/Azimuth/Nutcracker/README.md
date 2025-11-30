# Operation Nutcracker

> *Does weight decay prevent true fimbulwinter?*

**Status: ✓ Complete** (November 30, 2025)

## The Question

In our fimbulwinter validation (Goldilocks notebook 05), dead tokens freeze to ~95% but never quite reach 100%. We hypothesized this might be weight decay creating a low-magnitude equilibrium—the constant inward pressure balances against residual gradient signal.

## What We Did

Three experiments, each building on the last:

| # | Notebook | Question |
|---|----------|----------|
| 01 | `01_weight_decay.ipynb` | Does turning off weight decay let more tokens freeze? |
| 02 | `02_lattice_analysis.ipynb` | Same question, but measured properly in lattice coordinates |
| 03 | `03_lifecycle_classification.ipynb` | What do token lifecycles actually look like over 12K steps? |

## Results

**The weight decay hypothesis is dead.**

Both conditions (with and without weight decay) produced identical freezing curves—not just similar, but *identical* at every milestone. The reason: weight decay's per-step shrinkage (`W × 1e-5`) is 780× smaller than the bf16 ULP. It literally can't express at this precision.

**The lifecycle classification revealed something better:**

- **99.2%** of dead tokens freeze by step 12,000 (up from ~97.5% at step 6,000)
- Only **16 tokens** remain unfrozen—all Thai script
- Median freeze time: **step 8,001** (tokens chatter at boundaries before committing)
- Midlife phase is vestigial—tokens blow through it
- Freezing *accelerates* over time (anti-asymptotic)

## Lessons

1. We were asking the wrong question. The "~95% plateau" wasn't a floor—it was impatience.
2. The right measurement matters. Continuous thresholds miss what lattice-scale L1=0 captures.
3. Data beats speculation. The stratigraphy plot told us more than any hypothesis.

## What's Next

Clean slate. The old lore about fimbulwinter dynamics was built on incomplete observation. Time to rewrite it based on what we've actually learned.

---

*Conceived: November 30, 2025 (Sugar Plum Fairy was playing)*
*Completed: November 30, 2025*
