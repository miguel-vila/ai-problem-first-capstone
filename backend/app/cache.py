import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import os

class OverviewCache:
    def __init__(self, db_path: Optional[str] = None, ttl_days: int = 7):
        """
        Initialize the overview cache with SQLite backend.

        Args:
            db_path: Path to SQLite database file. Defaults to 'cache/overview_cache.db'
            ttl_days: Time-to-live for cached entries in days. Defaults to 7 (1 week)
        """
        if db_path is None:
            # Use a cache directory in the project root
            cache_dir = Path(__file__).parent.parent / 'cache'
            cache_dir.mkdir(exist_ok=True)
            db_path = str(cache_dir / 'overview_cache.db')

        self.db_path = db_path
        self.ttl_days = ttl_days
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS overview_cache (
                    ticker_symbol TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    cached_at TIMESTAMP NOT NULL
                )
            """)
            conn.commit()

    def get(self, ticker_symbol: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached overview data for a ticker symbol.

        Args:
            ticker_symbol: The stock ticker symbol

        Returns:
            Cached data as dict if found and not expired, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data, cached_at FROM overview_cache WHERE ticker_symbol = ?",
                (ticker_symbol.upper(),)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            data_json, cached_at_str = row
            cached_at = datetime.fromisoformat(cached_at_str)

            # Check if cache has expired
            if datetime.now() - cached_at > timedelta(days=self.ttl_days):
                # Cache expired, delete it
                conn.execute(
                    "DELETE FROM overview_cache WHERE ticker_symbol = ?",
                    (ticker_symbol.upper(),)
                )
                conn.commit()
                return None

            return json.loads(data_json)

    def set(self, ticker_symbol: str, data: Dict[str, Any]):
        """
        Cache overview data for a ticker symbol.

        Args:
            ticker_symbol: The stock ticker symbol
            data: The overview data to cache
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO overview_cache (ticker_symbol, data, cached_at)
                VALUES (?, ?, ?)
                """,
                (ticker_symbol.upper(), json.dumps(data), datetime.now().isoformat())
            )
            conn.commit()

    def clear(self, ticker_symbol: Optional[str] = None):
        """
        Clear cache entries.

        Args:
            ticker_symbol: If provided, clear only this ticker's cache.
                         If None, clear all cache entries.
        """
        with sqlite3.connect(self.db_path) as conn:
            if ticker_symbol:
                conn.execute(
                    "DELETE FROM overview_cache WHERE ticker_symbol = ?",
                    (ticker_symbol.upper(),)
                )
            else:
                conn.execute("DELETE FROM overview_cache")
            conn.commit()

    def cleanup_expired(self):
        """Remove all expired cache entries."""
        cutoff_time = datetime.now() - timedelta(days=self.ttl_days)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM overview_cache WHERE cached_at < ?",
                (cutoff_time.isoformat(),)
            )
            conn.commit()
