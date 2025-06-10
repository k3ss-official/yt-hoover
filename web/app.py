#!/usr/bin/env python3
"""
Fixed WebUI for YT-Hoover with timeout handling and better error management
"""

import os
import sys
import json
import asyncio
import signal
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS

# Import our modules
try:
    from src.yt_hoover import YouTubeAnalyzer, AnalysisResult
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Error importing modules: {e}")
    MODULES_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Global analyzer instance
analyzer = None

def timeout_handler(signum, frame):
    """Handle timeout for long-running operations"""
    raise TimeoutError("Operation timed out")

def load_config() -> Dict[str, Any]:
    """Load configuration from file"""
    config_file = Path.home() / '.yt-hoover-config.json'
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to file"""
    config_file = Path.home() / '.yt-hoover-config.json'
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except:
        return False

def test_api_key(key: str) -> Dict[str, Any]:
    """Test if API key is valid with timeout"""
    try:
        # Set timeout for API test
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout
        
        test_analyzer = YouTubeAnalyzer(key)
        result = test_analyzer.youtube_extractor.get_video_metadata("dQw4w9WgXcQ")
        
        signal.alarm(0)  # Cancel timeout
        
        if 'error' in result:
            return {'valid': False, 'error': result['error']}
        else:
            return {'valid': True, 'message': 'API key is valid!'}
    except TimeoutError:
        return {'valid': False, 'error': 'API test timed out'}
    except Exception as e:
        signal.alarm(0)  # Cancel timeout
        return {'valid': False, 'error': str(e)}

@app.route('/')
def index():
    """Main page"""
    global analyzer
    
    # Check if API key is configured
    config = load_config()
    api_key = config.get('youtube_api_key') or os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        return render_template('setup.html')
    
    # Initialize analyzer if not already done
    if not analyzer and MODULES_AVAILABLE:
        try:
            analyzer = YouTubeAnalyzer(api_key)
            print("✅ Analyzer initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize analyzer: {e}")
            return render_template('error.html', error=str(e))
    
    return render_template('index.html')

@app.route('/api/setup', methods=['POST'])
def api_setup():
    """Setup API credentials"""
    data = request.get_json()
    api_key = data.get('api_key', '').strip()
    
    if not api_key:
        return jsonify({'success': False, 'error': 'API key is required'})
    
    # Test the API key
    test_result = test_api_key(api_key)
    
    if test_result['valid']:
        # Save the API key
        config = load_config()
        config['youtube_api_key'] = api_key
        
        if save_config(config):
            # Initialize analyzer
            global analyzer
            try:
                analyzer = YouTubeAnalyzer(api_key)
                return jsonify({'success': True, 'message': 'API key saved and verified!'})
            except Exception as e:
                return jsonify({'success': False, 'error': f'Failed to initialize analyzer: {e}'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save API key'})
    else:
        return jsonify({'success': False, 'error': test_result['error']})

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Analyze a single video - simplified version without async operations"""
    global analyzer
    
    if not analyzer:
        return jsonify({'success': False, 'error': 'API key not configured'})
    
    data = request.get_json()
    video_input = data.get('video_url', '').strip()
    
    if not video_input:
        return jsonify({'success': False, 'error': 'Video URL is required'})
    
    try:
        # Extract video ID first (quick operation)
        video_id = analyzer.youtube_extractor.extract_video_id(video_input)
        if not video_id:
            return jsonify({'success': False, 'error': 'Invalid YouTube URL or video ID'})
        
        # Get metadata (should be fast with API)
        metadata_dict = analyzer.youtube_extractor.get_video_metadata(video_id)
        if 'error' in metadata_dict:
            return jsonify({'success': False, 'error': f'Failed to get video metadata: {metadata_dict["error"]}'})
        
        # Process description with NLP (fast operation)
        description = metadata_dict.get('description', '')
        analysis = analyzer.nlp_processor.process_text(description)
        
        # Create simplified result
        result = {
            'video_id': video_id,
            'metadata': metadata_dict,
            'urls': analysis.get('urls', []),
            'tools_and_software': analysis.get('tools_and_software', []),
            'programming_languages': analysis.get('programming_languages', []),
            'frameworks_and_libraries': analysis.get('frameworks_and_libraries', []),
            'platforms_and_services': analysis.get('platforms_and_services', []),
            'companies_and_brands': analysis.get('companies_and_brands', []),
            'file_formats': analysis.get('file_formats', []),
            'apis_and_protocols': analysis.get('apis_and_protocols', []),
            'technical_concepts': analysis.get('technical_concepts', []),
            'extraction_method': 'youtube_api_description_only',
            'analysis_timestamp': datetime.now().isoformat(),
            'confidence_scores': analysis.get('confidence_scores', {})
        }
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export', methods=['POST'])
def api_export():
    """Export analysis results"""
    data = request.get_json()
    result_data = data.get('result')
    format_type = data.get('format', 'markdown')
    
    if not result_data:
        return jsonify({'success': False, 'error': 'No result data provided'})
    
    try:
        if format_type == 'json':
            content = json.dumps(result_data, indent=2)
            filename = f"yt_analysis_{result_data['video_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        elif format_type == 'markdown':
            content = generate_markdown_report(result_data)
            filename = f"yt_analysis_{result_data['video_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        elif format_type == 'html':
            content = generate_html_report(result_data)
            filename = f"yt_analysis_{result_data['video_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        else:
            return jsonify({'success': False, 'error': 'Invalid format type'})
        
        # Save to temporary file
        temp_file = Path(f"/tmp/{filename}")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return send_file(str(temp_file), as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def generate_markdown_report(result: Dict[str, Any]) -> str:
    """Generate markdown report"""
    metadata = result.get('metadata', {})
    
    report = f"""# YouTube Video Analysis Report

## 📹 Video Information
- **Title:** {metadata.get('title', 'Unknown')}
- **Channel:** {metadata.get('channel_title', 'Unknown')}
- **Video ID:** {result.get('video_id', 'Unknown')}
- **Views:** {metadata.get('view_count', '0')}
- **Duration:** {metadata.get('duration', 'Unknown')}
- **Published:** {metadata.get('published_at', 'Unknown')}

## 🔗 URLs Found ({len(result.get('urls', []))})
"""
    
    for url in result.get('urls', []):
        report += f"- {url}\n"
    
    report += f"\n## 🛠️ Tools & Software ({len(result.get('tools_and_software', []))})\n"
    for tool in result.get('tools_and_software', []):
        report += f"- {tool}\n"
    
    report += f"\n## 💻 Programming Languages ({len(result.get('programming_languages', []))})\n"
    for lang in result.get('programming_languages', []):
        report += f"- {lang}\n"
    
    report += f"\n## 📚 Frameworks & Libraries ({len(result.get('frameworks_and_libraries', []))})\n"
    for framework in result.get('frameworks_and_libraries', []):
        report += f"- {framework}\n"
    
    report += f"\n## ☁️ Platforms & Services ({len(result.get('platforms_and_services', []))})\n"
    for platform in result.get('platforms_and_services', []):
        report += f"- {platform}\n"
    
    report += f"\n---\n*Report generated by YT-Hoover on {result.get('analysis_timestamp', 'Unknown')}*"
    
    return report

def generate_html_report(result: Dict[str, Any]) -> str:
    """Generate HTML report"""
    markdown_content = generate_markdown_report(result)
    
    # Simple markdown to HTML conversion
    html_content = markdown_content
    html_content = html_content.replace('\n', '<br>')
    html_content = html_content.replace('##', '<h2>')
    html_content = html_content.replace('#', '<h1>')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>YT-Hoover Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1, h2 {{ color: #333; }}
        .metadata {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .url-list, .tool-list {{ background: #f9f9f9; padding: 15px; border-radius: 5px; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; color: #666; }}
    </style>
</head>
<body>
    <div class="content">
        {html_content}
    </div>
</body>
</html>"""
    
    return html

if __name__ == '__main__':
    # Get configuration
    config = load_config()
    api_key = config.get('youtube_api_key') or os.getenv('YOUTUBE_API_KEY')
    
    print("🎬 YT-Hoover WebUI Starting...")
    print("=" * 40)
    
    if not MODULES_AVAILABLE:
        print("❌ Required modules not available")
        sys.exit(1)
    
    if api_key:
        print("🔑 API Key: ✅ Configured")
        try:
            analyzer = YouTubeAnalyzer(api_key)
            print("🤖 Analyzer: ✅ Initialized")
        except Exception as e:
            print(f"❌ Analyzer initialization failed: {e}")
    else:
        print("🔑 API Key: ⚠️  Not configured (setup required)")
    
    print("🛠️  Debug mode: False")
    print("🌐 Starting server...")
    
    # Run the app
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    app.run(host=host, port=port, debug=False, threaded=True)

