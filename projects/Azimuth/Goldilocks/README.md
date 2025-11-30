# Operation Goldilocks

> *Not too simple, not too slow, just right.*

**Status: ✓ Complete** (November 30, 2025)

## What Is This?

A tiny transformer optimized for studying token dynamics—small enough to train in minutes, fast enough to iterate on, rich enough to show the phenomena we care about. Our "E. coli" for embedding research.

We optimized for **scientific utility**, not model quality.

---

## The Reference Model

Use `goldilocks.ipynb` as your starting point for experiments. It's a locked-down template with all the standard parameters.

| Property | Value |
|----------|-------|
| Layers | 4 |
| Hidden dim | 128 |
| Heads | 2 |
| FFN | 256 (2×) |
| Parameters | ~1.05M |
| Batch size | 8 |
| Tokens/step | 1,024 |
| Frame rate | ~110 steps/sec |

**Why Rich?** All three candidates (Lean/Balanced/Rich) converged to the same final loss at similar frame rates. Bigger model = more dimensions = richer dynamics to observe = closer approximation to Qwen 3 4B behavior. Since capacity doesn't cost us speed, we take the biggest.

**Recording budget:** W + last-layer h at every step for 10K steps ≈ 23.5 GB (fits under 24 GB HDF5 streaming limit).

---

## Corpus & Tokenizer ✓

**Status: Complete** (see `01_corpora.ipynb` and `02_tokenizer.ipynb`)

### Corpora

We use [CulturaX](https://huggingface.co/datasets/uonlp/CulturaX)—6.3 trillion tokens across 167 languages, heavily deduplicated.

| Corpus | Size | Composition | Purpose |
|--------|------|-------------|---------|
| Tokenizer corpus | 98 MB | 50% English, 50% Thai | Train the BPE tokenizer |
| Model corpus | 100 MB | 100% English (different text) | Train the model |

### Tokenizer

**Approach:** Train separately, merge programmatically.

| Component | Count |
|-----------|-------|
| English tokens | 2,048 |
| Thai tokens | 2,048 |
| Overlap (shared) | 108 |
| **Merged vocabulary** | **3,988** |

### The Magic Number

| Category | Total | Dead | Dead % |
|----------|-------|------|--------|
| Thai | 1,904 | 1,904 | **100%** |
| Latin | 1,913 | 0 | **0%** |
| Common | 170 | 9 | 5.3% |

**★ 1,914 dead tokens ★** — tokens that will never receive gradient signal during training.

---

## The Work Constant

From `03_efficiency_cliff.ipynb`: batch size and model size trade off to maintain constant GPU utilization.

```
work_constant = params × batch_size × seq_len ≈ 1.27B
```

| Architecture | Params | Optimal Batch | Work |
|--------------|--------|---------------|------|
| Lean | 330K | 32 | 1.35B |
| Balanced | 618K | 16 | 1.27B |
| Rich | 1.05M | 8 | 1.08B |

All three run at ~110 steps/sec despite different sizes—the work constant holds (within ~20%).

---

## Notebooks

| # | Notebook | Description |
|---|----------|-------------|
| 01 | `01_corpora.ipynb` | Download CulturaX, prepare corpora |
| 02 | `02_tokenizer.ipynb` | Train bilingual BPE, census dead tokens |
| 03 | `03_efficiency_cliff.ipynb` | Batch size benchmark, work constant derivation |
| 04 | `04_architecture_search.ipynb` | Compare Lean/Balanced/Rich |
| 05 | `05_validation.ipynb` | Validate fimbulwinter dynamics |
| — | `goldilocks.ipynb` | **Reference template** for new experiments |

---

## Hardware & Budgets

See `lore/rules.md` for full constraints.

**M4 Pro:** 20-core GPU, 48 GB RAM

| Budget | Limit |
|--------|-------|
| Instantaneous RAM | 24 GB |
| Single safetensors file | 12 GB |
| HDF5 streaming experiment | 24 GB |

---

*Conceived: November 28, 2025*
*Completed: November 30, 2025*
