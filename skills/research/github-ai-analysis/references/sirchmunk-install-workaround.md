# Sirchmunk Installation Workaround (Intel Mac, no GPU)

Worked example of the `--no-deps` + stub module pattern documented in the
SKILL.md pitfall. Applied to sirchmunk v0.0.7.post1 on macOS 12.7.6 x86_64.

## Problem

Three heavy dependencies block `pip install sirchmunk`:

1. **sentence-transformers** → torch (200MB+ download, slow resolver on pip)
2. **modelscope** → also pulls torch, massive
3. **kreuzberg** → needs ONNX Runtime (`ort`), no prebuilt binary for `x86_64-apple-darwin`

Even `uv pip install` fails on kreuzberg because its Rust build needs `ort-sys`.

## Solution

### Step 1: Install core without deps, then lightweight deps

```bash
pip install --no-deps sirchmunk
pip install loguru fastapi "uvicorn[standard]" openai genson pillow \
  pypdf pandas parquet numpy msgpack sentencepiece tqdm rapidfuzz \
  duckdb python-docx openpyxl python-pptx charset-normalizer python-multipart
```

Skip: `sentence-transformers`, `modelscope`, `kreuzberg`.

### Step 2: Install system binary (rga)

```bash
# Download prebuilt rga from GitHub releases
RGA_VER=$(curl -sL https://api.github.com/repos/phiresky/ripgrep-all/releases/latest | jq -r .tag_name)
curl -sL "https://github.com/phiresky/ripgrep-all/releases/download/${RGA_VER}/ripgrep_all-${RGA_VER}-x86_64-apple-darwin.tar.gz" -o /tmp/rga.tar.gz
tar xzf /tmp/rga.tar.gz -C /tmp/rga_extract
find /tmp/rga_extract -name "rga" -type f -exec cp {} ~/.local/bin/rga \;
```

### Step 3: Stub kreuzberg module

Create `site-packages/kreuzberg/__init__.py`:

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ExtractionResult:
    content: str
    mime_type: str = "text/plain"

async def extract_file(file_path):
    path = Path(file_path)
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return ExtractionResult(content=content, mime_type="text/plain")
    except Exception:
        return ExtractionResult(content=f"[Cannot extract: {path.name}]")
```

Sirchmunk's `file_utils.py` does `from kreuzberg import ExtractionResult, extract_file` — this stub satisfies that import. The stub falls back to plain `read_text()`, which is fine for code/text file search (sirchmunk's primary use case).

### Step 4: Use `reuse_knowledge=False`

```python
searcher = AgenticSearch(llm=llm, paths=paths, reuse_knowledge=False)
```

This skips `sentence-transformers` / `modelscope` / `EmbeddingUtil` initialization at runtime. Without it, `AgenticSearch.__init__` tries to create an `EmbeddingUtil` which imports `sentence_transformers`.

### Step 5: Fix Path.home() in background processes

When Hermes runs scripts in background, `Path.home()` may resolve to the profile home (`~/.hermes/profiles/<name>/home/`) instead of the real home. Use absolute paths or set `REAL_HOME` + `HOME` env vars:

```bash
REAL_HOME=/Users/macbook HOME=/Users/macbook python script.py
```

## Verification

```python
from sirchmunk import AgenticSearch  # ✅ no ImportError
from sirchmunk.llm import OpenAIChat
searcher = AgenticSearch(llm=llm, reuse_knowledge=False)  # ✅ no EmbeddingUtil crash
```

## Why This Works for Evaluation

For code/text file search, sirchmunk doesn't need:
- `kreuzberg` — only used for PDF/DOCX/XLSX/PPTX extraction via `fast_extract()`
- `sentence-transformers` / `modelscope` — only used for KnowledgeCluster embedding reuse
- `EmbeddingUtil` — only needed when `reuse_knowledge=True`

The core pipeline (GrepRetriever → KnowledgeBase → LLM synthesis) runs fine without these.
