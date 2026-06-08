---
name: python-dependency-resolution
description: Resolve complex pip dependency conflicts — isolate, version-match, and unblock install chains for scientific/ML packages. Trigger when pip install fails with dependency chains, wheel build errors, or version deadlocks.
version: 1.0.0
tags: [pip, dependencies, mlops, troubleshooting, venv]
---

# Python Dependency Resolution

Resolve pip dependency deadlocks through systematic isolation — not blind retries or "just install everything from conda."

## When to Use

- `pip install X` fails with a chain of build errors (e.g., wheel build failures, cmake errors, LLVM version mismatches)
- Multiple packages have conflicting version constraints (A requires B<2, B requires A>=3)
- A dependency requires a system library (LLVM, CUDA, etc.) that's missing or wrong version
- Scientific/ML stack installs (numpy + numba + llvmlite + pytorch + pymc + ...)

## Core Pattern: Isolate → Identify → Resolve

### Phase 1: Isolate the culprit

```bash
# Install the main package without dependencies
pip install <target> --no-deps

# List what deps it would pull
pip install <target> --dry-run | grep -E "(Would install|Collecting)"

# Install deps one by one until you hit the failure
for pkg in dep1 dep2 dep3 ...; do
  pip install "$pkg" 2>&1 | tail -5
done
```

### Phase 2: Identify the constraint

For the failing package, check:
- **Version requirements**: `pip install <pkg> --dry-run` to see what's needed
- **System dependencies**: Read the build error — does it need cmake? LLVM? A specific compiler?
- **Pre-built wheel availability**: `pip index versions <pkg>` then check PyPI JSON for platform wheels
- **Cross-package constraints**: `pip show <pkg>` to see what requires what

### Phase 3: Resolve (options in order of preference)

1. **Pin to a version with pre-built wheels** — older wheels often exist for more platforms
   ```bash
   pip install pkg==X.Y.Z  # find via pip index versions + PyPI
   ```

2. **Install the blocker's deps selectively** — `--no-deps` for the main package, then manually install only compatible deps
   ```bash
   pip install blocker --no-deps
   pip install blocker-dep1 blocker-dep2 ...  # hand-pick compatible versions
   ```

3. **Accept degraded mode** — some packages work without optional deps (e.g., pymc without numba JIT)
   - Test with `python -c "import pkg; print(pkg.__version__)"`
   - If it imports and core functionality works, the optional dep is truly optional

4. **Install missing system library** — only as last resort (slow, may conflict)
   ```bash
   brew install llvm@18  # macOS
   apt install llvm-18-dev  # Linux
   ```

### Pitfalls

- **`externally-managed-environment` on macOS** — modern macOS system Python blocks bare `pip install`. Use a venv. Hermes ships one at `~/.hermes/hermes-agent/venv/`: `source ~/.hermes/hermes-agent/venv/bin/activate && pip install ...`. For timeouts on large downloads (playwright 43MB+), install packages individually rather than from a monolithic requirements.txt.
- **Don't trust `pip check`** — it reports missing optional deps as errors. Test with actual imports instead.
- **Don't upgrade pip mid-debug** unless the error specifically says so. Newer pip can change resolution behavior.
- **Don't install from source if a wheel exists** — always try older pinned versions first.
- **`--no-build-isolation`** can help when build deps clash with installed deps, but it usually makes things worse by exposing local package conflicts.
- **numpy 2.x breaks numba < 0.61** — if you need both, pin numpy<2 or accept non-JIT mode.
- **llvmlite has no x86_64 macOS wheels past 0.43** — need LLVM from brew for newer versions.

### Verification

After every resolution step:
```bash
python -c "import <target>; print(<target>.__version__)"
```
Don't trust "Successfully installed" — the real test is import.

## Reference Files

- `references/pymc-macos-x86_64.md` — Full pymc 5.28 installation recipe for macOS Intel with Python 3.11, including the llvmlite/numba/numpy deadlock workaround.
