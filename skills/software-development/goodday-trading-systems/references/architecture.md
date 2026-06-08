# GoodDay Repo — Full Architecture Reference

> Extracted 2026-06-01 from deep code review session. Update as systems evolve.

## Repo Structure

```
goodday/
├── MQ4/                          # Legacy MT4 systems (archive-tier)
│   ├── ea/                       # 20+ EAs (144MA, Hurricane, SSRC, ...)
│   ├── indicators/               # 30+ indicators (SuperTrend, SSRC, ZigZag, ...)
│   └── system/                   # Strategy documentation + templates
├── MQ5/                          # Active MT5 + Python systems
│   ├── ea/                       # 25+ EAs (TMA, TDI, Scalper, ...)
│   ├── indicators/               # MT5 indicators (TMA, Nostradamix, SSRC, ...)
│   └── system/                   # Core systems (see below)
│       ├── fx_tcn_rl/            # TCN + PPO deep RL (flagship)
│       ├── MMEA/                 # Multi-strategy fusion EA
│       ├── mt5-python-signal-system/  # Python signal pipeline
│       ├── AnnaSystem/           # Dual-mode EA (EURUSD intraday + XAUUSD scalping)
│       ├── ElliottWavesFibonacci/ # Wave + Fib indicator (many versions)
│       ├── ewm/                  # Elliott Wave Manager
│       ├── BBSystem/             # Bollinger Band EA
│       ├── EmaStoSystem/         # EMA + Stochastic docs
│       ├── assistant/            # BuySellPoints indicator variants
│       └── kronos/               # Kronos model (submodule only, no wrapper yet)
└── .github/workflows/            # CI (mql5 compile only)
```

## System Maturity Ranking

| System | Type | Tech | Maturity | Key Strength |
|--------|------|------|----------|-------------|
| fx_tcn_rl | Deep RL | Python/PyTorch/SB3 | ⭐⭐⭐⭐⭐ | 3-model cascade, calibrated |
| MMEA | Strategy fusion | MQL5 | ⭐⭐⭐⭐ | 8-strategy voting + structure |
| mt5-python-signal | Multi-factor signal | Python/MT5 | ⭐⭐⭐ | 4-layer confluence scoring |
| AnnaSystem | Dual-mode EA | MQL5 | ⭐⭐⭐ | H4+M15/M1, 8-indicator chain |
| ElliottWavesFibonacci | Indicator | MQL5 | ⭐⭐ | ~13 file versions, needs cleanup |
| kronos-project | Model only | Python | ⭐ | Submodule, no wrapper |

---

## fx_tcn_rl — Deep Dive

### Model Inventory

Three distinct TCN models, trained separately:

| Model | File | Arch | Window | Features | Classes | Training Data |
|-------|------|------|--------|----------|---------|---------------|
| Gate TCN | `tcn_gate.pt` | [32,32,64,64] | 128 bars | 11 (full) | 2 (flat/move) | All rows |
| Direction TCN | `dir_model.pt` | [16,16,32] | 24 bars | 6 (custom) | 2 (up/down) | gate_label=1 only |
| Main TCN | `tcn_h1.pt` | [32,32,64,64] | 128 bars | 11 (full) | 3 (-1/0/+1) | All rows |

### Gate TCN (`train/train_gate.py`)

- **Label**: `gate_label = 1 if |tb_label| > 0 else 0`
- **Class weights**: `1/sqrt(count)`, normalized to sum=2
- **Purpose**: Pre-filter — skip bars where no significant move is expected
- **Status**: Trained but NOT integrated into live pipeline yet

### Direction TCN (`train/train_dir.py`)

- **Label**: `dir_label ∈ {-1, +1}` (up/down), flat rows excluded
- **Training**: ONLY on rows where `gate_label == 1` AND `dir_label != 0`
- **Features** (6): `close_z, ema_fast_z, ema_slow_z, ema50_dist_z, rsi_14_z, roc_5_z`
- **Sampling**: `WeightedRandomSampler` — UP/DOWN balanced 50/50 per batch
- **Architecture**: Lightweight — `TcnEncoder([16,16,32], embedding_dim=64)`
- **Window**: 24 bars (~1 trading day) — short horizon, faster to overfit on distant patterns
- **Rationale**: The docstring says "direction signal is short-horizon, not a multi-week pattern, so a lighter model avoids over-reliance on distant context"
- **Thresholds**: `dir_long_th=0.52`, `dir_short_th=0.48` (slightly wider than 50/50 to reduce noise)

### Main TCN (`train/train_tcn.py`)

- **Label**: `tb_label` from Triple Barrier (SL=2*ATR, TP=3*ATR, max_horizon=24 H1 bars)
  - Also supports `--generate_label_if_missing` to generate Triple Barrier labels on the fly
- **Loss**: `FocalLoss(gamma=2.0, alpha=1.0)` with `1/sqrt(count)` class weights
- **Optimizer**: AdamW, CosineAnnealingLR, clip_grad_norm=1.0
- **Splits**: train/val from CSV `split` column; test segment is intentionally NEVER seen by TCN
- **Checkpoint**: Saves full metadata (feature_cols, seq_len, arch, params)

### Logit Bias Calibration (`train/calibrate_tcn.py`)

The system discovered a structural long-bias (L/S ratio ~10:1 before calibration).
Temperature scaling can't fix this because it preserves logit ordering.

**Solution**: Per-class bias shift on raw logits:

```
logits_corrected = logits + [+delta, 0, -delta]
```

Where `delta` is optimized via `scipy.optimize.minimize_scalar` to minimize:
`|median(conf) - 0.5|` on validation set.

Result stored in checkpoint as `direction_bias` key. `TcnInfer.infer()` reads this
and applies the correction at inference time.

Also stores `th_long` and `th_short` — balanced percentile thresholds for a target
signal rate (default 20%).

### Labeling Evolution

1. **Original**: Triple Barrier labels (`labeling.py: triple_barrier_labels`)
   - SL=2*ATR, TP=3*ATR, time barrier=24 bars
   - Labels: +1 (TP hit first), -1 (SL hit first), 0 (timeout)

2. **Current**: Forward direction labels (`labeling.py: forward_direction_label`)
   - `tb_label = sign(close[t+24] - close[t])` with 5-pip dead zone
   - No R:R concept in the label — pure directional signal

The Triple Barrier code still exists as a fallback option in `train_tcn.py`'s
`--generate_label_if_missing` flag.

### Live Inference Pipeline

**Active pipeline** (`live/paper_loop_v3.py`):

```
BarData → FeatureBuilder → Main TCN infer (embedding + probs)
    → SignalPipeline.on_bar() → PPO action (0/1/2) + direction
    → Direction TCN filter (must agree with PPO direction)
    → EMA trend alignment (ema_slow_z direction check)
    → Risk monitor (max drawdown, consecutive losses)
    → Position sizer (dynamic lots via RiskConfig)
    → Execute (SL/TP from PipelineConfig, exit simulation)
```

**Key components**:
- `live/paper_loop_v3.py` — current paper trading loop (v3 with Dir filter)
- `live/live_loop.py` — real-time loop (Yahoo Finance data, daemon mode)
- `live/signal_pipeline.py` — bar-by-bar H1 processing, TCN buffer, cooldown
- `live/tcn_infer.py` — Main TCN inference wrapper
- `live/dir_infer.py` — Direction TCN inference wrapper
- `live/ppo_infer.py` — PPO deterministic action prediction
- `live/trader_router.py` — RL/Rule/Stopped mode routing
- `live/monitor.py` — StrategyRiskMonitor (window_trades, consecutive_losses, max_dd)
- `live/position_sizer.py` — Risk-based dynamic position sizing

**Observation vector** (PPO, H1-only v4):
```
[h1_emb(128, L2-normed) | prob_pos | prob_neg | cooldown_frac | adx_z | hvol_pct | ema50_dist_z]
= 128 + 3 + 3 = 134 dims
```

### Training Pipeline

```
data/loader.py → cleaning.py → align.py (H1→H4 resample)
    → features.py (ATR, EMA, ADX, Bollinger, rolling z-score)
    → labeling.py (forward_direction_label or triple_barrier_labels)
    → build_prepared_data.py (train/val/test split)
    ↓
train/train_tcn.py (H1) + train/train_tcn.py (H4)
    → train/calibrate_tcn.py (logit bias correction)
    ↓
train/train_gate.py (Gate TCN)
    → train/train_dir.py (Direction TCN, filtered to gate=1)
    ↓
rl/train_ppo.py (PPO on train split, eval on test)
    → eval/robustness.py (walk-forward, regime analysis)
```

---

## MMEA — Multi-Currency Signal EA

### Architecture

```
OnTick/OnTimer → RunStrategies()
    → For each symbol × strategy: OnTickLogic()
    → RunDecisionLayer()
        → MarketStructureEngine.Evaluate()  (Swing Points, BOS, CHoCH)
        → RiskManager.Evaluate()            (daily loss, spread, lot sizing)
        → CountStrategyVotes()              (aligned vs opposite by fresh signals)
        → SignalScoring.Evaluate()          (5-dim scoring)
        → ShouldSendRecommendation()        (dedup check)
        → Notifier.Send() + ChartAnnotator
```

### Scoring Dimensions (SignalScoring.mqh)

| Dimension | Max | Logic |
|-----------|-----|-------|
| Structure | 35 | StructureEngine confidence (BOS, CHoCH, Impulse, Fibonacci) |
| Strategy | 20 | `aligned*5 - opposite*6` + extras for 3+ aligned / 2+ opposite |
| Momentum | 15 | Base 7 + BOS(+3) + Impulse(+3) - CHoCH(-5) - wrong zone(-3) |
| R:R | 15 | RR≥2.0→15, RR<1.5→0, linear between |
| Environment | 15 | Session (overlap=10, London=8, NY=6, Asia=2) + spread quality |

### Strategies

SMACross, EMACross, EMASar, MAPB, VegasChannel, EmaAtrTrend, EMAStoch, EMAStochRsi

Each strategy is a `CStrategyBase` subclass with `OnTickLogic()`, `HasFreshSignal()`, `LastSignalType()`.

---

## mt5-python-signal-system

### Pipeline

```
MT5 Connector → Trend Analyzer → Pullback Health Analyzer
    → Pattern Recognizer → Structure Analyzer
    → Signal Generator → Notification Manager → Feishu
```

### Confidence Formula

| Component | Weight | Description |
|-----------|--------|-------------|
| Trend | 30% | `abs(score - 0.5) * 2` normalized |
| Health | 25% | `health_score / 100` |
| Pattern | 15% | Pattern score × direction match |
| Structure | 15% | Structure score when verified |
| Pullback prob | 10% | Continuation probability |
| Reversal penalty | -5% | Reversal probability (subtracted) |
| Confluence bonus | up to 25% | 4-layer resonance: trend+position+structure+pattern |

---

## AnnaSystem

- **EURUSD mode**: H4 direction + M15 entry (intraday)
- **XAUUSD mode**: H4 direction + M1 entry (scalping)
- **8 indicators**: Stochastic(H1/H4/M15/M1), ATR, SSRC, Camarilla, i-Regr, SuperSignals, MA Slope, TMA
- **7-step filter chain**: Volatility → Trend → SSRC → Stochastic → Camarilla → i-Regr → SuperSignals
- **Adaptive lot sizing**: RiskPerTrade=1% with dynamic calculation
- **Time window**: StartHour=8 to EndHour=22

---

## Kronos Integration Status

The `kronos-project/` directory contains ONLY the `shiyu-coder/Kronos` submodule
(commit `d5ffd46`). No custom wrapper code has been pushed yet.

### Kronos Model Capabilities

- **Type**: Autoregressive K-line foundation model (generates OHLCV sequences)
- **Input**: N bars of OHLCV + timestamp
- **Output**: M bars of predicted OHLCV (price + volume)
- **Architecture**: KronosTokenizer + Kronos base model + KronosPredictor
- **Fine-tuning**: CSV-based (`finetune_csv/`) — supports custom OHLCV data
- **Pretrained**: `NeoQuasar/Kronos-Tokenizer-base` + `NeoQuasar/Kronos-small`

### Integration Design (planned, not implemented)

Kronos should serve as a **risk verification layer**, not a direction replacer:

```
Gate TCN → Direction TCN → Main TCN → PPO action=1
    ↓
Kronos predicts 24-bar OHLCV path
    ↓
Extract: path_consistency, expected_rr, max_dd_in_path, vol_ratio
    ↓
All pass → Execute with Kronos-informed SL/TP
Any fail → Skip
```

### Direction Signal from Kronos Path

Instead of `pred_close[-1] > cur_close`:
- Linear regression slope on predicted close sequence → trend direction
- Path consistency (same-direction bar ratio) → quality check
- Weighted direction (exponential decay on future bars) → recency bias

### R:R from Kronos

- `expected_rr = (pred_high - entry) / (entry - pred_low)` for long
- Use as dynamic override for fixed SL/TP instead of constant 2:1

### Kronos Wrapper Variables to Expose

| Variable | Meaning | Threshold |
|----------|---------|-----------|
| `path_consistency` | Ratio of same-direction bars | >0.55 |
| `expected_rr` | R:R from predicted extremes | >1.5 |
| `max_dd_in_path` | Largest drawdown within predicted path | <1.5 ATR |
| `vol_ratio` | Predicted volatility / historical volatility | <2.0 |
| `direction` | +1 long, -1 short (from slope) | must match TCN/PPO |
