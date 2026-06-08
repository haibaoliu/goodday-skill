# pymc Installation on macOS x86_64 (Python 3.11)

Full recipe for installing pymc 5.28 on Intel Mac without LLVM from brew.

## The Deadlock

```
pymc → pytensor → numba → llvmlite
                          ↘ LLVM (brew install llvm@19 — but llvmlite 0.47 needs LLVM 20, not yet released)
numba 0.60 → needs llvmlite 0.43 ✓, needs numpy < 2.0 ✗ (we have 2.4)
numba 0.65 → needs llvmlite ≥ 0.47 ✗ (no x86_64 wheel, needs LLVM 20)
```

No version pairing satisfies all constraints simultaneously.

## Working Recipe (non-JIT mode)

```bash
# Prerequisites
pip install --upgrade pip

# Step 1: install llvmlite from pre-built wheel (last version with x86_64 macOS wheel)
pip install llvmlite==0.43.0

# Step 2: install pymc body without dependencies
pip install pymc --no-deps

# Step 3: install pymc's deps (arviz pulls xarray, h5py, etc. as side effects)
pip install arviz cachetools cloudpickle xarray h5netcdf h5py xarray-einstats

# Step 4: fix cachetools version (pymc requires <7, pip installed 7.x)
pip install "cachetools<7"

# Step 5: install pytensor 2.38.x (matches pymc req) without deps
pip install "pytensor<2.39,>=2.38.2" --no-deps

# Step 6: install pytensor's runtime deps EXCEPT numba
pip install cons etuples logical-unification miniKanren filelock

# Step 7: verify
python -c "import pymc; print('pymc', pymc.__version__)"
# Output: pymc 5.28.5
```

## What's Missing

- **numba JIT compilation** — pymc runs in pure Python mode. Slower for large models but functionally complete.
- To get JIT: downgrade numpy to <2.0 OR wait for llvmlite to ship x86_64 macOS wheels for 0.47+.

## Environment

- macOS 12.7.6 (Intel x86_64)
- Python 3.11.15 (venv)
- pip 26.1.1
- Homebrew 5.1.0 (available but not needed)
