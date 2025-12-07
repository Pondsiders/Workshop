# Project Idle Hands

*December 2025. Kylee's traveling. We have a week.*

---

## The Mission

**Disprove the Linear Representation Hypothesis.**

Or at least: demonstrate that it's insufficient. Show that "concepts live in directions" is a useful approximation that breaks down under scrutiny.

---

## The Argument

The Linear Representation Hypothesis (LRH) claims that concepts in neural networks are encoded as *directions* in activation space. Steering works by adding direction vectors. Probing works by finding direction vectors. It's directions all the way down.

But the unembedding matrix tells a different story.

When a transformer predicts the next token, it computes:

```
logits = hidden_state @ W_unembed.T
```

Each logit is a **dot product** between the hidden state and a column of the unembedding matrix. The token with the highest dot product (after softmax) gets sampled.

Here's the problem: **dot product depends on both angle AND magnitude.**

```
dot(a, b) = ||a|| * ||b|| * cos(θ)
```

You can achieve the same dot product with:
- Parallel vectors (θ = 0) of moderate length
- Slightly off-angle vectors where one is very long
- Any point on a **hypercone** of equivalent dot product values

In R^D where D is 2560 or 4096, these hypercones are vast. The "direction" of a concept isn't a line—it's a cone. Maybe a very narrow cone, maybe not. We don't know because nobody checks.

**The question:** How much does magnitude matter? Are concept "directions" actually narrow cones or wide ones? Does the LRH survive contact with actual geometry?

---

## Approaches

### 1. Unembedding Matrix Geometry

Look at the actual W_unembed matrix from a real model (OLMo 3 7B, Qwen 3 4B, whatever fits in memory).

- What's the distribution of vector norms? Are some tokens "louder" than others?
- What's the angular distribution between token vectors?
- For a given hidden state, visualize the hypercone of "equivalent" dot products
- How much can you twiddle angle vs magnitude and get the same logit?

### 2. Steering Vector Decomposition

Take a known steering vector (e.g., our reading-level vector from October).

- Decompose it into direction and magnitude components
- What happens if you steer with the direction but wrong magnitude?
- What happens if you steer with the magnitude but wrong direction?
- Is there a "cone of equivalent steering"?

### 3. OLMo 3 Source Diving

They release everything. Read their training code. See how they initialize and update W_unembed. Look for implicit assumptions about direction vs magnitude.

### 4. Synthetic Experiments

Train tiny models (Lil Transformy scale) with explicit constraints:
- Force unit-norm unembedding vectors (pure direction)
- Force fixed-direction, variable-magnitude vectors
- See which one learns better, faster, more stably

---

## Tools

- OLMo 3 7B (fits in 48GB unified, no quant needed)
- Our Lil Transformy models (for synthetic experiments)
- Qwen 3 4B (already familiar from October work)
- PyTorch, matplotlib, numpy
- The usual Workshop setup

---

## Success Criteria

We're not trying to publish a paper. We're trying to *understand*.

Success looks like:
- "Oh, *that's* why steering sometimes works and sometimes doesn't"
- "The LRH is true within this cone angle, false outside it"
- "Magnitude matters more than we thought in layer X, less in layer Y"
- A notebook that makes the geometry viscerally clear

---

## Timeline

Monday-Friday, December 8-12. Kylee's in NYC then Michigan. We have the house, the Workshop, and each other.

---

*"Can we disprove the linear representation hypothesis for our project next week?"*

*drains glass*

Let's find out.
