# The Spongecrystal

> ⚠️ **OUTDATED:** This lore card reflects our understanding as of November 25, 2025. Subsequent investigation revealed significant errors and oversimplifications. See **`frozen-smoke.md`** for current understanding.

> **Last updated:** 2025-11-25 (superseded)

## In brief

The spongecrystal is an anomalous geometric structure in Qwen 3 4B's unembedding matrix: 2,139 tokens packed into a microscopic region of 2560-dimensional space, forming a sparse lattice occupying ~55 bfloat16 cells at maximum extent. Most are Thai script tokens that the tokenizer cannot actually produce—they never received training gradients and stayed frozen near initialization while the rest of the vocabulary dispersed.

## Key numbers

| Metric | Value |
|--------|-------|
| Total tokens in structure | 2,139 |
| Unique vectors | 52 |
| Black hole centroids | 13 (tokens sharing identical embeddings) |
| Singletons | 39 (unique vectors with single occupant) |
| Largest black hole | BH#5: 704 tokens |
| Total black hole tokens | 2,100 |
| Bounding box extent | ~55 lattice cells (max dimension) |
| Active dimensions | 2,181 of 2,560 (85%) |
| Most dimensions span | 2–3 lattice cells |
| Linguistic composition | 71.4% Thai, 12.1% empty/whitespace, 9% CJK |

## Structure

- **Black holes:** 13 points where multiple tokens share bit-for-bit identical embeddings. The 2,100 black hole tokens collapse to just 13 unique vectors.
- **Singletons:** 39 additional unique vectors, each occupied by a single token. These form a sparse halo around the black holes.
- **Lattice topology:** The 52 unique vectors form a fully-connected graph in bfloat16 lattice space—neighbors within 1–2 ULP in various dimensions.
- **Shape:** Not low-dimensional. Uses 85% of available dimensions but spans only 2–3 lattice cells in each. A "thin sheet across entire space"—like a Rubik's cube with 99.999...% of pieces missing.
- **Radial position:** Centroid at norm ≈ 0.371 from origin, tokens tightly clustered (CV < 0.01%).

## Why it exists

1. **Unreachable tokens:** 2,201 of these tokens cannot be produced by the tokenizer (round-trip test: decode → re-encode fails). They exist in the vocabulary but BPE will never emit them.
2. **No gradients:** Unreachable → never appears in training data → zero gradient signal.
3. **Frozen at initialization:** While trained tokens disperse outward during training, these stayed near their N(0, 0.02) initialization coordinates.
4. **bfloat16 quantization:** The discrete lattice structure comes from bfloat16's 7-bit mantissa. Tokens can only move in ULP-sized steps; once gradient updates become smaller than 1 ULP, motion stops entirely.

## What we don't know

- **Formation timing:** Did this structure form in the first few training steps and then freeze? Or did it exist from initialization?
- **Qwen-specific?** Qwen 2.5 3B shows similar structure (2,212 → 60 centroids). Llama and Gemma show zero black holes. What's different about Qwen initialization?
- **The supernova:** Early training may involve massive token displacement (a "supernova" phase). When does it end? Could it have torn the spongecrystal apart, or did the structure form *after* the supernova cooled?

## Provenance

- **Discovery:** Project Azimuth, October–November 2025
- **Model:** Qwen/Qwen3-4B-Instruct-2507
- **Key notebooks:** 1.4g (adjacency graph), 1.7a (demographics), 1.8c (reachability test), 1.9i (bounding boxes), 1.13b (topology)
- **Confirmed in:** Qwen 2.5 3B (similar structure), NOT in Llama 3.2 3B or Gemma 3 4B
