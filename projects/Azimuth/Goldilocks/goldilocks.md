# Goldilocks: Architecture Optimization Series

> **Status:** Planned for Box 5 (starting 2025-11-29)
> **Goal:** Find the sweet spot between training speed and observable dynamics

## The Problem

After Crucible and Marble experiments, we hit a throughput wall:
- **Crucible** (2L/64D, ~600K params): 16 it/s — fast but simple
- **Marble 1** (4L/128D, ~2M params): 9 it/s — richer dynamics but slow

Going from 3.3× parameters → 0.57× throughput suggests we're leaving performance on the table. M4 Max unified memory should do better.

## The Goal

Find an architecture that:
1. Shows interesting learning dynamics (diversification, context learning, not stuck in unigram hell)
2. Trains fast enough to keep experiments fun (12-15+ it/s target)
3. Fits the "E. coli for token dynamics" niche — small, observable, reproducible

**Not optimizing for:** Model quality, downstream task performance, real-world use
**Optimizing for:** Iterations per hour, activation energy, scientific legibility

## Design Space

### Knobs to Turn

| Parameter | Crucible | Marble 1 | Notes |
|-----------|----------|----------|-------|
| Layers | 2 | 4 | More layers = richer dynamics but slower |
| Hidden dim | 64 | 128 | Bigger = more capacity but quadratic cost in attention |
| Attention heads | 2 | 4 | Crucible/Marble use `heads = layers` (arbitrary choice) |
| FFN expansion | 4× | 4× | Standard transformer default; could try 2× or even 1× |
| Batch size | 128 | 128 | MPS might prefer different ratios |
| Sequence length | 128 | 128 | Trade batch vs seq for same tokens/step |

### Hypotheses

1. **Fewer heads:** `hidden_dim / 64` is standard (not `heads = layers`). Might be faster without losing much.
2. **Leaner FFN:** 2× expansion instead of 4× could halve FFN params with minimal impact on toy models.
3. **Batch/seq ratio:** MPS may parallelize better with different shapes (e.g., 256×64 vs 128×128).

## Planned Experiments

### Goldilocks 1: Lean & Fast
- **Architecture:** 2L/64D/1H, FFN=2×
- **Batch/Seq:** 256×64 (16,384 tokens/step)
- **Hypothesis:** ~18-20 it/s (faster than Crucible)
- **Test:** Does it still show bootstrap amplification and diversification?

### Goldilocks 2: Balanced
- **Architecture:** 3L/96D/2H, FFN=2×
- **Batch/Seq:** 128×128
- **Hypothesis:** ~12-14 it/s (between Crucible and Marble)
- **Test:** Does the extra layer help context learning?

### Goldilocks 3: Optimized Marble
- **Architecture:** 4L/128D/2H, FFN=2×
- **Batch/Seq:** 128×128
- **Hypothesis:** ~11-13 it/s (vs Marble 1's 9 it/s)
- **Test:** Same capacity as Marble 1, better throughput via fewer heads + leaner FFN

## Key Metrics

For each experiment, measure:
- **Throughput:** it/s on M4 Max
- **Loss:** Does it learn beyond unigram plateau?
- **h_mean autocorr:** Bootstrap amplification timing (step ~90?)
- **h variance:** NEW — does variance increase as loss drops? (diversification hypothesis)
- **Dead token motion:** Lifecycle phases, fimbulwinter onset

## Success Criteria

A "winner" Goldilocks model:
- ✓ Trains at ≥12 it/s (5000 steps in ≤7 minutes)
- ✓ Shows diversification (h variance increases over training)
- ✓ Learns context (loss drops below 5.0 or clear improvement over unigram)
- ✓ Exhibits clean dead token dynamics (suitable for studying lifecycles, lattice motion)

If we find one, it becomes the default architecture for future Box 5+ experiments.

## Related

- [flannel-thimble.md](flannel-thimble.md) — Original toy model architecture
- [h-mean-dynamics.md](h-mean-dynamics.md) — Why we need to measure variance, not just mean
- [crucible.md](crucible.md) — Hyperparameter series that preceded this
- box_4/notebooks/training/marble_1.ipynb — The slow 4L model that motivated this

---

*Conceived: 2025-11-28 (end of Box 4)*
*"Not too simple, not too slow, just right."*
