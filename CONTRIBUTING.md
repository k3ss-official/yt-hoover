# Contributing to YT-Hoover

We love contributions! Here's how to get started.

## 🚀 Quick Start for Contributors

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/yt-hoover.git
   cd yt-hoover
   ```
3. **Set up development environment**
   ```bash
   ./scripts/quick-start.sh
   ```
4. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

## 🛠️ Development Setup

### Prerequisites
- Python 3.11+
- YouTube Data API v3 key
- Git

### Installation
```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/

# Run specific test
python -m pytest tests/test_basic.py
```

## 📝 Code Style

We use:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

## 🧪 Testing Guidelines

- Write tests for new features
- Maintain test coverage above 80%
- Test both success and error cases
- Use meaningful test names

### Test Structure
```
tests/
├── test_basic.py          # Basic functionality tests
├── test_nlp_processor.py  # NLP processing tests
├── test_youtube_api.py    # YouTube API tests
└── test_web_ui.py         # Web UI tests
```

## 📚 Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update API documentation
- Include examples for new features

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment information**
   - Python version
   - Operating system
   - YT-Hoover version

2. **Steps to reproduce**
   - Exact commands used
   - Input data (if applicable)
   - Expected vs actual behavior

3. **Error messages**
   - Full error traceback
   - Log files (if available)

## 💡 Feature Requests

For new features:

1. **Check existing issues** first
2. **Describe the use case** clearly
3. **Provide examples** of how it would work
4. **Consider implementation** complexity

## 🔄 Pull Request Process

1. **Update documentation** as needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Follow code style guidelines**
5. **Write clear commit messages**

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(nlp): add support for new programming languages`
- `fix(api): handle rate limiting errors gracefully`
- `docs(readme): update installation instructions`

## 🏗️ Architecture

### Core Components

```
src/
├── yt_hoover.py       # Main analyzer class
├── nlp_processor.py   # NLP processing engine
├── cli.py             # Command line interface
└── gui_app.py         # Desktop GUI application

web/
├── app.py             # Flask web application
├── templates/         # HTML templates
└── static/           # CSS, JS, images
```

### Key Classes

- **YouTubeAnalyzer**: Main analysis orchestrator
- **YouTubeExtractor**: YouTube API integration
- **ContentExtractor**: Web scraping with crawl4ai
- **AdvancedNLPProcessor**: Entity extraction and NLP
- **AnalysisResult**: Result data structure

## 🌟 Areas for Contribution

### High Priority
- [ ] Speech-to-text integration for audio analysis
- [ ] Multi-language support for international content
- [ ] Real-time processing for live streams
- [ ] Advanced AI integration (GPT, Claude)
- [ ] Performance optimizations

### Medium Priority
- [ ] Additional output formats (XML, CSV)
- [ ] Database integration for result storage
- [ ] Batch processing improvements
- [ ] Mobile app development
- [ ] Browser extension

### Low Priority
- [ ] Integration with other video platforms
- [ ] Advanced visualization features
- [ ] Social media sharing
- [ ] Collaborative analysis features
- [ ] Plugin system

## 🤝 Community Guidelines

- **Be respectful** and inclusive
- **Help others** learn and contribute
- **Share knowledge** and best practices
- **Give constructive feedback**
- **Celebrate successes** together

## 📞 Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Questions and general discussion
- **Discord**: Real-time chat and support
- **Email**: maintainers@yt-hoover.com

## 🎉 Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Hall of fame page
- Annual contributor awards

## 📄 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to YT-Hoover! 🎬✨

