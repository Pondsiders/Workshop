# Azimuth Rules

> **Last updated:** 2025-11-30

Constraints and guidelines for Azimuth experiments.

---

## Hardware

**Machine:** M4 Pro MacBook Pro, 20-core GPU, 48 GB unified RAM

---

## Memory Budget

| Constraint | Limit | Notes |
|------------|-------|-------|
| Instantaneous RAM | **24 GB** | Don't hog the whole machine. If you're pushing close to this, ask first. |
| Single safetensors file | **12 GB** | These load entirely into RAM |
| HDF5 streaming experiment | **24 GB** | Stream to disk in chunks, don't load all at once |

For anything exceeding these limits, check with Jeffery first.

---

## Recording Strategy

**What we typically care about over long runs:**

| Tensor | Why | Resolution |
|--------|-----|------------|
| W[t] | The movie—watching embeddings move | Every step |
| h[batch, seq, t] (last layer) | Correlate model predictions with W motion | Every step |

**What we DON'T need at high resolution:**

| Tensor | Why not |
|--------|---------|
| m, v (Adam state) | Converges quickly to m/√v ≈ 1; interesting only in first ~100 steps |
| grads | Useful for spot-checks, not continuous recording |
| logits | Too big, not that informative |

**Rule of thumb:** For a 10K step run, budget for W + last-layer h every step. That's ~2.5 MB/step for Rich model, ~25 GB total—fits in HDF5 budget.

---

## bf16 Training Protocol

**Why bf16:** Qwen 3 4B trained in bfloat16. The bf16 quantization floor is what causes fimbulwinter—gradients below ULP round to zero, freezing dead tokens. To replicate this phenomenon, we need the same quantization behavior.

**How it works on MPS:** Apple Silicon doesn't have native bf16 compute. PyTorch on MPS upcasts bf16 tensors to float32 for computation, then downcasts back to bf16 for storage. This means:

- **Compute:** Identical to float32 (no precision loss during forward/backward)
- **Storage:** bf16 quantization applied after each optimizer step
- **Speed:** Same or slightly slower than float32 (cast overhead)
- **Dynamics:** The bf16 ULP floor IS enforced on weights, which is what matters

**The protocol:**

```python
# Create model in bf16
model = GPT(...).to(device).to(torch.bfloat16)

# Optimizer state stays float32 (AdamW default behavior)
optimizer = torch.optim.AdamW(model.parameters(), lr=...)

# Training loop is unchanged—PyTorch handles the casts
```

**What this gives us:**
- Gradients computed in float32 (full precision)
- Optimizer state (m, v) accumulated in float32 (no drift)
- Weight updates applied, then quantized to bf16
- Dead tokens freeze when updates fall below bf16 ULP (~1e-3 at typical magnitudes)

**Note:** The Goldilocks reference numbers below were measured in float32. They should hold for bf16 since MPS does the same math—but verify empirically if in doubt.

---

## Goldilocks Reference Numbers

From notebook 03-04 experiments (2025-11-30):

| Architecture | Params | Optimal Batch | Tokens/Step | Steps/sec |
|--------------|--------|---------------|-------------|-----------|
| Lean | 330K | 32 | 4,096 | ~104 |
| Balanced | 618K | 16 | 2,048 | ~113 |
| Rich | 1.05M | 8 | 1,024 | ~110 |

**Work constant:** ~1.27B (params × tokens_per_step)

**Recording budget (Rich, 10K steps):**
```
W:  1.05M × 2 bytes × 10K = 21 GB
h:  8 × 128 × 128 × 2 bytes × 10K = 2.5 GB
────────────────────────────────────────
Total: ~23.5 GB ✓ (fits HDF5 budget)
```

---

*These rules exist to keep experiments tractable. If a rule doesn't serve the science, revisit the rule.*
