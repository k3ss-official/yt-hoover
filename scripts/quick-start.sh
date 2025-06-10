#!/bin/bash
"""
YT-Hoover Quick Start Script
Automated installation and setup for YT-Hoover
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.11+ is available
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [[ $(echo "$PYTHON_VERSION >= 3.11" | bc -l) -eq 0 ]]; then
            print_warning "Python 3.11+ recommended, but found $PYTHON_VERSION"
        fi
    else
        print_error "Python 3 not found. Please install Python 3.11+"
        exit 1
    fi
    
    print_success "Using Python: $PYTHON_CMD"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Upgrade pip first
    $PYTHON_CMD -m pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        $PYTHON_CMD -m pip install -r requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup credentials
setup_credentials() {
    print_status "Setting up credentials..."
    
    echo ""
    echo "🔑 YouTube API Key Setup"
    echo "========================"
    echo ""
    echo "To use YT-Hoover, you need a YouTube Data API v3 key."
    echo "Here's how to get one:"
    echo ""
    echo "1. Go to: https://console.developers.google.com/"
    echo "2. Create a new project or select existing"
    echo "3. Enable 'YouTube Data API v3'"
    echo "4. Create credentials (API Key)"
    echo "5. Copy the API key"
    echo ""
    
    read -p "Do you have a YouTube API key? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your YouTube API key: " API_KEY
        
        if [ ! -z "$API_KEY" ]; then
            # Test the API key
            print_status "Testing API key..."
            
            if $PYTHON_CMD scripts/test_api_key.py "$API_KEY"; then
                print_success "API key is valid and saved!"
            else
                print_error "API key test failed"
                exit 1
            fi
        else
            print_warning "No API key provided. You can set it up later using the WebUI."
        fi
    else
        print_warning "You can set up your API key later using the WebUI or CLI."
    fi
}

# Create desktop shortcut (Linux/macOS)
create_shortcuts() {
    print_status "Creating shortcuts..."
    
    # Make scripts executable
    chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true
    chmod +x src/*.py 2>/dev/null || true
    chmod +x web/app.py 2>/dev/null || true
    
    # Create launcher script
    cat > yt-hoover << 'EOF'
#!/bin/bash
# YT-Hoover Launcher
cd "$(dirname "$0")"

case "$1" in
    "gui"|"")
        echo "🖥️  Launching YT-Hoover GUI..."
        python3 src/gui_app.py
        ;;
    "web"|"webui")
        echo "🌐 Starting YT-Hoover WebUI..."
        echo "Open http://localhost:5000 in your browser"
        python3 web/app.py
        ;;
    "cli")
        shift
        python3 src/cli.py "$@"
        ;;
    "setup")
        python3 scripts/setup_credentials.py
        ;;
    *)
        echo "YT-Hoover - YouTube Video Analysis Tool"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  gui, (default)  Launch desktop GUI"
        echo "  web, webui      Start web interface"
        echo "  cli [args]      Use command line interface"
        echo "  setup           Setup API credentials"
        echo ""
        echo "Examples:"
        echo "  $0                                    # Launch GUI"
        echo "  $0 web                               # Start WebUI"
        echo "  $0 cli VIDEO_ID                      # Analyze video"
        echo "  $0 cli --help                        # CLI help"
        ;;
esac
EOF
    
    chmod +x yt-hoover
    print_success "Launcher script created: ./yt-hoover"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    # Test imports
    if $PYTHON_CMD -c "from src.yt_hoover import YouTubeAnalyzer; print('✅ Core modules OK')"; then
        print_success "Core modules imported successfully"
    else
        print_error "Core module import failed"
        exit 1
    fi
    
    # Test CLI
    if $PYTHON_CMD src/cli.py --version > /dev/null 2>&1; then
        print_success "CLI is working"
    else
        print_warning "CLI test failed (may need API key)"
    fi
    
    # Test WebUI imports
    if $PYTHON_CMD -c "import sys; sys.path.append('web'); from app import app; print('✅ WebUI OK')"; then
        print_success "WebUI is ready"
    else
        print_warning "WebUI test failed"
    fi
}

# Main installation process
main() {
    echo ""
    echo "🎬 YT-Hoover Quick Start"
    echo "========================"
    echo ""
    echo "This script will install and set up YT-Hoover for you."
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "README.md" ] || [ ! -d "src" ]; then
        print_error "Please run this script from the YT-Hoover root directory"
        exit 1
    fi
    
    # Run installation steps
    check_python
    install_dependencies
    create_shortcuts
    test_installation
    setup_credentials
    
    echo ""
    print_success "🎉 YT-Hoover installation completed!"
    echo ""
    echo "Quick Start Options:"
    echo "  ./yt-hoover          # Launch desktop GUI"
    echo "  ./yt-hoover web      # Start web interface (http://localhost:5000)"
    echo "  ./yt-hoover cli --help  # Command line help"
    echo ""
    echo "Need help? Check out:"
    echo "  📖 README.md - Complete documentation"
    echo "  🌐 Web interface - User-friendly analysis"
    echo "  💻 CLI - Powerful automation features"
    echo ""
}

# Run main function
main "$@"

