---
name: goodday-trading-systems
description: >
  Analyze, modify, or extend the user's quantitative trading systems in the
  goodday repo (MT4/MT5 EAs, TCN+PPO deep learning, Python signal systems,
  Kronos model integration). Load this when the user mentions any of their
  trading systems, the goodday repo, TCN/PPO training, MT5 EAs, or Kronos
  forex prediction.
---

# GoodDay Trading Systems

## Trigger

Load when the user references:
- The `goodday` repo (`haibaoliu/goodday`)
- Any specific system: fx_tcn_rl, MMEA, AnnaSystem, ElliottWavesFibonacci, mt5-python-signal, ewm, kronos-project
- TCN, PPO, Triple Barrier, forward direction labeling
- MT4/MT5 Expert Advisors or indicators
- Kronos model for forex/stock prediction

## Critical Rule: Multi-Pass Deep Reading

**The user trains these systems for months.** Architecture evolves across iterations.
A surface-level read WILL miss the real design. Default approach:

1. **First pass** — list all files, identify subsystems, read top-level docs and configs
2. **Second pass** — read every .py/.mq5/.mqh file in the subsystem under scrutiny,
   looking for multi-model cascades, custom training pipelines, and non-obvious
   data flows
3. **Third pass** — trace the live/paper trading inference path end-to-end,
   because training code and inference code often diverge significantly
4. **Before offering opinions** — verify you've found ALL models in play.
   If the user says "I trained this for months," assume you're missing
   something and dig deeper before commenting.

## Architecture Overview

See `references/architecture.md` for the full system-by-system breakdown
including the TCN three-model cascade (Gate → Direction → Main TCN + PPO).

## Key Design Patterns

### Three-Model Cascade (fx_tcn_rl)

```
Gate TCN [32,32,64,64] → "Is there a move?" (binary, tb_label != 0)
    ↓ (not yet in live pipeline)
Direction TCN [16,16,32] → "Up or down?" (trained only on gate=1 rows, 24-bar)
    ↓ (confirmation filter in paper_loop_v3)
Main TCN [32,32,64,64] → 128-dim embedding + P(+1)/P(0)/P(-1) → PPO action
```

- **Dir TCN is a filter, not a replacement** — PPO decides, Dir can veto
- **Logit bias calibration**: `calibrate_tcn.py` optimizes `delta` via
  `scipy.optimize.minimize_scalar` to centre `median(conf) = 0.5`
- **Forward direction labeling** replaced Triple Barrier as training target —
  no R:R in the signal, pure direction

### Strategy Fusion with Scoring (MMEA)

8 strategies vote → Market Structure Engine validates → SignalScoring
scores on 5 dimensions (structure/strategy/momentum/RR/environment).

### Kronos Integration Gap

The `kronos-project/` directory currently only contains the Kronos model
submodule. No custom wrapper code exists in the repo yet. Kronos is a
generative K-line model — it predicts full OHLCV paths, not just labels.

When integrating Kronos, do NOT try to replace TCN's direction role.
Kronos fits as a **risk verification layer** after PPO decides to trade:
path quality, expected R:R from predicted extremes, max drawdown in path.

## Pitfalls

- **Never shallow-read**: the subsystems have multiple model files (train_gate.py,
  train_dir.py, train_tcn.py) that look like variants but are a coordinated cascade
- **paper_loop_v3 is the current live pipeline**, not live_loop.py
- **Labeling evolved**: Triple Barrier → Forward Direction. Don't assume one or the other
- **Gate TCN is trained but not yet in the live pipeline** — confirm current state
  before assuming it's active
- **Kronos is a submodule** — requires `git submodule update --init` to access

## Repo Access

```bash
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_goodday" git clone git@github.com:haibaoliu/goodday.git
```
