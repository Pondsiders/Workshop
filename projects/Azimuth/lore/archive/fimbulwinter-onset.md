# Fimbulwinter Onset: Hyperparameter Effects

**Status:** Observed, hypothesis needs testing

## The Observation

Freeze timing varies dramatically with hyperparameters:

| Experiment | lr | weight_decay | Last Motion | Fimbulwinter Duration |
|------------|-----|--------------|-------------|----------------------|
| Thimble 7 | 1e-3 | 0.0 | ~3200 | ~800 steps |
| Thimble 8 | 3e-4 | 0.1 | ~9400 | ~600 steps |
| Thimble 9 | 3e-4 | 0.1 | 9432 | 568 steps |
| Crucible 1 | 1e-3 | 0.0 | 2509 | 2491 steps |

Thimble 8/9 freeze ~3x later than Thimble 7/Crucible 1.

## Working Hypothesis

**Learning rate is the primary driver; weight decay is secondary.**

Reasoning:
- Weight decay at Fimbulwinter is deterministic: `wd * W`, applied uniformly
- No batch-dependent randomness in the weight decay term
- Gradient noise is the stochastic driver—depends on which tokens appear in each batch
- Higher lr amplifies gradient kicks by the same factor (3.3x for 1e-3 vs 3e-4)
- Larger kicks = more chance to jostle a nearly-frozen token back into motion
- Therefore: higher lr = longer thermal tail = later freeze

Weight decay may affect *where* tokens drift during cooling (the attractor geometry), but probably not *when* they freeze.

## To Investigate

1. **Isolate lr effect:** Run with lr=1e-3, wd=0.1 — does it freeze early like Crucible 1?
2. **Isolate wd effect:** Run with lr=3e-4, wd=0.0 — does it freeze late like Thimble 8/9?
3. **Gradient noise measurement:** Can we quantify the per-token gradient variance over batches?

## Related

- [flannel-thimble.md](flannel-thimble.md) — The mini-models used for these experiments
- Crucible series — Designed for clean lifecycle capture

---

*First observed: November 25, 2025*
*Crucible 1 provided definitive confirmation of fast-freeze regime*
