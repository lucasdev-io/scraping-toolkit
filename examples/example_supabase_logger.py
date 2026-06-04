"""
example_supabase_logger.py

Demonstrates the SupabaseLogger pattern used across all toolkit crawlers.

Key behaviours:
  - Lazy connection: the Supabase client is not created until first use
  - dry_run mode: logs are printed but never written — safe for local testing
  - environment tag: distinguishes runs from different machines (m1, vps, etc.)
  - log_run(): writes a structured row to crawler_logs after every run

Required environment variables:
  SUPABASE_URL
  SUPABASE_SERVICE_KEY

Part of lucasdev-io/scraping-toolkit
"""

import os
from scraping_toolkit.supabase_logger import SupabaseLogger
from scraping_toolkit.quality_fuse import QualityFuse
from scraping_toolkit.telegram_alerter import TelegramAlerter


def run_crawler() -> tuple[list[dict], bool]:
    """Placeholder — returns (records, fuse_triggered)."""
    records = [
        {"title_en": "Example Event A", "official_url": "https://..."},
        {"title_en": "Example Event B", "official_url": "https://..."},
    ]
    return records, False


def main():
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

    # SupabaseLogger is lazy — no network call happens here
    db = SupabaseLogger(dry_run=dry_run, environment="m1")

    alerter = TelegramAlerter(
        script_name="example_crawler",
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
    )
    fuse = QualityFuse(alerter)

    records, _ = run_crawler()

    if fuse.check(records, required_fields=["title_en", "official_url"]):
        # Connection opens here for the first time
        sb = db.client()
        sb.table("events").upsert(records, on_conflict="official_url").execute()
        status = "success"
    else:
        status = "fuse"

    # Always log the run result, regardless of outcome
    db.log_run(
        script="example_crawler",
        status=status,
        records_count=len(records),
        blocked_403=alerter.blocked_403,   # list of slugs that hit 403
        fuse_triggered=fuse.triggered,
    )


if __name__ == "__main__":
    main()
