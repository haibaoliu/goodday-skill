---
name: notebooklm
description: "Interact with Google NotebookLM via notebooklm CLI — login, list, create, chat, source management."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [productivity, google, notebooklm, CLI, research]
    related_skills: [google-workspace, ocr-and-documents]
---

# NotebookLM CLI

Automate Google NotebookLM via the unofficial `notebooklm-py` CLI. Requires browser-based Google OAuth on first login.

## Quick Reference

| Action | Command |
|--------|---------|
| Login (first time) | `notebooklm login` |
| Check auth/status | `notebooklm doctor` |
| List notebooks | `notebooklm list` |
| Set active notebook | `notebooklm use <id-prefix>` |
| Show context | `notebooklm status` |
| Create notebook | `notebooklm create "Title"` |
| Add source (URL) | `notebooklm source add <url>` |
| Add source (file) | `notebooklm source add <file>` |
| Chat with notebook | `notebooklm ask "Question"` |

## Environment

The notebooklm binary lives in the Hermes venv:

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
notebooklm --help
```

Profile data (cookies, storage state) at:
`~/.hermes/profiles/<profile>/home/.notebooklm/profiles/default/storage_state.json`

## Login & Authentication

`notebooklm login` opens a Chromium browser for Google OAuth. The user must complete the login in the browser window manually — this cannot be automated. Authentication is saved to `storage_state.json` on success.

After login, verify with `notebooklm doctor` (all checks should pass) and `notebooklm list` to confirm RPCs work.

## v0.4.1 Bug: Gzip Double-Decode

**Symptom:** All RPC calls (`list`, `create`, `ask`) fail with:
```
Error -3 while decompressing data: incorrect header check (server-error retries exhausted)
```
`notebooklm doctor` shows auth as healthy. Raw `httpx.post` to the same endpoint works fine.

**Root cause:** `_stream_post_with_size_cap` in `_core_transport.py` reads response chunks via `aiter_bytes()` (yields already-decompressed bytes), then rebuilds a fresh `httpx.Response` with `headers=response.headers`. The copied headers still carry `Content-Encoding: gzip`, so downstream `.text` access triggers zlib on already-decoded bytes.

**Fix:** Strip `content-encoding` and `content-length` from headers before constructing the buffered Response. See `references/v0.4.1-gzip-fix.md` for the exact patch. Upstream: [PR #771](https://github.com/teng-lin/notebooklm-py/pull/771) (merged 2026-05-17).

## Pitfalls

- **Login requires GUI browser.** The OAuth flow cannot be automated headlessly. Run `notebooklm login` on the user's desktop session.
- **v0.4.1 needs the gzip patch.** If the package was installed from PyPI (not git `main`), apply the hotfix in `references/v0.4.1-gzip-fix.md` before any RPC calls.
- **Partial IDs work.** `notebooklm use abc` matches `abc123...`. The full UUID is displayed on confirmation.
- **Language sync warning is benign.** `GET_USER_SETTINGS DecodingError` on login doesn't block functionality.

## Related

- [notebooklm-py GitHub](https://github.com/teng-lin/notebooklm-py)
- This user has the `anything-to-notebooklm` project at `~/Documents/hermes-output/anything-to-notebooklm/`
