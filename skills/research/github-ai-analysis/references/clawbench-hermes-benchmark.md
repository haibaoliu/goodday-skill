# ClawBench — Browser Agent Benchmark with Hermes Harness

> Source: https://github.com/TIGER-AI-Lab/ClawBench · 344 stars · arXiv 2604.08523

## What It Is

ClawBench is a standardized benchmark for evaluating AI web agents on real-world online tasks. 153 tasks across 144 live websites, 15 life categories. Each run is Docker-isolated with 5-layer recording (MP4, screenshots, HTTP traffic, browser actions, agent messages).

## Hermes Is a First-Class Harness

From `harnesses.yaml`:

```yaml
- name: hermes
  image: clawbench-hermes
  dockerfile: hermes/Dockerfile.hermes
  setup_script: hermes/setup-hermes.sh
  run_script: hermes/run-hermes.sh
  usage_emitter: hermes/usage-emitter.py
  extra_files:
    - hermes/hermes-capture.py
  agent_message_sources:
    - type: file
      path: /data/agent-messages.jsonl
    - type: file
      path: /tmp/hermes-live-agent-messages.jsonl
```

Hermes is one of 9 supported harnesses. Others: openclaw, opencode, claude-code, codex, browser-use, claw-code, pi.

## How to Run Hermes on ClawBench

```bash
git clone https://github.com/TIGER-AI-Lab/ClawBench
cd ClawBench
cp models/models.example.yaml models/models.yaml
# Edit models.yaml with your API keys
./run.sh  # Interactive TUI

# Or batch:
uv run clawbench-batch --models <model-name> --all-cases --harness hermes
```

## 5-Layer Recording Per Run

- `recording.mp4` — full session video
- `screenshots/*.png` — timestamped PNGs
- `requests.jsonl` — HTTP traffic
- `actions.jsonl` — browser action log
- `agent-messages.jsonl` — agent conversation transcript

## LLM Judge Evaluation

`eval/agentic_eval.md` defines the PASS/FAIL rubric. Scores are deterministic and reproducible.

## Why This Matters for Hermes

- First standardized benchmark where Hermes competes directly against other agent frameworks
- Can quantify Hermes' browser automation capabilities
- The 5-layer recording is a diagnostic goldmine — see exactly where Hermes succeeded/failed
- Results can be published to the ClawBench leaderboard for visibility
