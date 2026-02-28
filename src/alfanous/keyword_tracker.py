"""
Keyword Tracker Module

This module provides functionality to track and store search keywords
for analytics and autocomplete features. It uses a simple JSON file-based
storage for persistence.
"""

import json
import os
import threading
import time
from typing import Dict, List, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class KeywordTracker:
    """
    Tracks search keywords with their frequency and last search time.
    Thread-safe implementation using locks for concurrent access.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the keyword tracker.
        
        Args:
            storage_path: Path to the JSON file for storing keywords.
                         If None, uses default path in user's home directory.
        """
        if storage_path is None:
            # Default storage in a hidden directory in home folder
            home_dir = os.path.expanduser("~")
            alfanous_dir = os.path.join(home_dir, ".alfanous")
            os.makedirs(alfanous_dir, exist_ok=True)
            storage_path = os.path.join(alfanous_dir, "keywords.json")
        
        self.storage_path = storage_path
        self.lock = threading.Lock()
        self.keywords: Dict[str, Dict] = {}
        self._load()
    
    def _load(self):
        """Load keywords from storage file."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.keywords = json.load(f)
                logger.debug(f"Loaded {len(self.keywords)} keywords from storage")
        except Exception as e:
            logger.error(f"Error loading keywords: {e}")
            self.keywords = {}
    
    def _save(self):
        """Save keywords to storage file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.keywords, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved {len(self.keywords)} keywords to storage")
        except Exception as e:
            logger.error(f"Error saving keywords: {e}")
    
    def _normalize_keyword(self, keyword: str) -> str:
        """
        Normalize a keyword for consistent tracking.
        
        Args:
            keyword: The raw keyword string
            
        Returns:
            Normalized keyword string (lowercase, stripped)
        """
        if not keyword:
            return ""
        # Strip whitespace and convert to lowercase for normalization
        return keyword.strip().lower()
    
    def track(self, query: str):
        """
        Track a search query.
        
        Args:
            query: The search query string to track
        """
        if not query or not query.strip():
            return
        
        normalized = self._normalize_keyword(query)
        if not normalized:
            return
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        with self.lock:
            if normalized in self.keywords:
                self.keywords[normalized]["count"] += 1
                self.keywords[normalized]["last_searched"] = timestamp
            else:
                self.keywords[normalized] = {
                    "count": 1,
                    "first_searched": timestamp,
                    "last_searched": timestamp,
                    "original": query.strip()  # Keep original case/form
                }
            
            # Save after every track to ensure persistence
            self._save()
    
    def get_top_keywords(self, limit: int = 10, min_count: int = 1) -> List[Dict]:
        """
        Get the most searched keywords.
        
        Args:
            limit: Maximum number of keywords to return
            min_count: Minimum search count to include
            
        Returns:
            List of keyword dictionaries sorted by count (descending)
        """
        with self.lock:
            # Filter by minimum count and sort by count descending
            filtered = [
                {
                    "keyword": data["original"],
                    "count": data["count"],
                    "first_searched": data["first_searched"],
                    "last_searched": data["last_searched"]
                }
                for keyword, data in self.keywords.items()
                if data["count"] >= min_count
            ]
            
            # Sort by count descending, then by last searched
            filtered.sort(key=lambda x: (-x["count"], x["last_searched"]), reverse=False)
            
            return filtered[:limit]
    
    def get_keyword_count(self, query: str) -> int:
        """
        Get the search count for a specific keyword.
        
        Args:
            query: The keyword to look up
            
        Returns:
            Number of times this keyword was searched
        """
        normalized = self._normalize_keyword(query)
        with self.lock:
            return self.keywords.get(normalized, {}).get("count", 0)
    
    def clear(self):
        """Clear all tracked keywords (mainly for testing)."""
        with self.lock:
            self.keywords = {}
            self._save()


# Global instance for use across the application
_tracker: Optional[KeywordTracker] = None


def get_tracker() -> KeywordTracker:
    """
    Get the global keyword tracker instance.
    
    Returns:
        The global KeywordTracker instance
    """
    global _tracker
    if _tracker is None:
        _tracker = KeywordTracker()
    return _tracker
