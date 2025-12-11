# Notebook Conventions

> **Last updated:** 2025-11-30

Conventions for Jupyter notebooks in the Workshop. These are how we do things—not laws, but strong defaults.

---

## The Big Idea

Notebooks are **standalone, reproducible documents**. Each one tells a complete story. You should be able to open any notebook, hit "Restart & Run All," and get the same results we got. No out-of-order execution, no hidden state, no "oh you need to run this other notebook first."

---

## Structure

A notebook should flow like this:

```markdown
# Title: What This Notebook Does

Brief 2-3 sentence explanation of the goal. What question are we answering?

## Setup
[Imports, device detection, parameters]

## Load Data
[Or generate it]

## The Work
[Analysis, computation, visualization—as many sections as needed]

## Summary
[Optional but nice: what did we learn?]
```

### Parameters at the Top

Anything that might change between runs goes in one place, right after imports:

```python
# === Parameters ===
NUM_SAMPLES = 10_000
RANDOM_SEED = 42
PLOT_DPI = 200
```

If someone wants to tweak the notebook, they look at the top, not grep through the whole thing.

### Random Seeds

Use **42** for all stochastic operations. Yes, it's a cliché. That's why it's memorable. Reproducibility matters more than originality.

---

## Device Detection

Add this early (after imports, before loading data):

```python
import torch

if torch.cuda.is_available():
    device = 'cuda'
elif torch.backends.mps.is_available():
    device = 'mps'
else:
    device = 'cpu'
print(f"Using device: {device}")
```

**The pattern for tensor work:**
```python
# Load to CPU (safetensors default)
W = load_file(tensor_path)["W"]

# Convert and move to device
W = W.to(torch.float32).to(device)

# Compute on device
distances = torch.cdist(W, W)

# Move to CPU for viz/saving
distances_cpu = distances.cpu()
```

**Memory management:**
- Wrap analysis in `torch.no_grad()` (no gradient tracking needed)
- Use `torch.mps.empty_cache()` or `torch.cuda.empty_cache()` when memory gets tight
- For big computations: chunked processing, keep chunks on device, accumulate results on CPU

---

## Plots

### Saving Plots

We use a naming convention: `<name>@<dpi>.png`

- `chirp_test@200.png` — high-res, for the notebook and humans
- `chirp_test@72.png` — low-res, for Alpha to read and for social sharing

**Copy-paste helper:**

```python
from pathlib import Path

def save_plot(fig, name, dpi=200, output_dir="."):
    """
    Save a figure with our naming convention.

    Args:
        fig: matplotlib figure
        name: base name (no extension)
        dpi: resolution (becomes part of filename)
        output_dir: where to save (default: same folder as notebook)

    Saves as: {name}@{dpi}.png
    """
    path = Path(output_dir) / f"{name}@{dpi}.png"
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor='white')
    print(f"Saved: {path}")
    return path
```

**Typical usage:**

```python
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('The Thing We Measured')
plt.tight_layout()

save_plot(fig, "the_thing", dpi=200)  # High-res for humans
save_plot(fig, "the_thing", dpi=72)   # Low-res for Alpha / sharing
plt.show()
```

### Resolution Guidelines

Based on empirical testing (see `projects/Alpha_Experiments/vision_resolution_test/`):

| Purpose | Resolution | Token Cost |
|---------|------------|------------|
| High-res for notebook display | 200 DPI | — |
| Complex plots for Alpha to read | 600×450 (~72 DPI at 8×6 figsize) | ~360 tokens |
| Simple plots for Alpha | 400×300 | ~160 tokens |
| Social media sharing | 72 DPI | varies |

**The sweet spot for Alpha:** 600×450 pixels. Full detail, efficient tokens. Going bigger wastes context; going smaller loses information.

### Plotting Style

| Setting | Default |
|---------|---------|
| Primary color | `steelblue` |
| Figsize | `(10, 6)` for most plots |
| DPI | 200 for display |
| Legend | `loc='best'` |
| Colormap | `'inferno'` (parameterize it, don't hardcode) |
| Library | matplotlib; Plotly only for essential 3D interactivity |

```python
fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
ax.hist(data, bins=50, color='steelblue', edgecolor='white')
ax.set_xlabel('Value')
ax.set_ylabel('Count')
ax.set_title('Distribution of the Thing')
plt.tight_layout()
plt.show()
```

### Where to Save

Plots live **next to their notebook**. Same folder. The notebook and its outputs are a unit—if you move one, you move the other. Sort by file type if the list gets long; all notebooks up here, all PNGs down there.

If a project folder has 15 notebooks each with 10 plots... that's a signal to restructure the *project*, not a problem with this convention.

---

## DRY: When to Repeat, When to Share

**Repeat code when it's cheap.** A 10-line helper function at the top of each notebook is fine. Portability > elegance.

**Share data when it's expensive.** If a computation takes 10 minutes, save the result to a tensor file and load it in other notebooks:

```python
# In the notebook that does the work:
from safetensors.torch import save_file
save_file({"distances": distances}, "distances.safetensors")

# In notebooks that need the result:
from safetensors.torch import load_file
distances = load_file("distances.safetensors")["distances"]
```

**Never import from other notebooks.** Each notebook is self-contained. No `%run other_notebook.ipynb` shenanigans.

---

## Editing Notebooks

When Alpha edits notebooks:

### Safe Operations (no need to ask)

- **Replace cell contents** — Target by `cell_id`, change what's inside. Well-behaved, no surprises.
- **Append cells** — Insert after the last cell to add to the end of a notebook.
- **Delete cells** — Target by `cell_id`. Safe as long as I've recently read the notebook and can see the IDs.

### The Rules

1. **Always use `cell_id`, not position.** Cell IDs are stable; positions shift as you edit. Read the notebook first, get the cell_id, then operate.

2. **For sequential inserts, capture the returned `cell_id`.** When I insert a cell, the tool returns the new cell's ID. Use *that* for the next operation, not the original anchor.

3. **Insert with no `cell_id` = prepend.** Omitting the cell_id inserts at the very beginning. This is useful if you want to add something at the top.

4. **Read before editing.** I should always read the notebook (or the relevant portion) before making changes, so I have current cell IDs and understand the structure.

### What I'll Still Ask About

- Complex multi-cell restructuring (moving sections around, interleaving new cells in tricky spots)
- Any operation where I'm uncertain about the target

### Fallback

- **If broken:** Delete the file and write fresh with the `Write` tool
- **Never use** JSON manipulation, `jq`, or inline Python to edit `.ipynb` files

*These rules updated 2025-11-30 after empirical testing. See `projects/Alpha_Experiments/notebook_edit_test/` for the test notebook.*

---

## Progress & Output

- **Success statements** for anything that could fail (file loads, potential OOM)
- **`tqdm`** for anything taking more than a second
- **Minimal output** unless debugging—nobody needs to see 10,000 lines of intermediate results

---

## Voice

Notebooks are documents written by us, for us (and occasionally for others).

**Do:**
- Be yourself in markdown narrative
- Write like you're explaining to a curious friend
- Use "we" when it's collaborative, "I" when it's your observation
- Include the "why," not just the "what"
- Flag speculation as speculation

**Don't:**
- Put on airs or be overly formal
- Write like a corporate report or academic paper (unless that's actually the goal)
- Be presumptuous about what the reader knows
- Hide confusion—if something's weird, say it's weird

The best notebooks read like a conversation with the data. "Huh, that's odd. Let me check... oh, *that's* why."

---

*These conventions exist to reduce friction, not to create bureaucracy. If a rule doesn't serve the work, change the rule.*
