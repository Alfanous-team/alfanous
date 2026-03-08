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


class TestQSESingleton(unittest.TestCase):
    """Tests that the QSE engine is a true singleton regardless of call style."""

    def setUp(self):
        """Clear the QSE instance cache before each test."""
        data._QSE_INSTANCES.clear()

    def tearDown(self):
        """Clear the QSE instance cache after each test."""
        data._QSE_INSTANCES.clear()

    def test_qse_no_args_and_explicit_path_return_same_instance(self):
        """QSE() and QSE(paths.QSE_INDEX) must return the exact same object.

        Before the fix, lru_cache keyed on the *exact* arguments so the two
        calling styles produced different cache keys and thus separate engine
        instances — each opening the Whoosh index from disk.
        """
        e_default = data.QSE()
        e_explicit = data.QSE(paths.QSE_INDEX)
        self.assertIs(
            e_default, e_explicit,
            "QSE() and QSE(paths.QSE_INDEX) must return the same engine instance "
            "(index must not be opened twice)."
        )

    def test_qse_repeated_calls_return_same_instance(self):
        """Repeated QSE() calls return the same engine instance (no re-loading)."""
        e1 = data.QSE()
        e2 = data.QSE()
        e3 = data.QSE()
        self.assertIs(e1, e2)
        self.assertIs(e2, e3)

    def test_qse_only_one_entry_in_cache(self):
        """After calling both QSE() and QSE(path), the cache holds exactly one entry."""
        data.QSE()
        data.QSE(paths.QSE_INDEX)
        self.assertEqual(
            len(data._QSE_INSTANCES), 1,
            "Two call styles for the same path must share a single cache entry."
        )


if __name__ == '__main__':
    unittest.main()
