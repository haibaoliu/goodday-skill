# Hermes Agent 避坑指南 🕳️

> **What · How · Why** — 每个陷阱都回答：**现象是什么、怎么排查修复、为什么会有这个坑**
>
> Hermes 版本: `_config_version: 23` | 最后更新: 2026-05

---

## 前言

Hermes Agent 是一个功能极其丰富的 AI Agent 框架。功能多意味着配置项多、代码路径多、暗坑也多。**最要命的是：很多问题不会报错**——Agent 看起来正常运行，但某些功能悄悄失效了。

这份指南整理了实际使用中遇到的坑，**每个坑按 What · How · Why 三栏拆解**，让阅读者一看就明白。

| 标记 | 含义 |
|------|------|
| 🔴 | 功能完全失效，难以排查 |
| 🟡 | 表面正常但行为不符合预期 |
| 🟢 | 设计约束 / 注意事项，知道就行 |

---

## 一、配置陷阱 (config.yaml)

---

### 🔴 空字符串 `''` 不等于「未设置」

#### What（现象）
`auxiliary.vision.api_key: ''` 写进 config.yaml 后，Vision 功能返回 401 Unauthorized。明明 `.env` 里 `DASHSCOPE_API_KEY` 是正确的，但 Hermes 就是不用。

#### How（排查 & 修复）
```bash
# 1. 检查 config.yaml 中 auxiliary.vision 段
hermes config get auxiliary.vision

# 2. 如果看到 api_key: '' 或 base_url: ''，删掉那行
# ❌ 错误
auxiliary:
  vision:
    api_key: ''        # 空字符串覆盖了 .env 中的值
    base_url: ''        # 同理

# ✅ 正确：不写 api_key / base_url，让系统从 .env 读取
auxiliary:
  vision:
    provider: alibaba
    model: qwen-vl-max
    # api_key 和 base_url 不写 = 自动从环境变量读取
```

**影响范围**：所有 `auxiliary.*` 子项（vision, compression, session_search, skills_hub, approval, mcp, title_generation, triage_specifier, curator）都有这个陷阱。

#### Why（根因）
Hermes 的配置加载逻辑是：`config.yaml` 中的值 > `.env` 环境变量。空字符串 `''` 是一个**有效的值**——它不等于「未设置」。当 Hermes 读到 `api_key: ''`，它会认为「用户明确设置了空 key」，于是不会 fallback 到环境变量。这在 YAML 语义上是正确的，但对用户来说是反直觉的。

---

### 🔴 `streaming.enabled` 和 `display.streaming` 是两个独立开关

#### What（现象）
你在 `display` 段里设了 `streaming: true`，但终端回复还是一次性输出，没有逐字流式效果。

#### How（排查 & 修复）
```bash
hermes config get streaming.enabled
# 如果返回 false，就是被全局开关覆盖了

# 修复：
hermes config set streaming.enabled true
```

#### Why（根因）
```yaml
streaming:
  enabled: false       # ← 全局 API 层开关：false = API 请求不加 stream: true

display:
  streaming: true      # ← UI 层开关：被上面的全局 false 覆盖了，开了也没用
```
两个开关在代码中是 **AND 关系**：`streaming.enabled` 控制 API 请求，`display.streaming` 控制 UI 渲染。全局关了，UI 怎么开都没用。

---

### 🟡 `model.provider` 和 `custom_providers[].name` 的匹配

#### What（现象）
配置看起来没问题，但 Hermes 报 `unknown provider` 或使用了错误的 API 端点。

#### How（排查 & 修复）
```yaml
# ✅ 正确：provider 名和 name 完全对应
model:
  provider: my-deepseek       # ← 必须匹配下面的 name

custom_providers:
  - name: my-deepseek         # ← 必须匹配上面的 provider
    base_url: https://api.deepseek.com
    model: deepseek-chat

# ❌ 错误：provider 写 "deepseek"（这是内置服务商名）
# 同时又定义 custom_providers[].name: "deepseek" → 冲突
```

#### Why（根因）
Hermes 通过 `model.provider` 字符串查找服务商。查找顺序是：内置注册表 → `custom_providers` 列表。内置服务商（deepseek, openrouter, anthropic, openai, google 等）**已经注册**了默认 base_url。如果你在 custom_providers 里用同名，会被忽略（内置优先）。想覆盖内置的 base_url，要么用不同名字，要么设 `providers` 字段。

---

### 🔴 Vision 的 `base_url` 在非 custom provider 下被代码丢弃

#### What（现象）
你用阿里云 DashScope 做 vision，`auxiliary.vision.base_url` 写了 DashScope 的中国端点，但 `vision_analyze` 返回 401。直接 curl 同一个 API key + 端点能通。

#### How（排查 & 修复）
```bash
# 验证 API key 和端点是否能通
curl -s https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-vl-max","messages":[{"role":"user","content":"hi"}]}'

# 如果 curl 能通但 Hermes 里 401 → 就是代码丢弃了 base_url

# 临时修复：伪装成 custom provider
hermes config set auxiliary.vision.provider "custom:alibaba"
```

然后在 `custom_providers` 中添加：
```yaml
custom_providers:
  - name: custom:alibaba
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    model: qwen-vl-max
```

#### Why（根因）
在 `agent/auxiliary_client.py` ~L4472，对于非 `"custom"` 的 provider，代码将 `base_url` 强制设为 `None`，使用内置注册表中的默认地址。DashScope 的国际端点和中国端点不同，API key 可能只在一个端点上有效。这是一个已知的社区报告 bug。

---

### 🔴 DashScope vision 401 完整排查链

#### What（现象）
Vision 功能完全不可用，日志显示 401。

#### How（排查）
按以下顺序逐项排查：

1. `hermes config get auxiliary.vision.api_key` — 如果是空字符串 → 删掉
2. `hermes config get auxiliary.vision.base_url` — 如果是空字符串 → 删掉；如果写了值但 provider 不是 custom → 参考上一条
3. `echo $DASHSCOPE_API_KEY` — 确认环境变量存在且正确
4. 重启 session（`/reset` 或退出 CLI 重进）
5. 如果还是 401 → 用 curl 验证 API key 本身有效

#### Why（根因）
DashScope vision 的 401 有三种可能原因，按概率排序：
1. `api_key: ''` 覆盖了环境变量（最常见）
2. `base_url` 被代码丢弃（非 custom provider）
3. API key 本身过期或无效

**三种原因排查顺序不能乱**——先从最常见最简单的查起。

---

## 二、Memory 机制陷阱

---

### 🟡 写入 Memory 后当前 session 不会立即生效

#### What（现象）
你用 `memory` 工具让 Agent 记住一件事，Agent 说「已保存」。但紧接着问它刚才记了什么，它说「不知道」。

#### How
这不是 bug——是设计如此。下次 session 才会生效。

验证方法：
```bash
# 检查 MEMORY.md 是否真的写入了
cat ~/.hermes/memories/MEMORY.md
```

#### Why（根因）
Hermes 采用 **Frozen Snapshot** 模式：
- 启动时从 `MEMORY.md` / `USER.md` 拍快照 → 注入 system prompt
- Mid-session 的 `memory` 工具调用写入磁盘
- 但 system prompt 中的记忆保持**冻结**，不更新

这是故意的——为了保持 Anthropic prompt cache 稳定（cache 基于 system prompt 前缀，中途修改会 invalidate cache）。

---

### 🟡 Memory 的两个文件和字符硬限制

#### What（现象）
写 memory 时被拒绝，提示超过字符限制。

#### How
```bash
# 查看当前使用量
cat ~/.hermes/memories/MEMORY.md | wc -c   # 上限 2200
cat ~/.hermes/memories/USER.md | wc -c     # 上限 1375

# 手动编辑精简
vim ~/.hermes/memories/MEMORY.md
```

文件位置：
```
~/.hermes/memories/MEMORY.md   → Agent 的个人笔记（用 § 分隔条目）
~/.hermes/memories/USER.md     → 关于用户的了解
```

#### Why（根因）
字符限制是硬编码的（`memory_char_limit: 2200`，`user_char_limit: 1375`），**不是 token 限制而是字符数限制**。这是为了跨模型一致——不同模型的 tokenizer 不同，但字符数是确定的值。选择这个数字是因为它能在注入 system prompt 时留出足够空间给其他内容。

---

### 🔴 Memory 是持久化攻击面

#### What（现象）
如果有人通过 prompt injection 污染了 Memory，所有未来的 session 都会被影响。恶意指令会持续存在于 system prompt 中。

#### How（防御）
```bash
# 定期检查 memory 文件
cat ~/.hermes/memories/MEMORY.md
cat ~/.hermes/memories/USER.md

# 开启 secret 屏蔽
hermes config set security.redact_secrets true

# 如果发现可疑内容，直接编辑删除
vim ~/.hermes/memories/MEMORY.md
```

#### Why（根因）
Memory 直接注入到 system prompt 中，这是 LLM 应用的通病。Hermes 有 `_scan_memory_content()` 做基础防护：
- 拒绝 `ignore previous instructions` 等注入模式
- 拒绝不可见 Unicode 字符（零宽空格、RTL override 等）
- 拒绝 curl/wget 外泄 payload

但这些是**基于正则的**，不能保证 100% 安全。解决方案是定期审计 memory 文件。

---

### 🟢 session_search 和 memory 是不同概念

#### What（现象）
你问 Agent「我们上次讨论过什么」，它用 `memory` 工具查不到，因为那个是查结构化记忆的。

#### How
| 查什么 | 用 `session_search` | 用 `memory` |
|--------|---------------------|-------------|
| 过去对话 transcript | ✅ | ❌ |
| 持久化记忆条目 | ❌ | ✅ |
| 时效 | 随 session 过期 | 永久存在 |
| 保存方式 | 自动（每次对话） | Agent 主动写入 |

#### Why（根因）
两个是完全不同的数据源：`session_search` 查 SQLite 里的对话记录（FTS5 全文搜索），`memory` 查文件系统上的结构化记忆。选择哪个工具取决于你要找的是什么。

---

## 三、安全配置陷阱

---

### 🔴 `security.redact_secrets` 重启才生效

#### What（现象）
你执行了 `hermes config set security.redact_secrets true`，但当前 session 中工具输出仍然显示 API key。

#### How
```bash
# 确认已设置
hermes config get security.redact_secrets

# 退出 CLI 重进，或 /reset
# Gateway 模式：/restart
```

#### Why（根因）
安全配置在 Agent **启动时**加载，mid-session 不变。这是故意的——防止 LLM 在运行中调用 `hermes config set` 把自己的安全开关关掉。**同样的规则适用于所有 `security.*` 配置。**

---

### 🟡 Tirith 可能没装但默认启用

#### What（现象）
默认配置 `tirith_enabled: true`，日志中看到 tirith 相关的错误。

#### How
```bash
# 检查当前设置
hermes config get security.tirith_enabled
hermes config get security.tirith_fail_open

# 如果没装 tirith：
#   tirith_fail_open: true  → 无影响（扫描失败自动放行）
#   tirith_fail_open: false → 所有命令被拒绝！
```

#### Why（根因）
Tirith 是 Nous Research 的命令安全扫描器，默认配置中 `tirith_enabled: true`。设计是安全的：`tirith_fail_open: true` 时，扫描失败（包括没装 tirith）会放行命令。但如果有人把 `tirith_fail_open` 改成 `false` 却没有装 tirith，所有命令都会被拒绝。**保持 `tirith_fail_open: true`。**

---

### 🟡 子代理的审批独立于主 Agent

#### What（现象）
主 Agent 有 `approvals.mode: manual`，你每次危险命令都会确认。但子代理执行危险命令时直接失败了。

#### How
```yaml
delegation:
  subagent_auto_approve: false   # false = 子代理遇到危险命令直接拒绝
```

设为 `true` 信任子代理，或使用 `approvals.mode: smart` 让辅助模型评估风险。

#### Why（根因）
子代理**没有交互界面**——它不能弹确认框让你点 Yes/No。所以 `subagent_auto_approve: false` 意味着危险命令直接拒绝，`true` 意味着无条件放行。折中方案是用 `smart` 审批模式。

---

## 四、服务商/模型陷阱

---

### 🔴 OpenRouter + Copilot token 不通用

#### What（现象）
用 `gh auth login` 拿到的 GitHub token 配置到 OpenRouter，返回 401。

#### How
```bash
# ❌ gh auth token 不能用于 Copilot API
# ✅ 必须用 Copilot 专用 OAuth：
hermes model → GitHub Copilot  # 走 OAuth 流程
```

#### Why（根因）
GitHub 的 Copilot API token 和标准的 GitHub personal access token 是两套认证体系。`gh auth login` 拿到的 token 只能访问 GitHub REST/GraphQL API，不能用于 Copilot Chat API。需要走 Copilot 专用的 OAuth 流程。

---

### 🟡 `model.default` 为空时的自动检测

#### What（现象）
`model.default: ''` 时，Hermes 自动检测的模型不是你想要的。

#### How
```bash
hermes config set model.default "deepseek-v4-pro"
# 或交互选择:
hermes model
```

#### Why（根因）
空字符串触发自动检测逻辑，但检测结果可能不准（取决于服务商返回的默认模型）。建议显式设置 `default`。

---

### 🟢 Context compression 和 Prompt caching 的互动

#### What（现象）
两个都开了，不确定会不会冲突。

#### How
```yaml
prompt_caching:     # 仅 Anthropic/OpenRouter 有效
  cache_ttl: 5m

compression:        # 所有模型有效（用 auxiliary 模型做摘要）
  enabled: true
  threshold: 0.5
```

#### Why（根因）
两者可以共存，协作方式：
1. 当 context 达到 50% → compression 把旧消息压缩成摘要
2. 新的 system prompt + 摘要 → Anthropic 重建 prompt cache
3. 下次对话开始时 cache 命中，省 token

---

## 五、Terminal / 执行环境陷阱

---

### 🟡 `persistent_shell: true` 的副作用

#### What（现象）
你 `cd` 到项目目录，激活了 venv。过了 5 分钟，Agent 突然从错误目录执行命令，venv 也失效了。

#### How
```bash
# 检查 lifetime
hermes config get terminal.lifetime_seconds   # 默认 300 = 5分钟

# 调大
hermes config set terminal.lifetime_seconds 1800  # 30分钟
```

或者在关键命令中显式切换：
```bash
cd /path/to/project && source venv/bin/activate && python script.py
```

#### Why（根因）
`persistent_shell: true` 让同一 session 内的 `cd`、`export`、`source venv` 保留，但 **`lifetime_seconds: 300` 后自动重置**。这是为了防止 shell 状态累积导致不可预测的行为。建议关键操作用绝对路径。

---

### 🟡 Docker backend 的文件权限问题

#### What（现象）
Agent 在 Docker 后端模式下写入的文件，在你的宿主机上属于 `root:root`，你需要 `sudo` 才能操作。

#### How
```yaml
terminal:
  backend: docker
  docker_run_as_host_user: true    # ← 改成 true
```

#### Why（根因）
默认 `docker_run_as_host_user: false` 时容器内以 root 运行。所有 `write_file` / `patch` 创建的文件都归 root。改成 `true` 后容器以你的 UID/GID 运行，文件权限正常。

---

### 🟢 modal/docker 后端：所有文件工具都在容器内

#### What（现象）
`terminal.backend` 不是 `local` 时，`read_file` / `write_file` / `search_files` 看到的路径是**容器内路径**，不是宿主机路径。

#### How
确认你的文件路径在容器内可访问。如果用 `docker_mount_cwd_to_workspace: true`，工作目录会挂载到容器的 `/workspace`。

#### Why（根因）
Hermes 的文件工具跟随 terminal backend——backend 在容器内，文件操作也在容器内。这是为了保证一致性。

---

## 六、Gateway / 平台陷阱

---

### 🔴 Gateway 在 SSH 断开后挂掉

#### What（现象）
SSH 到服务器启动了 Hermes Gateway，断开 SSH 后 Gateway 进程被杀，微信 bot 掉线。

#### How（Linux）
```bash
# 启用 linger 防止 systemd user service 被杀
sudo loginctl enable-linger $USER
```

#### Why（根因）
Linux systemd 默认在用户最后一个 session 退出后杀掉所有 user service。`enable-linger` 让 user service 在用户登出后继续运行。

---

### 🔴 WSL2 上 Gateway 随终端关闭

#### What（现象）
WSL2 中启动 Gateway，关闭 Windows Terminal 后 Gateway 挂掉。

#### How
在 `/etc/wsl.conf` 中添加：
```ini
[boot]
systemd=true
```
然后 `wsl --shutdown` 重启 WSL。

#### Why（根因）
WSL2 默认不启动 systemd，Hermes 的服务管理（`hermes gateway start`）依赖 systemd user service。没有 systemd 时只能 fallback 到 `nohup`，终端一关就挂。

---

### 🟡 Discord bot 静默

#### What（现象）
Discord bot 在线但不响应消息。

#### How
Discord Developer Portal → Bot → Privileged Gateway Intents → 开启 **Message Content Intent**。

#### Why（根因）
Discord 的 Message Content Intent 默认关闭（2022 年后新 bot 的隐私政策要求）。没有这个权限，bot 读不到用户消息内容。

---

### 🟡 Slack bot 只能私聊

#### What（现象）
Slack bot 在私聊中正常工作，但在公开频道中不响应。

#### How
Slack App → Event Subscriptions → 订阅 `message.channels` 事件。

#### Why（根因）
默认只订阅了 `message.im`（私聊）。公开频道需要额外订阅 `message.channels`。

---

### 🟢 WeChat 公众号文章的读取

#### What（现象）
`mp.weixin.qq.com` 文章用 `browser_snapshot` 读经常截断或不完整。

#### How
用 `browser_console` 执行 JS 提取：
```javascript
document.querySelector('#js_content')?.innerText ?? document.body.innerText
```

#### Why（根因）
微信公众号文章的主体内容在 `#js_content` div 里，浏览器 snapshot 的 accessibility tree 对这个 div 的处理经常截断。直接提取 `innerText` 更可靠。

---

## 七、Windows 专项 🪟

---

### 🔴 Alt+Enter 不能插入换行

#### What（现象）
在 TUI 中输入多行消息，按 Alt+Enter 变成了全屏切换。

#### How
用 **Ctrl+Enter** 代替 Alt+Enter。

#### Why（根因）
Windows Terminal 把 Alt+Enter 拦截为全屏切换快捷键。Hermes TUI 的默认多行快捷键也是 Alt+Enter，冲突了。

---

### 🔴 `config.yaml` 带 BOM → HTTP 400

#### What（现象）
用 Windows 记事本编辑 `config.yaml` 后，API 调用返回 `400 "No models provided"`。

#### How
```bash
# 永远用这个命令编辑配置：
hermes config edit
```

#### Why（根因）
Windows 记事本保存 UTF-8 文件时自动加 BOM（Byte Order Mark，`\xEF\xBB\xBF`）。Hermes 的 YAML 解析器不认 BOM，导致文件头三个字节被当做内容，整个配置解析失败。

---

### 🔴 `execute_code` 报 WinError 10106

#### What（现象）
`execute_code` 执行 Python 脚本时抛出 `OSError: [WinError 10106]`。

#### How
新版 Hermes 已修复。如果还在遇到，在 execute_code 脚本开头打印环境变量确认：
```python
import os
print({k: v for k, v in os.environ.items() if k in ('SYSTEMROOT', 'WINDIR')})
```

#### Why（根因）
环境变量清理时误删了 `SYSTEMROOT` / `WINDIR`，Python 的 `socket` 模块需要这些来加载 `mswsock.dll`。新版已修复此问题。

---

### 🟢 Windows 上跑测试

#### What（现象）
`scripts/run_tests.sh` 不工作。

#### How
```bash
# ❌ ./scripts/run_tests.sh    # 找 POSIX venv 路径
# ✅
export PYTHONPATH="$(pwd)"
python -m pytest tests/ -v --tb=short -n 0   # 注意 -n 0 不是 -n 4
```

#### Why（根因）
`run_tests.sh` 里硬编码了 POSIX 路径（`.venv/bin/python`），Windows 上是 `.venv/Scripts/python.exe`。另外 `pyproject.toml` 有默认 `addopts = -n 4`（xdist 并行），Windows 上可能有问题，显式 `-n 0` 禁用。

---

## 八、其他零散坑

---

### 🟡 `human_delay.mode: 'off'` 是全局的

#### What（现象）
`display.streaming: true` 开了但没有打字机效果。

#### How
```bash
hermes config set human_delay.mode random
hermes config set human_delay.min_ms 200
hermes config set human_delay.max_ms 800
```

#### Why（根因）
打字机效果需要 `human_delay` 不为 `off` 配合 `display.streaming`。两者缺一不可。

---

### 🟢 子代理的超时和迭代限制独立配置

#### What（现象）
主 Agent `max_turns: 90`，子代理任务跑到 50 轮就停了。

#### How
```yaml
agent:
  max_turns: 90              # 主 agent
delegation:
  max_iterations: 50         # 子 agent 独立限制
  child_timeout_seconds: 600 # 子 agent 独立超时
```

#### Why（根因）
两个限制独立存在。子代理超时或耗尽迭代 → 返回已有结果，**不会导致主 agent 崩溃**。这是防御性设计——防止一个子代理卡死拖垮整个任务。

---

### 🟡 `prefill_messages_file` 每次对话都注入

#### What（现象）
每次对话开头总有重复的提示内容。

#### How
```bash
hermes config get prefill_messages_file
# 如果指向一个有效文件，每次对话开头都会注入其内容
```

#### Why（根因）
`prefill_messages_file` 中的内容在**每次对话开始时**注入。这是设计特性，不是 bug——用于全局 system prompt 扩展。但要小心不要写入敏感信息。

---

### 🟢 `checkpoints.enabled: false` 意味着 `/rollback` 不可用

#### What（现象）
输入 `/rollback` 无效。

#### How
```bash
hermes config set checkpoints.enabled true
```

#### Why（根因）
文件系统快照需要显式开启。默认关闭是为了省磁盘。开启后才支持 `/rollback`。

---

### 🟡 `tool_loop_guardrails` 的 hard_stop 默认关闭

#### What（现象）
Agent 连续失败同一个操作，一直重试到 `max_turns` 耗尽才停。

#### How
```bash
hermes config set tool_loop_guardrails.hard_stop_enabled true
```

#### Why（根因）
默认只警告（`warnings_enabled: true`），不强制停止（`hard_stop_enabled: false`）。开启硬停止可以在 Agent 死循环时及时中断，省 token。

---

### 🟢 按平台覆盖工具集

#### What（现象）
Gateway 上 WeChat bot 的工具能力比 CLI 少。

#### How
```yaml
platform_toolsets:
  cli: [hermes-cli]          # CLI 全功能
  weixin: [hermes-weixin]    # WeChat 限制
```

#### Why（根因）
`platform_toolsets` 是安全隔离机制。通过限制不同平台的工具集，你可以控制每个平台的能力边界——例如 WeChat bot 不给 terminal 权限。

---

## 快速诊断命令

```bash
# 检查整体健康
hermes doctor --fix

# 检查配置完整性
hermes config check

# 迁移到最新配置格式
hermes config migrate

# 查看所有工具及状态
hermes tools list

# 查看 memory 状态
hermes memory status

# 查看 gateway 日志
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20

# 查看 session 列表
hermes sessions list

# 查看特定配置
hermes config get auxiliary.vision.api_key
```

---

## 贡献

如果你遇到了新的坑，欢迎补充。每个坑请按照 **What · How · Why** 格式记录。

> 社区分享，CC0 授权。不保证完整性，但保证真实性 —— 每个坑都有人掉进去过。
