#!/usr/bin/env python3
"""
API Key Testing Script for YT-Hoover
Tests YouTube API key validity and saves it if valid
"""

import sys
import json
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.yt_hoover import YouTubeAnalyzer
except ImportError as e:
    print(f"Error importing YT-Hoover modules: {e}")
    sys.exit(1)

def save_api_key(api_key: str) -> bool:
    """Save API key to config file"""
    config_file = Path.home() / '.yt-hoover-config.json'
    config = {}
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except:
            pass
    
    config['youtube_api_key'] = api_key
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving API key: {e}")
        return False

def test_api_key(api_key: str) -> bool:
    """Test if API key is valid"""
    try:
        analyzer = YouTubeAnalyzer(api_key)
        result = analyzer.youtube_extractor.get_video_metadata("dQw4w9WgXcQ")
        
        if 'error' in result:
            print(f"API key test failed: {result['error']}")
            return False
        else:
            print("✅ API key is valid!")
            return True
    except Exception as e:
        print(f"API key test failed: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python test_api_key.py <API_KEY>")
        sys.exit(1)
    
    api_key = sys.argv[1].strip()
    
    if not api_key:
        print("Error: Empty API key provided")
        sys.exit(1)
    
    print("Testing YouTube API key...")
    
    if test_api_key(api_key):
        if save_api_key(api_key):
            print("✅ API key saved successfully!")
            sys.exit(0)
        else:
            print("⚠️  API key is valid but could not be saved")
            sys.exit(1)
    else:
        print("❌ API key is invalid")
        sys.exit(1)

if __name__ == "__main__":
    main()

