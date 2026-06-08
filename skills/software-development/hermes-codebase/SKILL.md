---
description: "改Hermes源码：修改/扩展/debug Hermes Agent代码。覆盖config/providers/prompts/tools/内部架构。触发词：改Hermes/修改agent/hermes源码/fix hermes/hermes codebase。"
version: 1.0.0
metadata:
  hermes:
    tags: [hermes, internals, contributing, codebase, config, development]
    related_skills: [hermes-agent, hermes-agent-skill-authoring]
---

# Hermes Codebase Modification

Patterns and pitfalls for modifying the Hermes Agent source code at
`~/.hermes/hermes-agent/`.  Use this whenever you need to add a config
field, extend the provider system, modify the system prompt, or debug
internal resolution chains.

## When to Use

- Adding a new config field (to `custom_providers`, `delegation`, etc.)
- Extending provider credential resolution
- Modifying the system prompt or skill listing
- Debugging API key / base_url / provider routing issues
- Running or writing tests against the Hermes codebase
- Any code change that touches `hermes_cli/config.py`, `hermes_cli/auth.py`,
  `hermes_cli/runtime_provider.py`, or `agent/prompt_builder.py`

## Prerequisites

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
cd ~/.hermes/hermes-agent
```

The test suite uses pytest.  Run with `-o 'addopts='` to clear baked-in flags:
```bash
python -m pytest tests/ -o 'addopts=' -q
```

## Architecture: Provider Credential Resolution Chain

When the agent needs an API key, this is the full chain:

```
~/.hermes/.env + os.environ
    │  load_env() / get_env_value()              [config.py:4686, 5101]
    ▼
_get_env_prefer_dotenv()                         [credential_pool.py:1760]
    │
    ▼
_resolve_api_key_provider_secret(provider, pconfig)  [auth.py:577]
    │  1. Copilot special case
    │  2. Iterates pconfig.api_key_env_vars → get_env_value()
    │  3. Checks pconfig.api_key_command → subprocess.run()
    │  4. Falls back to credential pool
    ▼
resolve_api_key_provider_credentials(provider)       [auth.py:5698]
    │
    ▼
resolve_runtime_provider()                           [runtime_provider.py:1047]
    │  Also handles custom_providers, OAuth, credential pool
    ▼
CLI extracts api_key, base_url                       [cli.py:4288]
    │
    ▼
init_agent(api_key=..., base_url=...)               [agent_init.py:648]
  or resolve_provider_client()                      [agent_init.py:715]
    │
    ▼
OpenAI(api_key=..., base_url=...)                   [auxiliary_client.py]
```

For **auxiliary models** (vision, compression, web_extract):
`_resolve_api_key_provider()` in `auxiliary_client.py:1391` iterates
`PROVIDER_REGISTRY` and calls `resolve_api_key_provider_credentials()`
which flows through the same `_resolve_api_key_provider_secret()`.

For **custom providers** (`custom_providers` in config.yaml):
`_get_named_custom_provider()` → `_resolve_named_custom_runtime()` in
`runtime_provider.py`, which also has its own `api_key_command` execution
path.

## Pitfall: Adding a Config Field Requires THREE Places

When adding a new field to `custom_providers` (or `providers`) entries,
you MUST update all three of these in `hermes_cli/config.py`:

1. **`_KNOWN_KEYS`** in `_normalize_custom_provider_entry()` (~line 3053)
   — prevents "unknown config keys ignored" warning and field stripping
2. **`_VALID_CUSTOM_PROVIDER_FIELDS`** (line 3338)
   — schema validation for config doctor / migration
3. **The normalized dict builder** in `_normalize_custom_provider_entry()`
   (~line 3120) — the function builds a NEW dict from scratch; unrecognized
   fields are silently dropped even if they pass `_KNOWN_KEYS`

Example for `api_key_command`:
```python
# 1. _KNOWN_KEYS: add "api_key_command"
# 2. _VALID_CUSTOM_PROVIDER_FIELDS: add "api_key_command"
# 3. normalized dict builder:
api_key_command = entry.get("api_key_command")
if isinstance(api_key_command, str) and api_key_command.strip():
    normalized["api_key_command"] = api_key_command.strip()
```

## Pitfall: Prompt Builder Cache Invalidation

`build_skills_system_prompt()` in `agent/prompt_builder.py:1001` has a
two-layer cache:
- **Layer 1**: In-process LRU dict (`_SKILLS_PROMPT_CACHE`)
- **Layer 2**: Disk snapshot (`.skills_prompt_snapshot.json`)

When testing prompt builder changes, clear both:
```python
import agent.prompt_builder as pb
pb._SKILLS_PROMPT_CACHE.clear()
```

Also: `load_config()` itself caches the config.  Reset with:
```python
import hermes_cli.config as cm
cm._config_cache = {}
cm._config_mtime = 0
```

Monkeypatching `cfg_get` may not work because the config object is
captured in closures.  Prefer patching `load_config` to return a
pre-populated dict.

## Pitfall: ProviderConfig vs Custom Provider Resolution

`ProviderConfig` (in `hermes_cli/auth.py:167`) is the registry entry for
known providers (OpenRouter, Anthropic, DeepSeek, etc.).  Its
`api_key_command` is resolved in `_resolve_api_key_provider_secret()`.

Custom providers from `config.yaml` `custom_providers` list use a
completely separate path: `_get_named_custom_provider()` →
`_resolve_named_custom_runtime()`.  If you add a field to both
pathways, implement it in BOTH places.

## Key Files Reference

| File | What it does |
|------|-------------|
| `hermes_cli/config.py` | Config schema, defaults, validation, `load_config()`, `_normalize_custom_provider_entry()` |
| `hermes_cli/auth.py` | `ProviderConfig`, `PROVIDER_REGISTRY`, `_resolve_api_key_provider_secret()` |
| `hermes_cli/runtime_provider.py` | `resolve_runtime_provider()`, `_resolve_named_custom_runtime()`, `_get_named_custom_provider()` |
| `agent/auxiliary_client.py` | Auxiliary model client construction, `_resolve_api_key_provider()` |
| `agent/agent_init.py` | `init_agent()` — agent construction with credential routing |
| `agent/prompt_builder.py` | `build_skills_system_prompt()`, system prompt assembly |
| `agent/system_prompt.py` | Three-tier prompt assembly: `build_system_prompt_parts()` |
| `agent/credential_pool.py` | Pooled credential management, env var seeding |
| `agent/toon_lite.py` | TOON-lite compact format for skills/memory |
| `agent/skill_router.py` | Routing table format for skills (`format_skills_routing_table()`) |

## Testing Patterns

```bash
# Config tests
python -m pytest tests/hermes_cli/test_config.py -o 'addopts=' -q

# Auxiliary / provider tests
python -m pytest tests/agent/test_auxiliary_named_custom_providers.py \
  tests/hermes_cli/test_aux_config.py -o 'addopts=' -q

# Prompt builder tests
python -m pytest tests/agent/test_prompt_builder.py -o 'addopts=' -q

# Specific test with verbose output
python -m pytest tests/hermes_cli/test_config.py::TestClassName::test_name \
  -o 'addopts=' -v --tb=short
```

After any code change, verify with `python -c "from hermes_cli.auth import ..."`
to catch import-level errors before running the full suite.

## Reference Documents

- [references/external-project-analysis.md](references/external-project-analysis.md) —
  Analysis of three external AI coding projects (vibecode-pro-max-kit, filetree-skill,
  cc-fleet) and their applicable design patterns for Hermes.
