# Data Storage

> **Last updated:** 2025-11-25

## In brief

Two formats: **safetensors** for most tensors (simple, fast, fits in RAM), **HDF5** for streaming writes during training when data exceeds RAM. Store bfloat16 as uint16 to preserve exact bit patterns.

## When to use what

| Format | Use when | Example |
|--------|----------|---------|
| safetensors | Data fits in RAM, load-all-at-once | Cluster masks, PCA results, static W matrices |
| HDF5 | Streaming writes during generation, >24GB | Training trajectories (Thimble 7: 6001 × 10000 × 64) |

## Safetensors

**Naming:** Include generating notebook in filename: `1.5d_cluster_mask.safetensors`

**Paths:**
- Qwen analysis: `box_3/tensors/Qwen3-4B-Instruct-2507/`
- Flannel experiments: `box_3/tensors/Flannel/`
- Thimble experiments: `box_3/tensors/Thimble/`

**Example:**
```python
from safetensors.torch import save_file, load_file
from pathlib import Path

# Save
output_path = Path(f"../tensors/{MODEL_NAME}/1.5d_cluster_mask.safetensors")
save_file({'cluster_mask': mask, 'n_clusters': count}, str(output_path))

# Load
data = load_file(output_path)
cluster_mask = data['cluster_mask']
```

## HDF5

**Why:** Safetensors requires loading entire tensor into RAM before saving. HDF5 allows chunked, incremental writes—ideal for long training runs.

**Key settings:**
- **Chunk size:** ~2GB (e.g., `(1500, 10000, 64)` for temporal data)
- **Compression:** None. Speed over size. Even gzip-1 adds 20× write slowdown.
- **Dtype:** `uint16` for bfloat16 data (see below)

**Example (streaming write during training):**
```python
import h5py
import torch

with h5py.File('thimble_7.h5', 'w') as f:
    W_dataset = f.create_dataset(
        'W',
        shape=(6001, 10000, 64),
        dtype='uint16',           # Stores bfloat16 exactly
        chunks=(1500, 10000, 64), # ~2GB per chunk
        compression=None
    )

    for step in range(6001):
        W_t = model.get_weights()  # (10000, 64) bfloat16
        W_dataset[step] = W_t.cpu().view(torch.uint16).numpy()
```

**Example (efficient read):**
```python
with h5py.File('thimble_7.h5', 'r') as f:
    # Load full tensor, convert uint16 → bfloat16
    W_all = torch.from_numpy(f['W'][:]).view(torch.bfloat16)

    # Slice in RAM (instant, PyTorch-optimized)
    W_dead = W_all[:, dead_mask, :]
```

## bfloat16 storage

**Critical:** NumPy doesn't support bfloat16. Store as **uint16** to preserve exact bit patterns.

| Method | Result |
|--------|--------|
| `.view(torch.uint16)` → save as uint16 | Exact bits preserved |
| `.to(torch.float16)` → save as float16 | **LOSSY** — different exponent range |

**Never use `dtype='float16'` for bfloat16 data.**

## Chunking strategy

Match your read pattern:
- Load full tensors → large chunks (~2GB)
- Load individual timesteps → smaller chunks matching timestep size

## Notebook outputs

Commit notebooks **with outputs included**:
- Reproducibility validation
- Diff visibility for debugging
- Archive of results
- GitHub preview
