# MemOS Hermes Multi-Profile Deployment Recipe

> Tested 2026-05-16: MemOS 2.0.4 local-plugin on Hermes with chuck/wawa/default profiles.

## Architecture

```
~/.hermes/
├── hermes-agent/plugins/memory/memtensor → shared symlink (once)
├── profiles/
│   ├── chuck/home/.hermes/memos-plugin/    ← data + config (unique)
│   └── wawa/home/.hermes/memos-plugin/     ← data + config (unique)
└── home/.hermes/memos-plugin/              ← default profile data
```

**Key insight**: install.sh changes `HOME` to `<hermes_home>/home/`, then creates `.hermes/memos-plugin/` inside that. So the runtime data lands at `<hermes_home>/home/.hermes/memos-plugin/`.

## Step 1: Install Plugin Code (once)

```bash
cd <repo>/apps/memos-local-plugin
bash install.sh --version 2.0.4
# Auto-detects Hermes, deploys to active profile's home
# Creates symlink: plugins/memory/memtensor → adapters/hermes/memos_provider
```

## Step 2: Multi-Profile Data Directories

The installer only sets up the ACTIVE profile. For extra profiles, **do NOT run the installer again** (it stops gateways, re-downloads npm packages).

Instead, symlink-share the code (415MB node_modules) and only keep unique data:

```bash
CHUCK_MEMOS="~/.hermes/profiles/chuck/home/.hermes/memos-plugin"

for profile in wawa default; do
  case $profile in
    wawa)   TARGET="~/.hermes/profiles/wawa/home/.hermes/memos-plugin" ;;
    default) TARGET="~/.hermes/home/.hermes/memos-plugin" ;;
  esac

  mkdir -p "$TARGET"/{data,logs,skills,daemon}

  # Symlink all code dirs from chuck (skip data/ config/ daemon/ logs/ skills/)
  for item in $(ls "$CHUCK_MEMOS"); do
    case "$item" in
      config.yaml|data|logs|skills|daemon) continue ;;
    esac
    ln -s "$CHUCK_MEMOS/$item" "$TARGET/$item"
  done
done
```

Saves ~830MB (no duplicate node_modules).

## Step 3: MemOS Runtime Config (per profile)

```yaml
# <hermes_home>/home/.hermes/memos-plugin/config.yaml
version: 1

viewer:
  port: 18800           # unique per profile: 18800(chuck) 18801(wawa) 18802(default)

embedding:
  provider: openai_compatible
  apiKey: "<DASHSCOPE_API_KEY>"
  baseUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  model: "text-embedding-v3"
  dimensions: 1024

llm:
  provider: openai_compatible
  apiKey: "<DASHSCOPE_API_KEY>"
  baseUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  model: "qwen-plus"    # good balance for extraction tasks

algorithm:
  lightweightMemory:
    enabled: false       # FALSE = full L1→L3→Skills self-evolution

hub:
  enabled: false

telemetry:
  enabled: true

logging:
  level: info
  detailedView: false
```

**Pitfall**: `lightweightMemory.enabled: true` (the default) only does low-cost summaries — no trace/policy/world model/skill. Must be `false` for self-evolution.

## Step 4: Enable in Hermes Config

Each profile's `config.yaml` needs:
```yaml
memory:
  provider: memtensor    # changed from ''
```

**Patching pitfall**: `provider: ''` appears multiple times in Hermes config.yaml (model fallback providers, image gen providers, etc.). Provide enough trailing context to make the replacement unique:
```
old: "  memory_char_limit: 2200\n  user_char_limit: 1375\n  provider: ''"
new: "  provider: memtensor"
```
Then restore removed lines in a second patch.

## Step 5: Restart Gateways

```bash
hermes gateway restart --profile default
hermes gateway restart --profile chuck
hermes gateway restart --profile wawa     # will disconnect WeChat session
```

## Verification

- Viewer: `curl http://127.0.0.1:18800` → 200 (chuck), 18801 (wawa), 18802 (default)
- Provider discovery: `python -c 'from plugins.memory import discover_memory_providers; ...'`
- First session triggers bridge startup + data directory initialization
- Data appears at `<hermes_home>/home/.hermes/memos-plugin/data/memos.db`

## Provider Lifecycle

The bridge (Node.js JSON-RPC process) starts lazily — NOT at gateway restart, but on the first `initialize()` call when a chat session begins. The viewer may be unreachable until then.
