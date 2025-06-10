#!/usr/bin/env python3
"""
Credential Setup Script for YT-Hoover
Interactive setup for YouTube API credentials
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

def print_header():
    """Print setup header"""
    print("🎬 YT-Hoover Credential Setup")
    print("=" * 40)
    print()

def print_instructions():
    """Print API key instructions"""
    print("To use YT-Hoover, you need a YouTube Data API v3 key.")
    print("Here's how to get one:")
    print()
    print("1. 🌐 Go to: https://console.developers.google.com/")
    print("2. 📁 Create a new project or select existing")
    print("3. 🔧 Enable 'YouTube Data API v3'")
    print("4. 🔑 Create credentials (API Key)")
    print("5. 📋 Copy the API key")
    print()

def load_existing_config():
    """Load existing configuration"""
    config_file = Path.home() / '.yt-hoover-config.json'
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config(config):
    """Save configuration"""
    config_file = Path.home() / '.yt-hoover-config.json'
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Configuration saved to: {config_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def test_api_key(api_key):
    """Test API key validity"""
    try:
        print("🔍 Testing API key...")
        analyzer = YouTubeAnalyzer(api_key)
        result = analyzer.youtube_extractor.get_video_metadata("dQw4w9WgXcQ")
        
        if 'error' in result:
            print(f"❌ API key test failed: {result['error']}")
            return False
        else:
            print("✅ API key is valid!")
            return True
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

def setup_youtube_api():
    """Setup YouTube API key"""
    config = load_existing_config()
    
    # Check if API key already exists
    existing_key = config.get('youtube_api_key')
    if existing_key:
        print(f"🔑 Found existing API key: {existing_key[:10]}...")
        
        while True:
            choice = input("Test existing key? (y/n/r=replace): ").lower().strip()
            if choice in ['y', 'yes']:
                if test_api_key(existing_key):
                    print("✅ Existing API key is working!")
                    return True
                else:
                    print("❌ Existing API key is not working")
                    break
            elif choice in ['n', 'no']:
                print("ℹ️  Keeping existing key without testing")
                return True
            elif choice in ['r', 'replace']:
                break
            else:
                print("Please enter 'y', 'n', or 'r'")
    
    # Get new API key
    print_instructions()
    
    while True:
        api_key = input("Enter your YouTube API key: ").strip()
        
        if not api_key:
            print("❌ No API key provided")
            continue
        
        if test_api_key(api_key):
            config['youtube_api_key'] = api_key
            if save_config(config):
                print("🎉 YouTube API key setup completed!")
                return True
            else:
                return False
        else:
            retry = input("❌ API key test failed. Try again? (y/n): ").lower().strip()
            if retry not in ['y', 'yes']:
                return False

def setup_optional_features():
    """Setup optional features"""
    config = load_existing_config()
    
    print("\n🔧 Optional Features Setup")
    print("-" * 30)
    
    # AI API keys (optional)
    print("\n🤖 AI Enhancement (Optional)")
    print("You can add AI API keys for enhanced analysis:")
    print("- OpenAI API key for GPT-powered analysis")
    print("- Anthropic API key for Claude-powered analysis")
    print()
    
    setup_ai = input("Setup AI enhancement? (y/n): ").lower().strip()
    if setup_ai in ['y', 'yes']:
        # OpenAI API
        openai_key = input("OpenAI API key (optional, press Enter to skip): ").strip()
        if openai_key:
            config['openai_api_key'] = openai_key
            print("✅ OpenAI API key saved")
        
        # Anthropic API
        anthropic_key = input("Anthropic API key (optional, press Enter to skip): ").strip()
        if anthropic_key:
            config['anthropic_api_key'] = anthropic_key
            print("✅ Anthropic API key saved")
    
    # Default settings
    print("\n⚙️  Default Settings")
    print("Configure default behavior:")
    
    default_format = input("Default output format (markdown/json/html) [markdown]: ").strip() or "markdown"
    config['default_output_format'] = default_format
    
    default_output_dir = input("Default output directory [./output]: ").strip() or "./output"
    config['default_output_dir'] = default_output_dir
    
    # Save configuration
    if save_config(config):
        print("✅ Optional features configured!")
        return True
    else:
        return False

def show_summary():
    """Show setup summary"""
    config = load_existing_config()
    
    print("\n📊 Setup Summary")
    print("=" * 20)
    
    # YouTube API
    if config.get('youtube_api_key'):
        print("✅ YouTube API: Configured")
    else:
        print("❌ YouTube API: Not configured")
    
    # Optional features
    if config.get('openai_api_key'):
        print("✅ OpenAI API: Configured")
    
    if config.get('anthropic_api_key'):
        print("✅ Anthropic API: Configured")
    
    # Settings
    print(f"📁 Default output format: {config.get('default_output_format', 'markdown')}")
    print(f"📂 Default output directory: {config.get('default_output_dir', './output')}")
    
    print("\n🚀 Ready to use YT-Hoover!")
    print("Next steps:")
    print("  ./yt-hoover          # Launch GUI")
    print("  ./yt-hoover web      # Start WebUI")
    print("  ./yt-hoover cli --help  # CLI help")

def main():
    """Main setup function"""
    print_header()
    
    # Check if we're in the right directory
    if not Path("src/yt_hoover.py").exists():
        print("❌ Error: Please run this script from the YT-Hoover root directory")
        sys.exit(1)
    
    try:
        # Setup YouTube API (required)
        if not setup_youtube_api():
            print("❌ YouTube API setup failed")
            sys.exit(1)
        
        # Setup optional features
        setup_optional = input("\nSetup optional features? (y/n): ").lower().strip()
        if setup_optional in ['y', 'yes']:
            setup_optional_features()
        
        # Show summary
        show_summary()
        
        print("\n🎉 Setup completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

