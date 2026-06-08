---
name: sirchmunk-intel-mac
description: Install and run Sirchmunk on Intel Mac (x86_64, no GPU). Covers kreuzberg stub workaround, rga install, and environment setup for background processes.
version: 1.0.0
tags: [sirchmunk, macos, intel, workaround]
---

# Sirchmunk on Intel Mac

## Problem

Sirchmunk's dependency `kreuzberg` requires ONNX Runtime prebuilt binaries, which are NOT available for x86_64-apple-darwin. `sentence-transformers` and `modelscope` pull in PyTorch (~2GB) which is unnecessary for code search.

## Install Steps

```bash
# 1. Install sirchmunk WITHOUT dependencies
pip install --no-deps sirchmunk

# 2. Install only needed deps (skip kreuzberg, sentence-transformers, modelscope)
pip install loguru fastapi "uvicorn[standard]" openai genson pillow \
  pypdf pandas parquet numpy msgpack sentencepiece tqdm rapidfuzz \
  duckdb python-docx openpyxl python-pptx charset-normalizer python-multipart

# 3. Create kreuzberg stub
mkdir -p venv/lib/python3.11/site-packages/kreuzberg
cat > venv/lib/python3.11/site-packages/kreuzberg/__init__.py << 'EOF'
"""Stub for kreuzberg — plain text extraction for sirchmunk."""
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
        return ExtractionResult(content=f"[Cannot extract: {path.name}]", mime_type="application/octet-stream")
EOF

# 4. Install rga (ripgrep-all) — required by sirchmunk
RGA_VER=$(curl -sL https://api.github.com/repos/phiresky/ripgrep-all/releases/latest | grep tag_name | head -1 | cut -d'"' -f4)
curl -sL "https://github.com/phiresky/ripgrep-all/releases/download/${RGA_VER}/ripgrep_all-${RGA_VER}-x86_64-apple-darwin.tar.gz" -o /tmp/rga.tar.gz
tar xzf /tmp/rga.tar.gz -C /tmp/rga_extract
find /tmp/rga_extract -name "rga" -type f -exec cp {} ~/bin/rga \;
chmod +x ~/bin/rga
```

## Usage

```python
from sirchmunk import AgenticSearch
from sirchmunk.llm import OpenAIChat

llm = OpenAIChat(api_key=..., base_url=..., model=...)
searcher = AgenticSearch(llm=llm, paths=["/path/to/code"], reuse_knowledge=False)
result = await searcher.search(query="...", mode="FAST")
```

Must pass `reuse_knowledge=False` to skip embedding initialization.

## Pitfalls

- Background processes need `REAL_HOME=/Users/macbook HOME=/Users/macbook` to avoid Hermes profile home override
- kreuzberg stub only handles text files; PDF/DOCX/XLSX extraction will return stub content
- rga (not rg) is required — sirchmunk checks for BOTH
- DEEP mode may return "No results found" when Monte Carlo sampling converges on wrong regions
