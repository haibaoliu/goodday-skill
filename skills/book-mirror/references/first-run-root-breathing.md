# First Run: 根本呼吸法 (2026-05-23)

## 输入

- 文件: `根本呼吸法（文字参考）.pdf` (174KB / 8 页)
- 类型: 中文参考文档
- 结构: 4 个节（导论、原理、功法、练习要点）

## 提取

- pdftotext 不可用 → 用 PyPDF2 (`pip install PyPDF2` 到 hermes venv)
- 提取成功: 4048 chars, ~159 "words"（中文不计空格，实际约 11K 字符）
- 分割: awk 失败（中文编码问题）→ Python `re.split(r'\n(?=一、|二、|三、|四[，,])')` 成功切为 4 节

## 上下文

- USER.md (1080 bytes): Chuck, 程序员/PM, 深圳, 已婚8岁儿子, 四口之家
- SOUL.md (669 bytes): 禁绝对化口吻, 偏悲观
- 人物页: wife, son, mother, mother-in-law
- 反思/模式页: 无（brain 新建）
- 总上下文: 3,547 bytes / 137 lines

## 子 Agent 分析

- 4 节，分两批: 3 + 1（delegate_task batch 限 3）
- 工具集: `['terminal', 'file']`（只读）
- 模型: deepseek-v4-pro
- 耗时: ~90s（第一批 3 个并行）, ~41s（第四段单独）
- 成本: ~$0.02 total

### 子 Agent 输出处理

- Task 0 (导论): 返回在 summary → 直接使用 ✅
- Task 1 (原理): summary 说写入了文件 `/原理_Chuck分析.md` → 需额外 `read_file` 读取 ⚠️
- Task 2 (功法): 返回在 summary → 直接使用 ✅
- Task 3 (练习要点): 返回在 summary → 直接使用 ✅

## 输出

- 文件: `~/.hermes/brain/books/root-breathing-personalized.md`
- 大小: 16,230 bytes
- 格式: YAML frontmatter + 4 节双栏表格
- 右栏质量: 高 — 多次引用 Chuck 的编程思维（死循环类比, while-break, full stack, 30/70 维护比）和家庭生活（四人同住、陪儿子写作业、科技园堵车）

## 经验教训

1. **pdftotext 不是标配** — macOS 需备 PyPDF2
2. **awk 分割中文不可靠** — Python regex 更稳
3. **子 Agent 可能写文件** — 拼装时检查 summary + 磁盘
4. **短文也能跑** — 4 节就够了，不需要强行分章
5. **上下文不需要大** — 3.5K 足以产生丰富映射，关键是密度
6. **SOUL.md 约束生效** — 右栏全程无"你必须""你应该"，语调保持推测性
