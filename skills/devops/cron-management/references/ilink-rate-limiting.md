# iLink Rate Limiting Details

## Source

`gateway/platforms/weixin.py` in the hermes-agent codebase.

## Key Constants

```python
RATE_LIMIT_ERRCODE = -2       # iLink frequency limit — backoff and retry
_send_chunk_retries = 4       # max retries (default, env: WEIXIN_SEND_CHUNK_RETRIES)
_send_chunk_retry_delay_seconds = 1.0  # base delay (env: WEIXIN_SEND_CHUNK_RETRY_DELAY_SECONDS)
```

## Retry Logic (lines 1698-1719)

On `ret == -2` or `errcode == -2`:
1. Record as `last_error = RuntimeError("iLink sendmessage rate limited: ...")`
2. If attempts exhausted (≥4), break
3. Wait `_send_chunk_retry_delay_seconds * 3 = 3.0s`
4. Retry

**Max retry window: ~12 seconds** (4 attempts × 3s each).

## Why 5-Minute Spacing Fails

iLink's rate limit window is **minutes-long**, not seconds. Hermes' 12s retry window cannot outlast it. Two messages < rate-limit-window apart → second is rejected through all retries → delivery lost silently.

## Stale Session vs Rate Limit (lines 99-107)

Both use `ret=-2 / errcode=-2`. Distinction:
- `errmsg == "unknown error"` → stale session (same as errcode=-14)
- Any other errmsg → genuine rate limit

## Delivery Error in Cron

The cron scheduler records `last_delivery_error` on failure but does NOT retry delivery later. The job itself completes with `last_status=ok` — the error is in delivery, not execution.

## Fix

Space WeChat cron jobs ≥ 1 hour apart. Verified: 5-min spacing (09:00 + 09:05) produced `ret=-2` on 2026-06-08 for 3 concurrent Monday jobs.

## Chunk Self-Rate-Limiting (Single Job Failure Mode)

Even a single cron job with NO concurrent jobs can hit `ret=-2` if the output message is long enough.

**Mechanism:** The WeChat adapter splits long messages into chunks, each sent as a separate iLink API call with `_send_chunk_delay_seconds = 1.5s` (default) between them. A long message → many chunks → rapid-fire iLink calls → triggers rate limit.

This was observed on 2026-06-06 with the Saturday learning summary cron — it was the ONLY job running, yet still failed with `ret=-2`. The message was a dense report with multiple tables.

**Mitigations:**
1. **Increase chunk delay:** Set `WEIXIN_SEND_CHUNK_DELAY_SECONDS=5.0` (or higher) to slow down chunk delivery
2. **Limit output length:** Keep cron output concise, especially for WeChat delivery. Prefer compact tables over verbose prose.
3. **Offload to file:** For very long reports, save to file and send a short WeChat message with the file path instead.
