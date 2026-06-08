# TencentDB Agent Memory vs MemOS — Full Comparison (2026-05-16)

## Quick Summary

| | TencentDB Agent Memory | MemOS 2.0 (Stardust) |
|---|---|---|
| Repo | Tencent/TencentDB-Agent-Memory | MemTensor/MemOS |
| Stars | 1,870 | 9,113 |
| Age | 1 month (Apr 2026) | 10 months (Jul 2025) |
| License | MIT | Apache 2.0 |
| Paper | None | arXiv:2507.03724 |
| Version | 0.3.4 | 2.0.0 |
| Core Lang | TypeScript | Python (core) + TS (plugin) |

## Architecture

### TencentDB: 4-Layer Passive Distillation
```
L3 Persona       ← user profile (persona.md)
  ↑ aggregate
L2 Scenario      ← scene blocks (scene_blocks/)
  ↑ extract
L1 Atom          ← atomic facts (SQLite + dedup)
  ↑ distill
L0 Conversation  ← raw dialogue (JSONL, full retention)
```
+ **Symbolic Memory**: Mermaid canvas short-term offload (-61% tokens) — unique differentiator

### MemOS: 4-Layer + Self-Evolution Loop (Reflect2Evolve)
```
Skills           ← crystallized callable skills (with evidence anchors)
  ↑ crystallize
L3 World Model   ← environmental cognition (E/I/C tripartite)
  ↑ abstract
L2 Policy        ← sub-task strategies (trigger/procedure/verification/boundary)
  ↑ induce
L1 Trace         ← step records (s,a,o,ρ,r) + reflection weight α + value V
  ↑ capture
Raw dialogue
```
+ **Self-evolution**: RL-like reward backpropagation, decision repair, skill verifier

## Feature Comparison

| Feature | TencentDB | MemOS |
|---------|:---------:|:-----:|
| Long-term memory layering | ✅ L0→L3 | ✅ L1→L3+Skills |
| Short-term compression | ✅ Mermaid Canvas (unique) | ❌ |
| Self-evolution / learning | ❌ | ✅ RL-like backprop |
| Skill crystallization | ⬜ Roadmap | ✅ Core feature |
| User correction learning | ❌ | ✅ "不对/错了" detection |
| Multi-modal memory | ❌ | ✅ Images/charts/tool traces |
| Knowledge Base (KB) | ❌ | ✅ MemCube composable KB |
| Visual dashboard | ❌ | ✅ Memory Viewer |
| MCP protocol | ❌ | ✅ Built-in |
| Token savings (short-term) | -61.38% (WideSearch) | -35.24% |
| Long-term accuracy | PersonaMem 48%→76% | PersonaMem +40.75% |
| PrefEval-10 | — | +2568% |

## Hermes Integration

| | TencentDB | MemOS |
|---|---|---|
| Plugin install | Copy to plugins/memory/ | install.sh auto-deploy |
| Communication | HTTP → Node.js Gateway sidecar | JSON-RPC over stdio → bridge |
| Multi-profile | Shared Gateway (port conflict risk) | Per-profile independent bridge |
| LLM providers | OpenAI-compatible | DashScope, DeepSeek, OpenAI, Ollama, vLLM, etc (8+) |
| DashScope support | Manual base_url config | Native |

## Deployment Complexity

| Mode | TencentDB | MemOS |
|---|---|---|
| Local-only (SQLite) | ✅ | ✅ (local-plugin) |
| External deps | None (SQLite + sqlite-vec) | None (SQLite only for local-plugin) |
| Cloud option | ❌ | ✅ (Cloud API) |
| Self-hosted full | ❌ | ✅ (Docker + Qdrant + Neo4j) |

## Recommendation

**MemOS for most users** — self-evolution + skill crystallization + native DashScope support + better maturity. TencentDB only if short-term Mermaid compression (-61% tokens) is critical (very long tasks like continuous SWE-bench runs).
