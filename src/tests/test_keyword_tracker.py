"""
Tests for the keyword tracker module
"""

import sys
import os
import tempfile
import json

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from alfanous.keyword_tracker import KeywordTracker


class TestKeywordTracker:
    """Tests for KeywordTracker class"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create a temporary file for storage"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def tracker(self, temp_storage):
        """Create a tracker with temporary storage"""
        return KeywordTracker(storage_path=temp_storage)
    
    def test_tracker_initialization(self, tracker):
        """Test that tracker initializes correctly"""
        assert tracker is not None
        assert tracker.keywords == {}
    
    def test_track_single_keyword(self, tracker):
        """Test tracking a single keyword"""
        tracker.track("الله")
        assert tracker.get_keyword_count("الله") == 1
    
    def test_track_multiple_occurrences(self, tracker):
        """Test tracking the same keyword multiple times"""
        tracker.track("الله")
        tracker.track("الله")
        tracker.track("الله")
        assert tracker.get_keyword_count("الله") == 3
    
    def test_track_different_keywords(self, tracker):
        """Test tracking different keywords"""
        tracker.track("الله")
        tracker.track("محمد")
        tracker.track("القرآن")
        
        assert tracker.get_keyword_count("الله") == 1
        assert tracker.get_keyword_count("محمد") == 1
        assert tracker.get_keyword_count("القرآن") == 1
    
    def test_normalization(self, tracker):
        """Test that keywords are normalized (case insensitive)"""
        tracker.track("Allah")
        tracker.track("ALLAH")
        tracker.track("allah")
        
        # Should all be counted as the same keyword
        assert tracker.get_keyword_count("allah") == 3
        assert tracker.get_keyword_count("Allah") == 3
    
    def test_whitespace_handling(self, tracker):
        """Test that whitespace is handled correctly"""
        tracker.track("  الله  ")
        tracker.track("الله")
        
        assert tracker.get_keyword_count("الله") == 2
    
    def test_empty_keyword_ignored(self, tracker):
        """Test that empty keywords are ignored"""
        tracker.track("")
        tracker.track("   ")
        
        assert len(tracker.keywords) == 0
    
    def test_get_top_keywords(self, tracker):
        """Test getting top keywords"""
        # Track various keywords with different counts
        for _ in range(5):
            tracker.track("الله")
        for _ in range(3):
            tracker.track("محمد")
        tracker.track("القرآن")
        
        top = tracker.get_top_keywords(limit=10)
        
        assert len(top) == 3
        assert top[0]["keyword"] == "الله"
        assert top[0]["count"] == 5
        assert top[1]["keyword"] == "محمد"
        assert top[1]["count"] == 3
        assert top[2]["keyword"] == "القرآن"
        assert top[2]["count"] == 1
    
    def test_get_top_keywords_with_limit(self, tracker):
        """Test getting top keywords with limit"""
        tracker.track("keyword1")
        tracker.track("keyword2")
        tracker.track("keyword3")
        
        top = tracker.get_top_keywords(limit=2)
        assert len(top) == 2
    
    def test_get_top_keywords_with_min_count(self, tracker):
        """Test getting top keywords with minimum count filter"""
        for _ in range(5):
            tracker.track("الله")
        for _ in range(2):
            tracker.track("محمد")
        tracker.track("القرآن")
        
        top = tracker.get_top_keywords(min_count=3)
        
        # Only "الله" has count >= 3
        assert len(top) == 1
        assert top[0]["keyword"] == "الله"
    
    def test_keyword_metadata(self, tracker):
        """Test that keyword metadata is stored correctly"""
        tracker.track("الله")
        
        top = tracker.get_top_keywords()
        assert len(top) == 1
        
        keyword = top[0]
        assert "keyword" in keyword
        assert "count" in keyword
        assert "first_searched" in keyword
        assert "last_searched" in keyword
        assert keyword["count"] == 1
    
    def test_persistence(self, temp_storage):
        """Test that keywords persist across tracker instances"""
        # Create first tracker and add keywords
        tracker1 = KeywordTracker(storage_path=temp_storage)
        tracker1.track("الله")
        tracker1.track("محمد")
        
        # Create second tracker with same storage
        tracker2 = KeywordTracker(storage_path=temp_storage)
        
        # Should load the keywords from storage
        assert tracker2.get_keyword_count("الله") == 1
        assert tracker2.get_keyword_count("محمد") == 1
    
    def test_clear(self, tracker):
        """Test clearing all keywords"""
        tracker.track("الله")
        tracker.track("محمد")
        
        assert len(tracker.keywords) > 0
        
        tracker.clear()
        
        assert len(tracker.keywords) == 0
        assert tracker.get_keyword_count("الله") == 0
    
    def test_original_form_preserved(self, tracker):
        """Test that original keyword form is preserved"""
        tracker.track("Allah")
        
        top = tracker.get_top_keywords()
        assert top[0]["keyword"] == "Allah"  # Original case preserved
        
        # But tracking with different case should still increment
        tracker.track("ALLAH")
        assert tracker.get_keyword_count("allah") == 2
