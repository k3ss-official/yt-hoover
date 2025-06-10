#!/usr/bin/env python3
"""
Basic tests for YT-Hoover
Simple test suite to verify core functionality
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.nlp_processor import AdvancedNLPProcessor

class TestNLPProcessor(unittest.TestCase):
    """Test the NLP processor"""
    
    def setUp(self):
        self.processor = AdvancedNLPProcessor()
    
    def test_url_extraction(self):
        """Test URL extraction"""
        text = "Check out https://github.com/example/repo and www.example.com"
        urls = self.processor.extract_urls(text)
        
        self.assertGreater(len(urls), 0)
        self.assertIn("https://github.com/example/repo", urls)
    
    def test_entity_extraction(self):
        """Test entity extraction"""
        text = "We use Python and React for our web application with MongoDB database"
        result = self.processor.process_text(text)
        
        self.assertIn("Python", result['programming_languages'])
        self.assertGreater(len(result['tools_and_software']), 0)
    
    def test_empty_text(self):
        """Test with empty text"""
        result = self.processor.process_text("")
        
        self.assertEqual(len(result['urls']), 0)
        self.assertEqual(len(result['tools_and_software']), 0)

class TestYouTubeAnalyzer(unittest.TestCase):
    """Test YouTube analyzer (without API calls)"""
    
    def test_video_id_extraction(self):
        """Test video ID extraction from URLs"""
        from src.yt_hoover import YouTubeExtractor
        
        extractor = YouTubeExtractor("dummy_key")
        
        # Test various URL formats
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ]
        
        for url, expected_id in test_cases:
            with self.subTest(url=url):
                video_id = extractor.extract_video_id(url)
                self.assertEqual(video_id, expected_id)

def run_tests():
    """Run all tests"""
    print("🧪 Running YT-Hoover Tests")
    print("=" * 30)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestNLPProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestYouTubeAnalyzer))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 30)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return True
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

