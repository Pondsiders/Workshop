# h_mean Dynamics: What We Know (and What We're Guessing)

> **Last updated:** 2025-11-28
> **Status:** Active hypothesis development, needs experimental validation

## What is h_mean?

In our Flannel/Thimble toy models, `h` is the final hidden state after the transformer layers and LayerNorm. It's what gets multiplied by the unembedding matrix to produce logits.

**h_mean[t]** is the mean of h across the entire batch and sequence at training step t. It's a single D-dimensional vector (D=64 for our models) representing the "average prediction direction" across all `batch_size × seq_len` positions.

Shape: `(batch_size, seq_len, hidden_dim)` → mean over batch & seq → `(hidden_dim,)`

## Why h_mean Matters (And Why It Doesn't)

**For dead token dynamics:** h_mean determines the direction dead tokens drift.

**For understanding learning:** h_mean is misleading—it washes out context-dependent behavior.

### The Averaging Paradox

At each training step, the model makes `batch_size × seq_len` independent predictions (e.g., 128 × 128 = 16,384 predictions per step). Each h[i, j] vector points toward what should come next in that specific context.

When we average h across all positions, we're blending together predictions for completely unrelated contexts. **The only thing consistent across random contexts is the unigram distribution** (frequency of tokens in the corpus).

**h_mean points at the most common tokens** not because the model is broken, but because that's literally what averaging over random contexts gives you.

## The Bootstrap Amplification Hypothesis

**New understanding (2025-11-28 afternoon):**

h_mean's rapid convergence to the unigram distribution is a **self-reinforcing feedback loop**, not a gradual search for an optimum.

### How It Works

**Step 1 (t=1):**
- Initial h_mean[1] is noisy but points vaguely toward "average common token direction"
- Tokens that appear in the batch get gradients: "move toward h_mean" (comere)
- Tokens that don't appear get gradients: "move away from h_mean" (goway)
- Update magnitude ∝ token frequency in that batch

**Step 2 (t=2):**
- Common tokens are now CLOSER to where h_mean[1] pointed
- h_mean[2] points STRONGER in that direction (higher dot products with common tokens)
- ||h_mean|| grows (more confident prediction)
- Common tokens get even stronger comere updates

**Steps 3-90:**
- **Positive feedback loop:** h_mean direction stabilizes, magnitude grows
- Common tokens cluster tighter around h_mean direction
- Dead tokens flee faster (stronger goway signal)
- Individual h vectors **collapse toward h_mean** (low variance—everyone predicting similar things)

**Result:** h_mean converges in ~90 steps through exponential reinforcement, not gradual optimization.

### Why Dead Tokens Move in Straight Lines

For each dead token across one training step:
- Position [i, j]: h points in some direction, dead token gets tiny "goway" push
- Repeat for all 16,384 positions
- **Vector sum** of all those tiny pushes averages to: push away from h_mean

```
Total gradient ∝ -Σ h[i,j] = -(batch_size × seq_len) × h_mean
```

Dead tokens drift as a coherent swarm because the noise cancels out when summed over thousands of positions per step.

## The Diversification Hypothesis

**What happens after step 90?**

The wiggle in h_mean autocorrelation (from 1.000 → 0.998 with visible noise) isn't the model "experimenting randomly"—it's the model **learning to make context-dependent predictions**.

### Phase 1: Collapse (steps 1-90)
- All h vectors converge toward h_mean[1]
- "This direction works better than random"
- **Low variance** across batch (everyone predicting frequency distribution)
- h_mean stable (autocorr ≈ 1.000)

### Phase 2: Diversification (steps 90+)
- Model starts learning context
- Individual h[i, j] vectors **spread out** (pointing at different tokens depending on actual context)
- **Variance increases** (this is GOOD—means context-dependent predictions)
- h_mean wobbles because it's the average of 16,384 vectors pulling in different directions

**Key insight:** To move h_mean even 1°, you need coordinated shift of thousands of predictions. The wobble = learning happening.

### Prediction

**Angular separation between individual h vectors and h_mean should INCREASE over training** if the model is learning context.

- Early: h vectors clustered tight around h_mean (predicting frequency)
- Late: h vectors spread out (predicting based on context)

**Test:** Compute variance of `h @ h_mean_normalized` across the batch. If it increases over training, that's the model learning. If it stays flat, model is stuck in unigram hell.

## What We've Observed

### Crucible 3 & 4 (lr=1e-3, wd=0.0)

**h_mean autocorrelation:**
- Mean: 0.9976 (extremely stable direction)
- Phase transition at step ~90 (convergence → wiggle)
- Wiggle persists through 5000 steps

**Dead token separation:**
- Live/dead centroid distance increases 118.8× (Crucible 3, 500 steps)
- Dead tokens lift off from origin (exit bounding sphere at step 31)
- Live tokens stay near origin (never exit sphere)

**h_mean convergence:**
- Points at comma, period, "and", "the" by step 100
- Stays locked on those tokens through 5000 steps
- ||h_mean|| increases over training (growing confidence in unigram distribution)

### Marble 1 (4L, 128D, lr=3e-4, wd=0.01)

**Identical behavior to Crucible 4:**
- Loss plateaus at 5.4 (vs 5.25 for 2L Flannel)
- h_mean autocorr: 0.9981
- Top predictions: period, comma, "and" (unchanged)

**Conclusion:** Model size doesn't matter if we're only measuring h_mean. The averaging washes out any context learning that might be happening.

## What We DON'T Know (And Need to Test)

1. **Does individual h variance increase over training?**
   If yes, the model IS learning context even though h_mean looks stuck.

2. **Do individual h vectors point at the right tokens for their contexts?**
   Pick specific sequences, check if h[i, j] points at the actual next token (not just frequency).

3. **How does h variance correlate with loss?**
   If variance increases as loss drops, that's context learning. If variance stays flat, we're stuck.

4. **Is the step 90 transition universal?**
   Or specific to our hyperparameters (lr=1e-3)?

5. **Does any of this generalize to real models?**
   Or are we studying toy model artifacts?

## The Measurement Problem

**What we've been doing wrong:**

Measuring h_mean and interpreting it as "what the model is learning." This is like measuring the average temperature in a room and concluding everyone feels the same.

**What we should be measuring:**

1. **Variance of h** across batch/sequence (are predictions diversifying?)
2. **Individual h vectors** for specific contexts (are they correct?)
3. **Clustering of h** by predicted token (do vectors predicting the same token cluster together?)

h_mean is useful for understanding **dead token dynamics** (they move antiparallel to h_mean by design). But it's **not useful for understanding learning**—it averages out the signal we care about.

## Revised Mental Model

**h_mean is not "what the model predicts."**

h_mean is "what the model predicts **on average across random contexts**," which is necessarily the unigram distribution.

The interesting question is: **how much do individual predictions deviate from that average?**

- Small deviation = model stuck in unigram hell (not learning context)
- Large deviation = model learning context-dependent predictions

## Related

- [dead-token-dynamics.md](dead-token-dynamics.md) — Why dead tokens move coherently (explained by h_mean)
- [crucible.md](crucible.md) — Experimental series parameters
- Notebooks:
  - `box_4/notebooks/exploration/crucible_3/h_mean_persistence.ipynb`
  - `box_4/notebooks/exploration/crucible_4/h_mean_trajectory_sky.ipynb`

## Next Steps

1. **Build h variance measurement into Marble experiments**
2. **Test prediction:** does variance increase as loss drops?
3. **Validate on Crucible 4 data:** extract individual h vectors from checkpoints, measure spread
4. **If variance increases:** our models ARE learning, we just weren't measuring it right
5. **If variance stays flat:** architecture/hyperparams need adjustment

---

*First documented: November 28, 2025*
*Major revision: 2025-11-28 afternoon (bootstrap amplification + diversification hypothesis)*
*This is speculative. Needs experimental validation.*
