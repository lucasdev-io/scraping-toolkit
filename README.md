# scraping-toolkit

A production-grade Python toolkit I use across all my web scraping projects.
Built from real crawler work — not a demo.

**Stats from active production system:**
- 8 live scrapers running in production
- 44,871+ n8n workflow executions
- 0.6% failure rate

---

## Why this exists

Every scraping project needs the same plumbing: error alerts, circuit breakers, DB logging, anti-detect browser handling. I extracted these from my IdolPulse project (scraping 8 platforms) and packaged them so every new project starts solid instead of from scratch.

---

## Modules

### `TelegramAlerter` — real-time error alerts
Sends immediate alerts on crashes, batches 403 warnings to avoid noise.
```python
alerter = TelegramAlerter(script_name='my_crawler', category='news', hint='Check site X')
alerter.alert('HTTP 503 unavailable')   # fires immediately
alerter.record_403('page-slug')         # queued
alerter.flush_403()                     # sends all 403s in one message
```

### `QualityFuse` — circuit breaker for bad data
Blocks database writes when required fields are missing in more than 50% of records. Prevents garbage data from polluting the DB silently.
```python
fuse = QualityFuse(alerter, threshold=0.5)
if fuse.check(records, ['title', 'url']):
    write_to_db(records)
```

### `SupabaseLogger` — lazy DB client + run logging
Connection opens only on first use — dry-run scripts never touch the database.
```python
db = SupabaseLogger(environment='vps')
db = SupabaseLogger(dry_run=True)   # prints instead of writing

db.log_run(
    script='my_crawler',
    status='success',     # 'success' | 'fuse' | 'error'
    records_count=42,
    blocked_403=alerter.blocked_403,
    fuse_triggered=fuse.triggered,
)
```

### `browser_utils` — Playwright UA rotation + 403 retry
Handles anti-detect browser setup and automatic retry on 403 blocks.
```python
ctx = await make_browser_context(browser, referer='https://target-site.com/')
title, body = await fetch_with_retry(page, url)

if title is None:
    alerter.record_403(slug)   # persistent block — caller decides next step
```

### `text_utils` — HTML cleaning + translation
```python
clean_html('<b>Hello &amp; World</b>')   # → 'Hello & World'
translate_to_zh('BTS 새 앨범 발매')      # → '少年時代 新專輯發行'
```

### `artist_utils` — keyword matching against DB
Builds a keyword map from the artists table and matches event titles.
```python
keywords = load_artist_keywords(db.client())
artist_id = match_artist(title, keywords)   # str | None
```

### `event_utils` — event type detection
```python
detect_event_type('BTS Fanmeet Seoul 2025')   # → 'fanmeet'
detect_event_type('BLACKPINK World Tour')      # → 'concert'
```

---

## Standard script template

Every project I deliver follows this pattern — consistent error handling, logging, and alerting out of the box.

```python
from scraping_toolkit import TelegramAlerter, QualityFuse, SupabaseLogger

alerter = TelegramAlerter('my_crawler', category='news', hint='Check site X')
fuse    = QualityFuse(alerter)
db      = SupabaseLogger(environment='vps')

_count, _error = 0, None
try:
    items = fetch_items()
    if fuse.check(items, ['title', 'url']):
        _count = write_items(db.client(), items)
    alerter.flush_403()
except Exception as e:
    alerter.alert(f'Script crashed: {e}')
    _error = str(e)
    raise
finally:
    db.log_run(
        script='my_crawler',
        status='error' if _error else ('fuse' if fuse.triggered else 'success'),
        records_count=_count,
        blocked_403=alerter.blocked_403,
        fuse_triggered=fuse.triggered,
        error_message=_error,
    )
```

---

## Stack

Python · Playwright · BeautifulSoup · Supabase · n8n · Telegram Bot API

---

## Work with me

I build custom web scrapers and automation workflows for clients on Upwork and Fiverr.

- **Upwork:** [AI Automation & Data Engineer](https://www.upwork.com/freelancers/~01b6e64088ec0af08c)
- **Fiverr:** [@lucasdev_tw](https://www.fiverr.com/lucasdev_tw)
