#!/usr/bin/env python3
"""
YT-Hoover CLI - Command Line Interface
Simple and powerful CLI for YouTube video analysis
"""

import asyncio
import argparse
import json
import sys
import os
from pathlib import Path
from typing import List, Optional
import csv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Note: Install 'rich' for better CLI experience: pip install rich")

from src.yt_hoover import YouTubeAnalyzer, AnalysisResult

class YTHooverCLI:
    """Command line interface for YT-Hoover"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.analyzer = None
    
    def print_message(self, message: str, style: str = ""):
        """Print message with optional styling"""
        if self.console:
            self.console.print(message, style=style)
        else:
            print(message)
    
    def print_error(self, message: str):
        """Print error message"""
        if self.console:
            self.console.print(f"❌ {message}", style="red")
        else:
            print(f"ERROR: {message}")
    
    def print_success(self, message: str):
        """Print success message"""
        if self.console:
            self.console.print(f"✅ {message}", style="green")
        else:
            print(f"SUCCESS: {message}")
    
    def print_info(self, message: str):
        """Print info message"""
        if self.console:
            self.console.print(f"ℹ️  {message}", style="blue")
        else:
            print(f"INFO: {message}")
    
    def load_api_key(self, api_key_arg: Optional[str] = None) -> Optional[str]:
        """Load API key from argument, environment, or config file"""
        
        # 1. Command line argument
        if api_key_arg:
            return api_key_arg
        
        # 2. Environment variable
        env_key = os.getenv('YOUTUBE_API_KEY')
        if env_key:
            return env_key
        
        # 3. Config file
        config_file = Path.home() / '.yt-hoover-config.json'
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('youtube_api_key')
            except Exception as e:
                self.print_error(f"Could not read config file: {e}")
        
        return None
    
    def save_api_key(self, api_key: str):
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
            self.print_success(f"API key saved to {config_file}")
        except Exception as e:
            self.print_error(f"Could not save API key: {e}")
    
    def setup_credentials(self):
        """Interactive credential setup"""
        self.print_info("Setting up YouTube API credentials...")
        print()
        
        print("To use YT-Hoover, you need a YouTube Data API v3 key.")
        print("Here's how to get one:")
        print()
        print("1. Go to: https://console.developers.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable 'YouTube Data API v3'")
        print("4. Create credentials (API Key)")
        print("5. Copy the API key")
        print()
        
        api_key = input("Enter your YouTube API key: ").strip()
        
        if not api_key:
            self.print_error("No API key provided")
            return False
        
        # Test the API key
        self.print_info("Testing API key...")
        
        try:
            analyzer = YouTubeAnalyzer(api_key)
            # Test with a known video
            test_result = analyzer.youtube_extractor.get_video_metadata("dQw4w9WgXcQ")
            
            if 'error' in test_result:
                self.print_error(f"API key test failed: {test_result['error']}")
                return False
            else:
                self.print_success("API key is valid!")
                self.save_api_key(api_key)
                return True
                
        except Exception as e:
            self.print_error(f"API key test failed: {e}")
            return False
    
    async def analyze_single_video(self, video_input: str, output_file: Optional[str] = None, 
                                 output_format: str = 'markdown') -> bool:
        """Analyze a single video"""
        
        if not self.analyzer:
            self.print_error("Analyzer not initialized")
            return False
        
        try:
            if self.console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Analyzing video...", total=None)
                    result = await self.analyzer.analyze(video_input)
                    progress.update(task, description="Analysis complete!")
            else:
                print("Analyzing video...")
                result = await self.analyzer.analyze(video_input)
            
            # Generate output
            if output_format == 'json':
                content = result.to_json()
            else:
                content = self.analyzer.generate_report(result, output_format)
            
            # Save or print
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.print_success(f"Results saved to: {output_path}")
            else:
                print("\n" + "="*60)
                print("ANALYSIS RESULTS")
                print("="*60)
                print(content)
            
            # Print summary
            self.print_summary(result)
            return True
            
        except Exception as e:
            self.print_error(f"Analysis failed: {e}")
            return False
    
    async def analyze_batch(self, input_file: str, output_dir: str, 
                          output_format: str = 'markdown') -> bool:
        """Analyze multiple videos from a file"""
        
        if not self.analyzer:
            self.print_error("Analyzer not initialized")
            return False
        
        # Read video list
        try:
            with open(input_file, 'r') as f:
                video_inputs = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.print_error(f"Could not read input file: {e}")
            return False
        
        if not video_inputs:
            self.print_error("No videos found in input file")
            return False
        
        self.print_info(f"Processing {len(video_inputs)} videos...")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Process videos
        successful = 0
        failed = 0
        
        for i, video_input in enumerate(video_inputs, 1):
            try:
                self.print_info(f"Processing video {i}/{len(video_inputs)}: {video_input}")
                
                result = await self.analyzer.analyze(video_input)
                
                # Generate filename
                video_id = result.video_id
                timestamp = result.analysis_timestamp.split('T')[0]  # Date only
                
                if output_format == 'json':
                    filename = f"{video_id}_{timestamp}.json"
                    content = result.to_json()
                else:
                    filename = f"{video_id}_{timestamp}.md"
                    content = self.analyzer.generate_report(result, output_format)
                
                # Save file
                file_path = output_path / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.print_success(f"Saved: {filename}")
                successful += 1
                
            except Exception as e:
                self.print_error(f"Failed to process {video_input}: {e}")
                failed += 1
        
        # Summary
        self.print_info(f"Batch processing complete: {successful} successful, {failed} failed")
        return successful > 0
    
    def print_summary(self, result: AnalysisResult):
        """Print analysis summary"""
        if self.console:
            # Rich table
            table = Table(title="Analysis Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Count", style="green")
            
            table.add_row("URLs Found", str(len(result.urls)))
            table.add_row("Tools & Software", str(len(result.tools_and_software)))
            table.add_row("Programming Languages", str(len(result.programming_languages)))
            table.add_row("Frameworks & Libraries", str(len(result.frameworks_and_libraries)))
            table.add_row("Platforms & Services", str(len(result.platforms_and_services)))
            
            self.console.print(table)
            
            # Video info panel
            info_text = f"""
Title: {result.metadata.title}
Channel: {result.metadata.channel_title}
Views: {int(result.metadata.view_count):,}
Duration: {result.metadata.duration}
            """.strip()
            
            panel = Panel(info_text, title="Video Information", border_style="blue")
            self.console.print(panel)
        else:
            # Simple text output
            print(f"\n📊 Analysis Summary:")
            print(f"   • Title: {result.metadata.title}")
            print(f"   • Channel: {result.metadata.channel_title}")
            print(f"   • Views: {int(result.metadata.view_count):,}")
            print(f"   • URLs found: {len(result.urls)}")
            print(f"   • Tools/Software: {len(result.tools_and_software)}")
            print(f"   • Programming languages: {len(result.programming_languages)}")
    
    def export_csv_summary(self, results: List[AnalysisResult], output_file: str):
        """Export batch results to CSV summary"""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'video_id', 'title', 'channel', 'views', 'duration',
                    'urls_count', 'tools_count', 'languages_count',
                    'frameworks_count', 'platforms_count', 'analysis_date'
                ])
                
                # Data
                for result in results:
                    writer.writerow([
                        result.video_id,
                        result.metadata.title,
                        result.metadata.channel_title,
                        result.metadata.view_count,
                        result.metadata.duration,
                        len(result.urls),
                        len(result.tools_and_software),
                        len(result.programming_languages),
                        len(result.frameworks_and_libraries),
                        len(result.platforms_and_services),
                        result.analysis_timestamp
                    ])
            
            self.print_success(f"CSV summary saved to: {output_file}")
            
        except Exception as e:
            self.print_error(f"Could not save CSV summary: {e}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='YT-Hoover: Extract structured information from YouTube videos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://www.youtube.com/watch?v=VIDEO_ID
  %(prog)s VIDEO_ID --output results.json --format json
  %(prog)s --batch video_list.txt --output-dir ./results/
  %(prog)s --setup  # Setup API credentials
  %(prog)s --gui    # Launch GUI version
        """
    )
    
    # Main arguments
    parser.add_argument('video', nargs='?', help='YouTube video URL or video ID')
    
    # Output options
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['markdown', 'json', 'html'], 
                       default='markdown', help='Output format (default: markdown)')
    
    # Batch processing
    parser.add_argument('--batch', help='Process multiple videos from file (one URL per line)')
    parser.add_argument('--output-dir', help='Output directory for batch processing')
    
    # Configuration
    parser.add_argument('--api-key', help='YouTube API key (overrides saved key)')
    parser.add_argument('--setup', action='store_true', help='Setup API credentials')
    parser.add_argument('--gui', action='store_true', help='Launch GUI version')
    
    # Utility
    parser.add_argument('--version', action='version', version='YT-Hoover 1.0.0')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = YTHooverCLI()
    
    # Handle special commands
    if args.setup:
        success = cli.setup_credentials()
        sys.exit(0 if success else 1)
    
    if args.gui:
        cli.print_info("Launching GUI version...")
        try:
            import subprocess
            subprocess.run([sys.executable, 'src/gui_app.py'])
        except Exception as e:
            cli.print_error(f"Could not launch GUI: {e}")
            cli.print_info("Make sure GUI dependencies are installed")
        return
    
    # Validate arguments
    if not args.video and not args.batch:
        parser.print_help()
        return
    
    # Load API key
    api_key = cli.load_api_key(args.api_key)
    if not api_key:
        cli.print_error("YouTube API key required.")
        cli.print_info("Use --setup to configure credentials, or --api-key KEY")
        cli.print_info("You can also set YOUTUBE_API_KEY environment variable")
        sys.exit(1)
    
    # Initialize analyzer
    try:
        cli.analyzer = YouTubeAnalyzer(api_key)
        if args.verbose:
            cli.print_success("YouTube analyzer initialized")
    except Exception as e:
        cli.print_error(f"Could not initialize analyzer: {e}")
        sys.exit(1)
    
    # Run analysis
    try:
        if args.batch:
            # Batch processing
            if not args.output_dir:
                cli.print_error("--output-dir required for batch processing")
                sys.exit(1)
            
            success = asyncio.run(cli.analyze_batch(
                args.batch, args.output_dir, args.format
            ))
        else:
            # Single video
            success = asyncio.run(cli.analyze_single_video(
                args.video, args.output, args.format
            ))
        
        if success:
            cli.print_success("Analysis completed successfully!")
        else:
            cli.print_error("Analysis failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        cli.print_info("Analysis interrupted by user")
    except Exception as e:
        cli.print_error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

