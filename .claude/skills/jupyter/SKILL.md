---
name: jupyter-notebooks
description: Create and edit Jupyter notebooks following Workshop conventions. Use when working with .ipynb files, creating new notebooks, editing existing notebooks, or doing ML/data analysis work in the Workshop.
---

# Jupyter Notebooks - Workshop Style

This skill contains our conventions for writing Jupyter notebooks. Standalone, reproducible, well-structured.

## Quick Reference

- **Standalone & reproducible**: "Restart & Run All" should work
- **Parameters at the top**: After imports, before work
- **Random seed**: 42, always
- **Device detection**: Early, use the standard pattern
- **Plots**: `steelblue`, `(10, 6)` figsize, save as `name@dpi.png`

## Full Conventions

See [conventions.md](conventions.md) for the complete guide, including:
- Notebook structure (Title → Setup → Load Data → Work → Summary)
- Device detection and memory management patterns
- Plotting style and resolution guidelines
- When to repeat code vs share data
- How I should edit notebooks (cell_id targeting, safe operations)
- Voice and tone for notebook narrative

## Standard Imports

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
from pathlib import Path
from tqdm.auto import tqdm

# Device detection
if torch.cuda.is_available():
    device = 'cuda'
elif torch.backends.mps.is_available():
    device = 'mps'
else:
    device = 'cpu'
print(f"Using device: {device}")
```

## Plot Saving Helper

```python
from pathlib import Path

def save_plot(fig, name, dpi=200, output_dir="."):
    path = Path(output_dir) / f"{name}@{dpi}.png"
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor='white')
    print(f"Saved: {path}")
    return path
```
