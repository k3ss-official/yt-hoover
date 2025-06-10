# 🎬 YT-Hoover

> **Hoover up all the good stuff from YouTube videos!** 🧹✨

YT-Hoover is a powerful, user-friendly tool that extracts structured information from YouTube videos including tools, technologies, links, and resources mentioned by content creators. Perfect for researchers, developers, and anyone who wants to quickly extract valuable information from video content.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/your-username/yt-hoover)

## 🚀 Quick Start

### One-Line Install & Run
```bash
git clone https://github.com/your-username/yt-hoover.git
cd yt-hoover
./scripts/quick-start.sh
```

### Or try the WebUI instantly:
```bash
python -m pip install -r requirements.txt
python web/app.py
```
Then open http://localhost:5000 in your browser! 🌐

## ✨ What YT-Hoover Does

YT-Hoover analyzes YouTube videos and extracts:

- 🔗 **URLs & Links** - All web resources mentioned
- 🛠️ **Tools & Software** - Development tools, applications, services
- 💻 **Programming Languages** - Python, JavaScript, Rust, etc.
- 📚 **Frameworks & Libraries** - React, Django, TensorFlow, etc.
- ☁️ **Platforms & Services** - AWS, GitHub, Docker, etc.
- 🏢 **Companies & Brands** - Google, Microsoft, OpenAI, etc.
- 📄 **File Formats** - JSON, CSV, PDF, etc.
- 🌐 **APIs & Protocols** - REST, GraphQL, OAuth, etc.

## 🎯 Perfect For

- **📚 Educational Content Analysis** - Extract tools from programming tutorials
- **🔍 Research & Competitive Intelligence** - Monitor technology trends
- **📊 Tech Review Monitoring** - Track mentioned software and tools
- **🎤 Conference Talk Analysis** - Compile resources from presentations
- **📝 Content Creation** - Research tools used by successful creators

## 🖥️ Multiple Interfaces

### 🌐 WebUI (Recommended for beginners)
Beautiful web interface with drag-and-drop functionality:
```bash
python web/app.py
```

### 🖼️ Desktop GUI
Native desktop application with video preview:
```bash
python src/gui_app.py
```

### 💻 Command Line
Powerful CLI for automation and scripting:
```bash
python src/cli.py https://www.youtube.com/watch?v=VIDEO_ID
```

### 🤖 Python API
Integrate into your own projects:
```python
from src.yt_hoover import YouTubeAnalyzer
analyzer = YouTubeAnalyzer(api_key="your_key")
result = await analyzer.analyze("VIDEO_ID")
```

## 📦 Installation

### Prerequisites
- Python 3.11+ 🐍
- YouTube Data API v3 key 🔑
- Internet connection 🌐

### Method 1: Quick Install (Recommended)
```bash
git clone https://github.com/your-username/yt-hoover.git
cd yt-hoover
chmod +x scripts/install.sh
./scripts/install.sh
```

### Method 2: Manual Install
```bash
git clone https://github.com/your-username/yt-hoover.git
cd yt-hoover
python -m pip install -r requirements.txt
python scripts/setup_credentials.py
```

### Method 3: Docker (Coming Soon)
```bash
docker run -p 5000:5000 yt-hoover/webui
```

## 🔑 Getting Your YouTube API Key

1. 🌐 Go to [Google Cloud Console](https://console.developers.google.com/)
2. 📁 Create a new project or select existing
3. 🔧 Enable **YouTube Data API v3**
4. 🔑 Create credentials (API Key)
5. 📋 Copy the API key
6. 🎯 Run our setup: `python scripts/setup_credentials.py`

**Don't worry!** Our setup script will guide you through this step-by-step with helpful links and screenshots! 😊

## 🎮 Usage Examples

### WebUI
1. Open http://localhost:5000
2. Paste YouTube URL
3. Click "Analyze"
4. Download results in your preferred format!

### CLI Examples
```bash
# Basic analysis
python src/cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Save to file
python src/cli.py "VIDEO_ID" --output results.json --format json

# Batch processing
python src/cli.py --batch video_list.txt --output-dir ./results/

# Custom API key
python src/cli.py "VIDEO_ID" --api-key "YOUR_API_KEY"
```

### Python API
```python
import asyncio
from src.yt_hoover import YouTubeAnalyzer

async def analyze_video():
    analyzer = YouTubeAnalyzer(api_key="your_key")
    
    # Analyze single video
    result = await analyzer.analyze("dQw4w9WgXcQ")
    
    # Get extracted information
    urls = result.get_urls()
    tools = result.get_tools()
    languages = result.get_programming_languages()
    
    print(f"Found {len(urls)} URLs and {len(tools)} tools!")

asyncio.run(analyze_video())
```

## 📊 Output Formats

YT-Hoover supports multiple output formats:

- **📝 Markdown** - Human-readable reports
- **📄 JSON** - Machine-readable data
- **📊 CSV** - Spreadsheet-compatible
- **📑 PDF** - Professional documents
- **📘 Word** - Microsoft Word format
- **🌐 HTML** - Web-friendly reports

## 🏗️ Project Structure

```
yt-hoover/
├── 📁 src/                 # Core source code
│   ├── 🐍 yt_hoover.py     # Main analysis engine
│   ├── 🖼️ gui_app.py       # Desktop GUI application
│   ├── 💻 cli.py           # Command-line interface
│   └── 🧠 nlp_processor.py # NLP processing engine
├── 🌐 web/                 # Web interface
│   ├── 🎨 app.py           # Flask web application
│   ├── 📁 templates/       # HTML templates
│   └── 📁 static/          # CSS, JS, images
├── 📚 docs/                # Documentation
├── 🧪 tests/               # Test suite
├── 🔧 scripts/             # Setup and utility scripts
├── 📋 requirements.txt     # Python dependencies
└── 📖 README.md           # This file!
```

## 🧪 Testing

Run the test suite to make sure everything works:

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_analyzer.py

# Run with coverage
python -m pytest --cov=src tests/
```

## 🤝 Contributing

We love contributions! Here's how to get started:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch: `git checkout -b feature/amazing-feature`
3. 💻 Make your changes
4. 🧪 Add tests for new functionality
5. ✅ Run tests: `python -m pytest`
6. 📝 Commit changes: `git commit -m "Add amazing feature"`
7. 📤 Push to branch: `git push origin feature/amazing-feature`
8. 🔄 Open a Pull Request

### Development Setup
```bash
git clone https://github.com/your-username/yt-hoover.git
cd yt-hoover
python -m pip install -r requirements-dev.txt
pre-commit install
```

## 📈 Performance & Limitations

### ✅ What Works Great
- **Video Metadata**: Excellent extraction using YouTube Data API
- **Description Analysis**: High-quality NLP processing
- **URL Detection**: Comprehensive link extraction
- **Tool Recognition**: Advanced pattern matching
- **Batch Processing**: Efficient handling of multiple videos

### ⚠️ Current Limitations
- **Transcript Access**: YouTube captions require OAuth2 authentication
- **Audio Processing**: No direct speech-to-text (yet!)
- **Language Support**: Optimized for English content
- **Rate Limits**: YouTube API has daily quotas

### 🔮 Coming Soon
- 🎤 **Speech-to-text integration** for direct audio analysis
- 🌍 **Multi-language support** for international content
- 📺 **Live stream analysis** capabilities
- 🤖 **Advanced AI integration** with LLMs
- 📊 **Analytics dashboard** for trend analysis

## 🆘 Troubleshooting

### Common Issues

#### "No API key found"
```bash
python scripts/setup_credentials.py
```

#### "API quota exceeded"
- Check your [Google Cloud Console](https://console.cloud.google.com/)
- Monitor daily usage limits
- Consider upgrading your quota

#### "Video not found"
- Ensure video is public and not deleted
- Try with video ID instead of full URL
- Check for typos in the URL

#### WebUI won't start
```bash
pip install --upgrade flask
python web/app.py --debug
```

### Getting Help
1. 📖 Check our [Documentation](docs/)
2. 🔍 Search [Issues](https://github.com/your-username/yt-hoover/issues)
3. 💬 Join our [Discussions](https://github.com/your-username/yt-hoover/discussions)
4. 🐛 Report bugs with detailed information

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- 🎥 **YouTube Data API** for providing video metadata
- 🤖 **Google AI** for NLP capabilities
- 🌐 **Flask** for the beautiful web interface
- 🐍 **Python community** for amazing libraries
- 👥 **Contributors** who make this project better

## 🌟 Star History

If you find YT-Hoover useful, please consider giving it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=your-username/yt-hoover&type=Date)](https://star-history.com/#your-username/yt-hoover&Date)

## 📞 Support

- 📧 **Email**: support@yt-hoover.com
- 💬 **Discord**: [Join our community](https://discord.gg/yt-hoover)
- 🐦 **Twitter**: [@yt_hoover](https://twitter.com/yt_hoover)
- 📖 **Documentation**: [docs.yt-hoover.com](https://docs.yt-hoover.com)

---

<div align="center">

**Made with ❤️ by the YT-Hoover team**

[🌟 Star us on GitHub](https://github.com/your-username/yt-hoover) • [🐛 Report Bug](https://github.com/your-username/yt-hoover/issues) • [💡 Request Feature](https://github.com/your-username/yt-hoover/issues)

</div>

