#!/usr/bin/env python3
"""
YT-Hoover WebUI - Flask Web Application
Beautiful web interface for YouTube video analysis
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile
import zipfile

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
    from flask_cors import CORS
    from werkzeug.utils import secure_filename
    FLASK_AVAILABLE = True
except ImportError:
    print("Flask not available. Install with: pip install flask flask-cors")
    FLASK_AVAILABLE = False
    sys.exit(1)

from src.yt_hoover import YouTubeAnalyzer, AnalysisResult

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'yt-hoover-secret-key-change-in-production'
CORS(app)

# Global analyzer instance
analyzer = None
api_key = None

# Configuration
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / 'yt-hoover-uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)

def load_api_key() -> Optional[str]:
    """Load API key from various sources"""
    # Environment variable
    env_key = os.getenv('YOUTUBE_API_KEY')
    if env_key:
        return env_key
    
    # Config file
    config_file = Path.home() / '.yt-hoover-config.json'
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('youtube_api_key')
        except:
            pass
    
    return None

def save_api_key(key: str):
    """Save API key to config file"""
    config_file = Path.home() / '.yt-hoover-config.json'
    config = {}
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except:
            pass
    
    config['youtube_api_key'] = key
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except:
        return False

def test_api_key(key: str) -> Dict[str, Any]:
    """Test if API key is valid"""
    try:
        test_analyzer = YouTubeAnalyzer(key)
        result = test_analyzer.youtube_extractor.get_video_metadata("dQw4w9WgXcQ")
        
        if 'error' in result:
            return {'valid': False, 'error': result['error']}
        else:
            return {'valid': True, 'message': 'API key is valid!'}
    except Exception as e:
        return {'valid': False, 'error': str(e)}

@app.route('/')
def index():
    """Main page"""
    global api_key
    
    # Check if API key is configured
    if not api_key:
        api_key = load_api_key()
    
    has_api_key = bool(api_key)
    
    return render_template('index.html', has_api_key=has_api_key)

@app.route('/setup')
def setup():
    """Setup page for API key configuration"""
    return render_template('setup.html')

@app.route('/api/setup', methods=['POST'])
def api_setup():
    """Handle API key setup"""
    global api_key, analyzer
    
    data = request.get_json()
    new_api_key = data.get('api_key', '').strip()
    
    if not new_api_key:
        return jsonify({'success': False, 'error': 'API key is required'})
    
    # Test the API key
    test_result = test_api_key(new_api_key)
    
    if test_result['valid']:
        # Save the API key
        if save_api_key(new_api_key):
            api_key = new_api_key
            analyzer = YouTubeAnalyzer(api_key)
            return jsonify({'success': True, 'message': 'API key saved successfully!'})
        else:
            return jsonify({'success': False, 'error': 'Could not save API key'})
    else:
        return jsonify({'success': False, 'error': test_result['error']})

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Analyze a YouTube video"""
    global analyzer
    
    if not analyzer:
        return jsonify({'success': False, 'error': 'API key not configured'})
    
    data = request.get_json()
    video_input = data.get('video_url', '').strip()
    
    if not video_input:
        return jsonify({'success': False, 'error': 'Video URL is required'})
    
    try:
        # Run analysis in async context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(analyzer.analyze(video_input))
        loop.close()
        
        # Convert result to dict for JSON response
        result_dict = result.to_dict()
        
        return jsonify({
            'success': True,
            'result': result_dict
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/batch-analyze', methods=['POST'])
def api_batch_analyze():
    """Analyze multiple videos"""
    global analyzer
    
    if not analyzer:
        return jsonify({'success': False, 'error': 'API key not configured'})
    
    data = request.get_json()
    video_urls = data.get('video_urls', [])
    
    if not video_urls:
        return jsonify({'success': False, 'error': 'No video URLs provided'})
    
    try:
        # Run batch analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(analyzer.analyze_batch(video_urls))
        loop.close()
        
        # Convert results to dict
        results_dict = [result.to_dict() for result in results]
        
        return jsonify({
            'success': True,
            'results': results_dict,
            'total': len(results),
            'successful': len([r for r in results if 'error' not in r.metadata.title])
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export', methods=['POST'])
def api_export():
    """Export analysis results"""
    global analyzer
    
    if not analyzer:
        return jsonify({'success': False, 'error': 'API key not configured'})
    
    data = request.get_json()
    result_data = data.get('result')
    export_format = data.get('format', 'markdown')
    
    if not result_data:
        return jsonify({'success': False, 'error': 'No result data provided'})
    
    try:
        # Reconstruct AnalysisResult object
        from src.yt_hoover import VideoMetadata
        
        metadata = VideoMetadata(**result_data['metadata'])
        result = AnalysisResult(
            video_id=result_data['video_id'],
            metadata=metadata,
            urls=result_data['urls'],
            tools_and_software=result_data['tools_and_software'],
            programming_languages=result_data['programming_languages'],
            frameworks_and_libraries=result_data['frameworks_and_libraries'],
            platforms_and_services=result_data['platforms_and_services'],
            companies_and_brands=result_data['companies_and_brands'],
            file_formats=result_data['file_formats'],
            apis_and_protocols=result_data['apis_and_protocols'],
            technical_concepts=result_data['technical_concepts'],
            extraction_method=result_data['extraction_method'],
            analysis_timestamp=result_data['analysis_timestamp'],
            confidence_scores=result_data['confidence_scores']
        )
        
        # Generate content
        if export_format == 'json':
            content = result.to_json()
            filename = f"yt_hoover_analysis_{result.video_id}.json"
            mimetype = 'application/json'
        elif export_format == 'html':
            content = analyzer.generate_report(result, 'html')
            filename = f"yt_hoover_analysis_{result.video_id}.html"
            mimetype = 'text/html'
        else:  # markdown
            content = analyzer.generate_report(result, 'markdown')
            filename = f"yt_hoover_analysis_{result.video_id}.md"
            mimetype = 'text/markdown'
        
        # Save to temporary file
        temp_file = UPLOAD_FOLDER / filename
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return send_file(
            temp_file,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/batch-export', methods=['POST'])
def api_batch_export():
    """Export multiple analysis results as ZIP"""
    global analyzer
    
    if not analyzer:
        return jsonify({'success': False, 'error': 'API key not configured'})
    
    data = request.get_json()
    results_data = data.get('results', [])
    export_format = data.get('format', 'markdown')
    
    if not results_data:
        return jsonify({'success': False, 'error': 'No results data provided'})
    
    try:
        # Create temporary ZIP file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"yt_hoover_batch_export_{timestamp}.zip"
        zip_path = UPLOAD_FOLDER / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for i, result_data in enumerate(results_data):
                try:
                    # Reconstruct AnalysisResult object
                    from src.yt_hoover import VideoMetadata
                    
                    metadata = VideoMetadata(**result_data['metadata'])
                    result = AnalysisResult(
                        video_id=result_data['video_id'],
                        metadata=metadata,
                        urls=result_data['urls'],
                        tools_and_software=result_data['tools_and_software'],
                        programming_languages=result_data['programming_languages'],
                        frameworks_and_libraries=result_data['frameworks_and_libraries'],
                        platforms_and_services=result_data['platforms_and_services'],
                        companies_and_brands=result_data['companies_and_brands'],
                        file_formats=result_data['file_formats'],
                        apis_and_protocols=result_data['apis_and_protocols'],
                        technical_concepts=result_data['technical_concepts'],
                        extraction_method=result_data['extraction_method'],
                        analysis_timestamp=result_data['analysis_timestamp'],
                        confidence_scores=result_data['confidence_scores']
                    )
                    
                    # Generate content
                    if export_format == 'json':
                        content = result.to_json()
                        filename = f"analysis_{result.video_id}.json"
                    elif export_format == 'html':
                        content = analyzer.generate_report(result, 'html')
                        filename = f"analysis_{result.video_id}.html"
                    else:  # markdown
                        content = analyzer.generate_report(result, 'markdown')
                        filename = f"analysis_{result.video_id}.md"
                    
                    # Add to ZIP
                    zipf.writestr(filename, content)
                    
                except Exception as e:
                    # Add error file for failed exports
                    error_content = f"Error exporting result {i+1}: {str(e)}"
                    zipf.writestr(f"error_{i+1}.txt", error_content)
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=zip_filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/status')
def api_status():
    """Get application status"""
    global api_key, analyzer
    
    return jsonify({
        'api_key_configured': bool(api_key),
        'analyzer_ready': bool(analyzer),
        'version': '1.0.0'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

def create_templates():
    """Create HTML templates"""
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    static_dir = Path(__file__).parent / 'static'
    static_dir.mkdir(exist_ok=True)
    
    # Create main template
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YT-Hoover - YouTube Video Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .main-container { background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; border-radius: 15px 15px 0 0; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .btn-primary:hover { background: linear-gradient(135deg, #764ba2 0%, #667eea 100%); }
        .result-card { border-left: 4px solid #667eea; }
        .loading { display: none; }
        .url-list { max-height: 200px; overflow-y: auto; }
        .tool-badge { margin: 2px; }
    </style>
</head>
<body>
    <div class="container mt-4">
        <div class="main-container p-0">
            <!-- Header -->
            <div class="header p-4 text-center">
                <h1><i class="fas fa-video"></i> YT-Hoover</h1>
                <p class="mb-0">Extract structured information from YouTube videos</p>
            </div>
            
            <!-- Setup Warning -->
            {% if not has_api_key %}
            <div class="alert alert-warning m-4">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Setup Required:</strong> 
                <a href="/setup" class="alert-link">Configure your YouTube API key</a> to start analyzing videos.
            </div>
            {% endif %}
            
            <!-- Main Content -->
            <div class="p-4">
                <!-- Single Video Analysis -->
                <div class="row">
                    <div class="col-md-6">
                        <div class="card h-100">
                            <div class="card-header">
                                <h5><i class="fas fa-search"></i> Single Video Analysis</h5>
                            </div>
                            <div class="card-body">
                                <form id="singleAnalysisForm">
                                    <div class="mb-3">
                                        <label for="videoUrl" class="form-label">YouTube URL or Video ID</label>
                                        <input type="text" class="form-control" id="videoUrl" 
                                               placeholder="https://www.youtube.com/watch?v=..." required>
                                    </div>
                                    <button type="submit" class="btn btn-primary w-100" {% if not has_api_key %}disabled{% endif %}>
                                        <i class="fas fa-play"></i> Analyze Video
                                    </button>
                                </form>
                                
                                <div id="singleLoading" class="loading text-center mt-3">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                    <p class="mt-2">Analyzing video...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="card h-100">
                            <div class="card-header">
                                <h5><i class="fas fa-list"></i> Batch Analysis</h5>
                            </div>
                            <div class="card-body">
                                <form id="batchAnalysisForm">
                                    <div class="mb-3">
                                        <label for="batchUrls" class="form-label">Video URLs (one per line)</label>
                                        <textarea class="form-control" id="batchUrls" rows="4" 
                                                  placeholder="https://www.youtube.com/watch?v=...&#10;https://www.youtube.com/watch?v=..."></textarea>
                                    </div>
                                    <button type="submit" class="btn btn-primary w-100" {% if not has_api_key %}disabled{% endif %}>
                                        <i class="fas fa-tasks"></i> Analyze Batch
                                    </button>
                                </form>
                                
                                <div id="batchLoading" class="loading text-center mt-3">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                    <p class="mt-2">Processing videos...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Results Section -->
                <div id="resultsSection" class="mt-4" style="display: none;">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5><i class="fas fa-chart-bar"></i> Analysis Results</h5>
                            <div class="btn-group">
                                <button class="btn btn-outline-primary btn-sm" onclick="exportResults('markdown')">
                                    <i class="fas fa-download"></i> Markdown
                                </button>
                                <button class="btn btn-outline-primary btn-sm" onclick="exportResults('json')">
                                    <i class="fas fa-download"></i> JSON
                                </button>
                                <button class="btn btn-outline-primary btn-sm" onclick="exportResults('html')">
                                    <i class="fas fa-download"></i> HTML
                                </button>
                            </div>
                        </div>
                        <div class="card-body">
                            <div id="resultsContent"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentResults = null;
        
        // Single video analysis
        document.getElementById('singleAnalysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const videoUrl = document.getElementById('videoUrl').value.trim();
            if (!videoUrl) return;
            
            const loading = document.getElementById('singleLoading');
            const resultsSection = document.getElementById('resultsSection');
            
            loading.style.display = 'block';
            resultsSection.style.display = 'none';
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ video_url: videoUrl })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentResults = [data.result];
                    displayResults(currentResults);
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                loading.style.display = 'none';
            }
        });
        
        // Batch analysis
        document.getElementById('batchAnalysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const batchUrls = document.getElementById('batchUrls').value.trim();
            if (!batchUrls) return;
            
            const urls = batchUrls.split('\\n').map(url => url.trim()).filter(url => url);
            if (urls.length === 0) return;
            
            const loading = document.getElementById('batchLoading');
            const resultsSection = document.getElementById('resultsSection');
            
            loading.style.display = 'block';
            resultsSection.style.display = 'none';
            
            try {
                const response = await fetch('/api/batch-analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ video_urls: urls })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentResults = data.results;
                    displayResults(currentResults);
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                loading.style.display = 'none';
            }
        });
        
        function displayResults(results) {
            const resultsContent = document.getElementById('resultsContent');
            const resultsSection = document.getElementById('resultsSection');
            
            let html = '';
            
            if (results.length === 1) {
                // Single result
                const result = results[0];
                html = generateSingleResultHTML(result);
            } else {
                // Multiple results
                html = generateBatchResultsHTML(results);
            }
            
            resultsContent.innerHTML = html;
            resultsSection.style.display = 'block';
        }
        
        function generateSingleResultHTML(result) {
            const metadata = result.metadata;
            
            return `
                <div class="row">
                    <div class="col-md-6">
                        <div class="result-card p-3 mb-3">
                            <h6><i class="fas fa-video"></i> Video Information</h6>
                            <p><strong>Title:</strong> ${metadata.title}</p>
                            <p><strong>Channel:</strong> ${metadata.channel_title}</p>
                            <p><strong>Views:</strong> ${parseInt(metadata.view_count).toLocaleString()}</p>
                            <p><strong>Duration:</strong> ${metadata.duration}</p>
                        </div>
                        
                        <div class="result-card p-3 mb-3">
                            <h6><i class="fas fa-chart-pie"></i> Analysis Summary</h6>
                            <p><strong>URLs Found:</strong> ${result.urls.length}</p>
                            <p><strong>Tools & Software:</strong> ${result.tools_and_software.length}</p>
                            <p><strong>Programming Languages:</strong> ${result.programming_languages.length}</p>
                            <p><strong>Frameworks:</strong> ${result.frameworks_and_libraries.length}</p>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        ${result.urls.length > 0 ? `
                        <div class="result-card p-3 mb-3">
                            <h6><i class="fas fa-link"></i> URLs Found (${result.urls.length})</h6>
                            <div class="url-list">
                                ${result.urls.map(url => `<p><a href="${url}" target="_blank">${url}</a></p>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                        
                        ${result.tools_and_software.length > 0 ? `
                        <div class="result-card p-3 mb-3">
                            <h6><i class="fas fa-tools"></i> Tools & Software</h6>
                            <div>
                                ${result.tools_and_software.map(tool => {
                                    const name = typeof tool === 'object' ? tool.text : tool;
                                    return `<span class="badge bg-primary tool-badge">${name}</span>`;
                                }).join('')}
                            </div>
                        </div>
                        ` : ''}
                        
                        ${result.programming_languages.length > 0 ? `
                        <div class="result-card p-3 mb-3">
                            <h6><i class="fas fa-code"></i> Programming Languages</h6>
                            <div>
                                ${result.programming_languages.map(lang => `<span class="badge bg-success tool-badge">${lang}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }
        
        function generateBatchResultsHTML(results) {
            const successful = results.filter(r => !r.metadata.title.startsWith('Error:')).length;
            
            let html = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i>
                    Processed ${results.length} videos. ${successful} successful, ${results.length - successful} failed.
                </div>
                
                <div class="row">
            `;
            
            results.forEach((result, index) => {
                const metadata = result.metadata;
                const isError = metadata.title.startsWith('Error:');
                
                html += `
                    <div class="col-md-6 mb-3">
                        <div class="card ${isError ? 'border-danger' : ''}">
                            <div class="card-body">
                                <h6 class="card-title">${isError ? 'Error' : metadata.title}</h6>
                                ${!isError ? `
                                    <p class="card-text">
                                        <small class="text-muted">Channel: ${metadata.channel_title}</small><br>
                                        <small class="text-muted">Views: ${parseInt(metadata.view_count).toLocaleString()}</small>
                                    </p>
                                    <div class="d-flex justify-content-between">
                                        <small>URLs: ${result.urls.length}</small>
                                        <small>Tools: ${result.tools_and_software.length}</small>
                                        <small>Languages: ${result.programming_languages.length}</small>
                                    </div>
                                ` : `
                                    <p class="text-danger">${metadata.title}</p>
                                `}
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            return html;
        }
        
        async function exportResults(format) {
            if (!currentResults) return;
            
            try {
                if (currentResults.length === 1) {
                    // Single export
                    const response = await fetch('/api/export', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            result: currentResults[0], 
                            format: format 
                        })
                    });
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = response.headers.get('Content-Disposition').split('filename=')[1];
                        a.click();
                        window.URL.revokeObjectURL(url);
                    }
                } else {
                    // Batch export
                    const response = await fetch('/api/batch-export', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            results: currentResults, 
                            format: format 
                        })
                    });
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `yt_hoover_batch_export.zip`;
                        a.click();
                        window.URL.revokeObjectURL(url);
                    }
                }
            } catch (error) {
                alert('Export failed: ' + error.message);
            }
        }
    </script>
</body>
</html>"""
    
    with open(templates_dir / 'index.html', 'w') as f:
        f.write(index_html)
    
    # Create setup template
    setup_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Setup - YT-Hoover</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .setup-container { background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); max-width: 600px; margin: 50px auto; }
        .header { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; border-radius: 15px 15px 0 0; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .step { border-left: 4px solid #667eea; padding-left: 15px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="setup-container">
            <div class="header p-4 text-center">
                <h1><i class="fas fa-cog"></i> Setup YT-Hoover</h1>
                <p class="mb-0">Configure your YouTube API key</p>
            </div>
            
            <div class="p-4">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i>
                    <strong>Why do I need an API key?</strong> YT-Hoover uses the YouTube Data API to access video information. This requires a free API key from Google.
                </div>
                
                <h5>How to get your YouTube API key:</h5>
                
                <div class="step">
                    <strong>Step 1:</strong> Go to <a href="https://console.developers.google.com/" target="_blank">Google Cloud Console</a>
                </div>
                
                <div class="step">
                    <strong>Step 2:</strong> Create a new project or select an existing one
                </div>
                
                <div class="step">
                    <strong>Step 3:</strong> Enable the "YouTube Data API v3"
                </div>
                
                <div class="step">
                    <strong>Step 4:</strong> Create credentials (API Key)
                </div>
                
                <div class="step">
                    <strong>Step 5:</strong> Copy your API key and paste it below
                </div>
                
                <hr>
                
                <form id="setupForm">
                    <div class="mb-3">
                        <label for="apiKey" class="form-label">YouTube API Key</label>
                        <input type="text" class="form-control" id="apiKey" placeholder="AIzaSy..." required>
                        <div class="form-text">Your API key will be saved securely on your device.</div>
                    </div>
                    
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="fas fa-check"></i> Test & Save API Key
                    </button>
                </form>
                
                <div id="setupLoading" class="text-center mt-3" style="display: none;">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Testing...</span>
                    </div>
                    <p class="mt-2">Testing API key...</p>
                </div>
                
                <div id="setupResult" class="mt-3"></div>
                
                <div class="text-center mt-4">
                    <a href="/" class="btn btn-outline-secondary">
                        <i class="fas fa-arrow-left"></i> Back to Main
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('setupForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const apiKey = document.getElementById('apiKey').value.trim();
            if (!apiKey) return;
            
            const loading = document.getElementById('setupLoading');
            const result = document.getElementById('setupResult');
            
            loading.style.display = 'block';
            result.innerHTML = '';
            
            try {
                const response = await fetch('/api/setup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_key: apiKey })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    result.innerHTML = `
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle"></i>
                            ${data.message} <a href="/">Click here to start analyzing videos!</a>
                        </div>
                    `;
                } else {
                    result.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-circle"></i>
                            Error: ${data.error}
                        </div>
                    `;
                }
            } catch (error) {
                result.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle"></i>
                        Error: ${error.message}
                    </div>
                `;
            } finally {
                loading.style.display = 'none';
            }
        });
    </script>
</body>
</html>"""
    
    with open(templates_dir / 'setup.html', 'w') as f:
        f.write(setup_html)
    
    # Create error template
    error_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - YT-Hoover</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .error-container { background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); max-width: 500px; margin: 100px auto; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-container p-5">
            <i class="fas fa-exclamation-triangle text-warning" style="font-size: 4rem;"></i>
            <h1 class="mt-3">Error {{ error_code }}</h1>
            <p class="text-muted">{{ error_message }}</p>
            <a href="/" class="btn btn-primary">
                <i class="fas fa-home"></i> Go Home
            </a>
        </div>
    </div>
</body>
</html>"""
    
    with open(templates_dir / 'error.html', 'w') as f:
        f.write(error_html)

def main():
    """Main function to run the web application"""
    global api_key, analyzer
    
    # Create templates if they don't exist
    create_templates()
    
    # Load API key on startup
    api_key = load_api_key()
    if api_key:
        try:
            analyzer = YouTubeAnalyzer(api_key)
            print("✅ YouTube analyzer initialized with saved API key")
        except Exception as e:
            print(f"⚠️  Could not initialize analyzer: {e}")
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting YT-Hoover WebUI...")
    print(f"📍 URL: http://localhost:{port}")
    print(f"🔑 API Key: {'✅ Configured' if api_key else '❌ Not configured'}")
    print(f"🛠️  Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()

