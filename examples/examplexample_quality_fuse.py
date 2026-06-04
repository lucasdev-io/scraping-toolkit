"""
example_quality_fuse.py

Demonstrates the QualityFuse circuit breaker pattern.

Before writing scraped records to the database, QualityFuse checks
that required fields are populated above a minimum threshold (default 50%).
If quality drops — e.g. the site changed its HTML structure — the fuse
trips, blocks the DB write, and fires a Telegram alert instead of
silently overwriting good data with garbage.

Part of lucasdev-io/scraping-toolkit
"""

from scraping_toolkit.telegram_alerter import TelegramAlerter
from scraping_toolkit.quality_fuse import QualityFuse


def write_to_database(records: list[dict]):
    """Placeholder — replace with your Supabase / Postgres upsert."""
    print(f"  📦 Writing {len(records)} records to DB")


def main():
    alerter = TelegramAlerter(
        script_name="example_crawler",
        bot_token="YOUR_BOT_TOKEN",   # loaded from env in production
        chat_id="YOUR_CHAT_ID",
    )
    fuse = QualityFuse(alerter, threshold=0.5)

    # Simulate a batch where the site layout partially broke
    scraped_events = [
        {"title_en": "BTS World Tour", "official_url": "https://..."},
        {"title_en": "BLACKPINK Concert", "official_url": "https://..."},
        {"title_en": "",  "official_url": ""},   # broken — missing fields
        {"title_en": "",  "official_url": ""},   # broken
        {"title_en": "",  "official_url": ""},   # broken
    ]

    # 3 out of 5 records are missing title_en → 60 % empty > 50 % threshold
    # QualityFuse will trip and block the write
    if fuse.check(scraped_events, required_fields=["title_en", "official_url"]):
        write_to_database(scraped_events)
    else:
        print("  ⚡ Fuse tripped — DB write skipped to protect existing data")

    print(f"\n  fuse.triggered = {fuse.triggered}")
    # → True; the run logger will record this as status='fuse'


if __name__ == "__main__":
    main()
