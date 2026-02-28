"""
Test module for memory caching functionality in alfanous.data module.

This module tests that JSON loading functions properly use LRU cache 
to avoid redundant file I/O.
"""

import unittest
from unittest.mock import patch, mock_open
from alfanous import data
from alfanous import paths


class TestJSONFunctionCaching(unittest.TestCase):
    """Test caching behavior of JSON loading functions."""

    def setUp(self):
        """Clear LRU caches before each test."""
        data.recitations.cache_clear()
        data.translations.cache_clear()
        data.hints.cache_clear()
        data.stats.cache_clear()
        data.information.cache_clear()
        data.ai_query_translation_rules.cache_clear()

    def test_recitations_uses_cache(self):
        """Test that recitations() uses cache on repeated calls."""
        mock_data = '{"rec1": "value1"}'
        
        with patch('builtins.open', mock_open(read_data=mock_data)) as mock_file:
            # First call - should read from file
            result1 = data.recitations()
            assert result1 == {"rec1": "value1"}
            assert mock_file.call_count == 1
            
            # Second call - should use cache, not read file again
            result2 = data.recitations()
            assert result2 == {"rec1": "value1"}
            assert mock_file.call_count == 1  # Still 1, not 2
            
            # Verify both results are the same object (cached)
            assert result1 is result2

    def test_translations_uses_cache(self):
        """Test that translations() uses cache on repeated calls."""
        mock_data = '{"trans1": "value1"}'
        
        with patch('builtins.open', mock_open(read_data=mock_data)) as mock_file:
            result1 = data.translations()
            result2 = data.translations()
            
            # File should only be opened once
            assert mock_file.call_count == 1
            # Results should be identical (cached)
            assert result1 is result2

    def test_hints_uses_cache(self):
        """Test that hints() uses cache on repeated calls."""
        mock_data = '{"hint1": "value1"}'
        
        with patch('builtins.open', mock_open(read_data=mock_data)) as mock_file:
            result1 = data.hints()
            result2 = data.hints()
            
            assert mock_file.call_count == 1
            assert result1 is result2

    def test_stats_uses_cache(self):
        """Test that stats() uses cache on repeated calls."""
        mock_data = '{"stat1": "value1"}'
        
        with patch('builtins.open', mock_open(read_data=mock_data)), \
             patch('os.path.exists', return_value=True):
            result1 = data.stats()
            result2 = data.stats()
            
            # File should only be opened once (cache hit on second call)
            assert result1 is result2

    def test_information_uses_cache(self):
        """Test that information() uses cache on repeated calls."""
        mock_data = '{"info1": "value1"}'
        
        with patch('builtins.open', mock_open(read_data=mock_data)) as mock_file:
            result1 = data.information()
            result2 = data.information()
            
            assert mock_file.call_count == 1
            assert result1 is result2

    def test_ai_query_translation_rules_uses_cache(self):
        """Test that ai_query_translation_rules() uses cache on repeated calls."""
        mock_content = "rule1\nrule2\nrule3"
        
        with patch('builtins.open', mock_open(read_data=mock_content)) as mock_file:
            result1 = data.ai_query_translation_rules()
            result2 = data.ai_query_translation_rules()
            
            assert mock_file.call_count == 1
            assert result1 is result2
            assert result1["content"] == mock_content

    def test_cache_respects_different_paths(self):
        """Test that cache differentiates between different file paths."""
        mock_data1 = '{"data": "from_file1"}'
        mock_data2 = '{"data": "from_file2"}'
        
        def mock_open_with_path(path, *args, **kwargs):
            if 'file1' in str(path):
                return mock_open(read_data=mock_data1)()
            else:
                return mock_open(read_data=mock_data2)()
        
        with patch('builtins.open', side_effect=mock_open_with_path):
            result1 = data.recitations(path='file1.json')
            result2 = data.recitations(path='file2.json')
            
            # Results should be different for different paths
            assert result1 != result2

    def test_cache_info_available(self):
        """Test that cache_info() method is available for inspection."""
        # Clear cache first
        data.recitations.cache_clear()
        
        # Check initial cache state
        cache_info = data.recitations.cache_info()
        assert cache_info.hits == 0
        assert cache_info.misses == 0
        
        # Mock the file and make first call
        mock_data = '{"test": "data"}'
        with patch('builtins.open', mock_open(read_data=mock_data)):
            data.recitations()
            cache_info = data.recitations.cache_info()
            assert cache_info.misses == 1
            assert cache_info.hits == 0
            
            # Second call should hit cache
            data.recitations()
            cache_info = data.recitations.cache_info()
            assert cache_info.misses == 1
            assert cache_info.hits == 1


if __name__ == '__main__':
    unittest.main()
