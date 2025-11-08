"""
Cache management utility for stock overview data.

This script allows you to:
- Delete a specific ticker from the cache
- Clear all cache entries
- List all cached tickers
- View cache statistics

Usage:
    python manage_cache.py --delete AAPL
    python manage_cache.py --list
    python manage_cache.py --clear-all
    python manage_cache.py --stats
    python manage_cache.py --cleanup-expired
"""

import argparse
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from app.cache import OverviewCache


def list_cached_tickers(cache: OverviewCache):
    """List all tickers currently in the cache."""
    with sqlite3.connect(cache.db_path) as conn:
        cursor = conn.execute(
            "SELECT ticker_symbol, cached_at FROM overview_cache ORDER BY cached_at DESC"
        )
        rows = cursor.fetchall()

    if not rows:
        print("📭 Cache is empty - no tickers cached")
        return

    print(f"\n📊 Cached Tickers ({len(rows)} total):")
    print("=" * 60)
    print(f"{'Ticker':<10} {'Cached At':<25} {'Age (days)':<15}")
    print("-" * 60)

    now = datetime.now()
    for ticker, cached_at_str in rows:
        cached_at = datetime.fromisoformat(cached_at_str)
        age_days = (now - cached_at).days
        age_hours = (now - cached_at).seconds // 3600

        if age_days == 0:
            age_str = f"{age_hours}h"
        else:
            age_str = f"{age_days}d"

        print(f"{ticker:<10} {cached_at_str:<25} {age_str:<15}")

    print("=" * 60)


def show_cache_stats(cache: OverviewCache):
    """Display cache statistics."""
    with sqlite3.connect(cache.db_path) as conn:
        # Total entries
        cursor = conn.execute("SELECT COUNT(*) FROM overview_cache")
        total_count = cursor.fetchone()[0]

        # Expired entries
        cutoff_time = datetime.now() - timedelta(days=cache.ttl_days)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM overview_cache WHERE cached_at < ?",
            (cutoff_time.isoformat(),)
        )
        expired_count = cursor.fetchone()[0]

        # Oldest and newest entries
        cursor = conn.execute(
            "SELECT MIN(cached_at), MAX(cached_at) FROM overview_cache"
        )
        oldest, newest = cursor.fetchone()

    print("\n📈 Cache Statistics:")
    print("=" * 60)
    print(f"Total entries: {total_count}")
    print(f"Valid entries: {total_count - expired_count}")
    print(f"Expired entries: {expired_count}")
    print(f"TTL: {cache.ttl_days} days")

    if oldest and newest:
        oldest_dt = datetime.fromisoformat(oldest)
        newest_dt = datetime.fromisoformat(newest)
        print(f"Oldest entry: {oldest} ({(datetime.now() - oldest_dt).days} days ago)")
        print(f"Newest entry: {newest} ({(datetime.now() - newest_dt).days} days ago)")

    # Database file size
    db_path = Path(cache.db_path)
    if db_path.exists():
        size_bytes = db_path.stat().st_size
        size_kb = size_bytes / 1024
        print(f"Database size: {size_kb:.2f} KB")

    print("=" * 60)


def delete_ticker(cache: OverviewCache, ticker: str):
    """Delete a specific ticker from the cache."""
    ticker = ticker.upper()

    # Check if ticker exists
    with sqlite3.connect(cache.db_path) as conn:
        cursor = conn.execute(
            "SELECT cached_at FROM overview_cache WHERE ticker_symbol = ?",
            (ticker,)
        )
        row = cursor.fetchone()

    if row is None:
        print(f"❌ Ticker '{ticker}' not found in cache")
        return False

    cached_at = row[0]
    print(f"🔍 Found ticker '{ticker}' (cached at {cached_at})")

    # Delete it
    cache.clear(ticker)
    print(f"✅ Successfully deleted '{ticker}' from cache")
    return True


def clear_all_cache(cache: OverviewCache, confirm: bool = True):
    """Clear all cache entries."""
    if confirm:
        response = input("\n⚠️  Are you sure you want to clear ALL cache entries? (y/n): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Cancelled - no entries deleted")
            return False

    cache.clear()
    print("✅ All cache entries cleared successfully")
    return True


def cleanup_expired_entries(cache: OverviewCache):
    """Remove expired cache entries."""
    # Count before cleanup
    with sqlite3.connect(cache.db_path) as conn:
        cutoff_time = datetime.now() - timedelta(days=cache.ttl_days)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM overview_cache WHERE cached_at < ?",
            (cutoff_time.isoformat(),)
        )
        expired_count = cursor.fetchone()[0]

    if expired_count == 0:
        print("✅ No expired entries to clean up")
        return

    print(f"🧹 Found {expired_count} expired entries (older than {cache.ttl_days} days)")
    cache.cleanup_expired()
    print(f"✅ Successfully removed {expired_count} expired entries")


def main():
    parser = argparse.ArgumentParser(
        description="Manage the stock overview cache",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_cache.py --list                    # List all cached tickers
  python manage_cache.py --delete AAPL             # Delete AAPL from cache
  python manage_cache.py --delete AAPL MSFT TSLA   # Delete multiple tickers
  python manage_cache.py --stats                   # Show cache statistics
  python manage_cache.py --clear-all               # Clear entire cache
  python manage_cache.py --cleanup-expired         # Remove expired entries
        """
    )

    parser.add_argument(
        "--delete",
        "-d",
        nargs="+",
        metavar="TICKER",
        help="Delete specific ticker(s) from cache"
    )

    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List all cached tickers"
    )

    parser.add_argument(
        "--stats",
        "-s",
        action="store_true",
        help="Show cache statistics"
    )

    parser.add_argument(
        "--clear-all",
        action="store_true",
        help="Clear all cache entries (with confirmation)"
    )

    parser.add_argument(
        "--cleanup-expired",
        action="store_true",
        help="Remove expired cache entries"
    )

    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompts"
    )

    args = parser.parse_args()

    # Initialize cache
    cache = OverviewCache()

    # Show header
    print("\n" + "=" * 60)
    print("📦 Stock Overview Cache Manager")
    print("=" * 60)
    print(f"Cache location: {cache.db_path}")
    print(f"TTL: {cache.ttl_days} days")

    # If no arguments provided, show help
    if not any([args.delete, args.list, args.stats, args.clear_all, args.cleanup_expired]):
        print("\n💡 No action specified. Use --help to see available options")
        print("\nQuick actions:")
        print("  --list              List cached tickers")
        print("  --stats             Show statistics")
        print("  --delete TICKER     Delete a ticker")
        return

    # Execute requested actions
    if args.list:
        list_cached_tickers(cache)

    if args.stats:
        show_cache_stats(cache)

    if args.delete:
        print()
        for ticker in args.delete:
            delete_ticker(cache, ticker)

    if args.cleanup_expired:
        print()
        cleanup_expired_entries(cache)

    if args.clear_all:
        print()
        clear_all_cache(cache, confirm=not args.yes)

    print()


if __name__ == "__main__":
    main()
