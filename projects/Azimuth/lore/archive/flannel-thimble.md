# Flannel & Thimble Models

> **Last updated:** 2025-11-25

## In brief

Flannel and Thimble are minimal language models designed to simulate dead token dynamics in an observable, reproducible way. Training Qwen 3 4B from scratch is infeasible; these give us the same essential dynamics (tied weights, dead tokens, bfloat16 quantization) in a system small enough to instrument completely and run dozens of times.

## Why they exist

We want to understand how structures like the spongecrystal form during training. But we can't:
- Retrain Qwen 3 4B (too expensive)
- Access Qwen's training logs (proprietary)
- Know exactly what happened in the first 10,000 steps

Flannel/Thimble let us watch dead token dynamics unfold in real time, with complete instrumentation.

## Architecture

| Parameter | Value |
|-----------|-------|
| Vocabulary | 10,000 tokens |
| Dead tokens | ~3,699 (never appear in training data) |
| Hidden dimension | 64 |
| Layers | 2 |
| Attention heads | 2 |
| Embedding tying | Yes (E = W^T, like Qwen 3 4B) |
| Training data | FineWeb (English web text) |

## Training configuration

| Parameter | Value |
|-----------|-------|
| Optimizer | AdamW |
| β₁, β₂ | 0.9, 0.999 |
| ε | 1e-8 |
| Learning rate | 3e-4 |
| Weight decay | 0.1 |
| Precision | bfloat16 |

## Initialization

- **Embeddings:** N(0, 0.02) — standard transformer practice
- **Other weights:** PyTorch defaults

## What we record

Full embedding matrix **W** at every training step. Saved to `box_3/tensors/Flannel/` or `box_3/tensors/Thimble/`.

This lets us track:
- Individual token trajectories through 2560D space
- Dead token cloud geometry over time
- Lattice structure formation
- Phase transitions (supernova → cooling → freezing)

## Flannel vs Thimble

Both use the same architecture. The distinction is experimental:
- **Flannel:** Earlier experiments, various configurations
- **Thimble:** Later experiments with refined methodology

Key datasets:
- `thimble_7.h5`: 6,001 timesteps × 10,000 tokens × 64 dimensions (our primary training trajectory)

## Key findings so far

1. **Dead tokens move** — Even with zero direct gradients, dead tokens experience displacement during training (via tied weights and optimizer state)
2. **Early chaos** — First ~100-1000 steps show massive displacement (the "supernova")
3. **Gradual freezing** — Displacement decays as gradients shrink below bfloat16 ULP threshold
4. **No spongecrystal yet** — We haven't reproduced Qwen's exact structure; still investigating what initial conditions produce it

## Open questions

- What initialization produces spongecrystal-like structures?
- When exactly does the supernova end?
- Do dead tokens freeze simultaneously or progressively?
- What's the flux of live tokens through the dead token cloud?

## See also

- [spongecrystal.md](spongecrystal.md) — The structure we're trying to explain
- [data-storage.md](data-storage.md) — How training trajectories are stored (HDF5)
