# Operation Goldilocks

> *Not too simple, not too slow, just right.*

## What Is This?

We're searching for the ideal tiny transformer to use as our "E. coli for token dynamics"—a model small enough to train in minutes, fast enough to iterate on, but rich enough to show the phenomena we care about (embedding movement, dead token behavior, fimbulwinter onset).

## The Goal

Find an architecture that:
1. **Trains fast** on M4 Pro (~12+ it/s target, but see below about frame rate)
2. **Shows interesting dynamics** (not stuck in unigram hell)
3. **Is fully observable** (we can record everything without drowning in data)

We're *not* optimizing for model quality. We're optimizing for **scientific utility**.

## The Insight: Frame Rate Matters

Batch size isn't about "how much training"—it's about **temporal resolution**.

| Batch Size | Steps per 1M tokens | Metaphor |
|------------|---------------------|----------|
| 256 × 128 | ~30 steps | 30 fps |
| 128 × 128 | ~61 steps | 60 fps |
| 64 × 128 | ~122 steps | 120 fps |
| 32 × 128 | ~244 steps | 240 fps |

Same total gradient signal. More frames = finer observation of dynamics. The question becomes: **what's the smallest batch size that still saturates the GPU?**

## The Search Space

**Architecture axes:**
- Layers: 2, 3, 4
- Hidden dim: 64, 96, 128
- Heads: 1, 2, 4
- FFN ratio: 2×, 4×

**Fixed (for now):**
- Sequence length: 128
- Tokenizer: TBD (custom character-level BPE, ~1K-10K vocab)
- Precision: bfloat16 weights (to match Qwen, observe lattice dynamics)

**To determine empirically:**
- Batch size (find the efficiency cliff first)

## Phase 1: Find the Efficiency Cliff

Before searching architectures, we need to know: at what batch size do we stop saturating M4 Pro's compute?

**Experiment:** Pick one architecture (say 3L/96D), run 1000 steps at batch sizes 32, 64, 128, 256. Measure tokens/sec. Find where throughput stops scaling linearly with batch size.

This tells us our "frame rate budget."

## Phase 2: Architecture Search

With batch size fixed at the efficiency cliff, test candidate architectures:

| Name | Layers | Hidden | Heads | FFN | Hypothesis |
|------|--------|--------|-------|-----|------------|
| Lean | 2 | 64 | 1 | 2× | Fastest, maybe too simple? |
| Balanced | 3 | 96 | 2 | 2× | Middle ground |
| Rich | 4 | 128 | 2 | 2× | Most capacity, slower |

Measure: tokens/sec, loss curve shape, whether it escapes unigram behavior.

## Phase 3: Validate Dynamics

Winner from Phase 2 gets a proper training run. Questions:
- Does it show bootstrap amplification (h_mean autocorr spike)?
- Do dead tokens freeze (fimbulwinter)?
- Is the lattice-scale motion observable and interesting?

If yes → this becomes our standard Goldilocks model for future experiments.

## Corpus & Tokenizer

**Previous approach:**
- ~2MB FineWeb (way too small, many epochs)
- Custom 10K character-level BPE with English + Thai
- Thai tokens stay "dead" when training on English-only

**Goldilocks approach:**
- Scale up corpus to ~100MB (single-digit epochs for biggest models)
- Revisit tokenizer size (smaller vocab = smaller embedding table = faster)
- Keep the Thai-tokens-as-dead-tokens trick (or simplify?)

Notebooks to create:
1. `01_corpus.ipynb` — Download and prepare training corpus
2. `02_tokenizer.ipynb` — Train custom tokenizer
3. `03_efficiency_cliff.ipynb` — Find optimal batch size
4. `04_architecture_search.ipynb` — Test candidate architectures
5. `05_validation.ipynb` — Full training run with winner

## Hardware Context

**M4 Pro 20-core GPU:**
- ~7.4 TFLOPS (FP32)
- 273 GB/s memory bandwidth
- We're almost certainly compute-bound, not memory-bound

**Napkin math:** For a 2M param model at batch 128×128:
- ~192 GFLOPs/step
- Theoretical max ~38 steps/sec
- Real-world will be lower (overhead, inefficiencies)

## Success Criteria

A winning Goldilocks model:
- ✓ Saturates GPU at reasonable batch size
- ✓ Trains at ≥10 it/s (adjustable based on what we learn)
- ✓ Shows diversification (loss drops, h variance increases)
- ✓ Exhibits clean dead token dynamics
- ✓ Small enough to record full W trajectory without pain

---

*Conceived: November 28, 2025 (end of Box 4)*
*Revised: November 29, 2025 (Workshop era begins)*
