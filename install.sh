#!/bin/bash
# YT-Hoover Installation Script
# GenMan Standard Setup for YouTube Video Analysis Tool

# Colors for better UX
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Project configuration
PROJECT_NAME="YT-Hoover"
PROJECT_DESCRIPTION="YouTube Video Analysis & Content Extraction Tool"
CONDA_ENV_NAME="yt-hoover"
PYTHON_VERSION="3.12"
REQUIRED_APIS="YouTube Data API v3"

# Banner
show_banner() {
    echo -e "${BLUE}"
    echo "  ╔═══════════════════════════════════════════════════════════════╗"
    echo "  ║                        YT-Hoover                              ║"
    echo "  ║              YouTube Video Analysis Tool                      ║"
    echo "  ║                   GenMan Standard Setup                       ║"
    echo "  ╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo -e "${YELLOW}YouTube Video Analysis & Content Extraction Tool${NC}"
    echo -e "${CYAN}Extract tools, links, and technical content from YouTube videos${NC}"
    echo
}

# Utility functions
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

log_step() {
    echo -e "${PURPLE}[$(date '+%H:%M:%S')] $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Check system dependencies
check_dependencies() {
    log_step "Checking system dependencies..."
    
    local missing_deps=()
    
    # Check conda/miniconda
    if ! command_exists conda; then
        missing_deps+=("conda")
    fi
    
    # Check git
    if ! command_exists git; then
        missing_deps+=("git")
    fi
    
    # Check python (fallback)
    if ! command_exists python3; then
        missing_deps+=("python3")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        echo
        echo "Please install the missing dependencies:"
        echo "• Conda: https://docs.conda.io/en/latest/miniconda.html"
        echo "• Git: https://git-scm.com/downloads"
        echo "• Python 3: https://www.python.org/downloads/"
        exit 1
    fi
    
    log_success "All required dependencies found"
}

# Setup conda environment with proper timing
setup_conda_env() {
    log_step "Setting up conda environment 'yt-hoover'..."
    
    # Check if environment already exists
    if conda env list | grep -q "^yt-hoover "; then
        log_warning "Conda environment 'yt-hoover' already exists"
        read -p "Remove and recreate? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_step "Removing existing environment..."
            conda env remove -n yt-hoover -y
        else
            log_info "Using existing environment"
            return 0
        fi
    fi
    
    # Create new environment
    log_step "Creating conda environment with Python 3.12..."
    conda create -n yt-hoover python=3.12 -y
    
    if [ $? -eq 0 ]; then
        log_success "Conda environment 'yt-hoover' created successfully"
        
        # CRITICAL: Wait for environment to be fully ready
        log_step "Waiting for environment to initialize..."
        sleep 3
        log_info "Environment initialization complete"
    else
        log_error "Failed to create conda environment"
        exit 1
    fi
}

# Install Python dependencies
install_python_deps() {
    log_step "Installing Python dependencies..."
    
    # Activate environment
    eval "$(conda shell.bash hook)"
    conda activate yt-hoover
    
    if [ $? -ne 0 ]; then
        log_error "Failed to activate conda environment"
        exit 1
    fi
    
    # Verify we're in the right environment
    current_env=$(conda info --envs | grep '*' | awk '{print $1}')
    if [ "$current_env" != "yt-hoover" ]; then
        log_error "Environment activation failed - not in correct environment"
        exit 1
    fi
    
    log_success "Activated conda environment: yt-hoover"
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        log_step "Installing from requirements.txt..."
        pip install -r requirements.txt
        
        if [ $? -eq 0 ]; then
            log_success "Python dependencies installed successfully"
        else
            log_error "Failed to install Python dependencies"
            exit 1
        fi
    else
        log_warning "No requirements.txt found"
        log_info "Installing core dependencies manually..."
        pip install flask beautifulsoup4 requests python-dotenv nltk spacy
    fi
}

# Setup API configuration
setup_api_config() {
    log_step "Setting up API configuration..."
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# YT-Hoover Configuration
YOUTUBE_API_KEY=your_youtube_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
PORT=5000
DEBUG=True
EOF
        log_success "Created .env configuration file"
    else
        log_warning ".env file already exists"
    fi
    
    log_info "YouTube Data API v3 key required for full functionality"
    log_info "Edit .env file to add your API keys:"
    echo "  • YouTube API: https://console.developers.google.com/"
    echo "  • OpenAI API (optional): https://platform.openai.com/api-keys"
}

# Test installation
test_installation() {
    log_step "Testing installation..."
    
    # Test conda environment
    eval "$(conda shell.bash hook)"
    if conda activate yt-hoover; then
        log_success "Conda environment activation test passed"
        
        # Test Python imports
        python -c "
import sys
print(f'Python {sys.version}')
try:
    import flask, requests, beautifulsoup4
    print('✅ Core dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
        
        if [ $? -eq 0 ]; then
            log_success "Python environment test passed"
        else
            log_error "Python import test failed"
            conda deactivate
            return 1
        fi
        
        conda deactivate
        return 0
    else
        log_error "Conda environment activation test failed"
        return 1
    fi
}

# Show completion message and next steps
show_completion() {
    echo
    echo -e "${GREEN}🎉 YT-Hoover installation complete!${NC}"
    echo
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Activate environment: ${CYAN}conda activate yt-hoover${NC}"
    echo "2. Configure API keys in .env file"
    echo "3. Run the application:"
    echo "   • WebUI: ${CYAN}python web/app.py${NC}"
    echo "   • CLI: ${CYAN}python src/cli.py VIDEO_URL${NC}"
    echo "   • GUI: ${CYAN}python youtube_analysis_gui.py${NC}"
    
    echo
    echo -e "${YELLOW}Quick test:${NC}"
    echo "${CYAN}conda activate yt-hoover && python src/cli.py --help${NC}"
    
    echo
    echo -e "${YELLOW}API Configuration:${NC}"
    echo "• Edit .env file with your YouTube API key"
    echo "• Get YouTube API key: https://console.developers.google.com/"
    
    echo
    echo -e "${BLUE}📚 Documentation: README.md${NC}"
    echo -e "${BLUE}🐛 Issues: Check troubleshooting section in README${NC}"
    echo -e "${BLUE}🌐 WebUI: http://localhost:5000 (after starting)${NC}"
    echo -e "${PURPLE}🚀 Built with GenMan standards${NC}"
}

# Main installation flow
main() {
    show_banner
    
    log_step "Starting YT-Hoover installation..."
    echo
    
    # Run installation steps
    check_dependencies
    setup_conda_env
    install_python_deps
    setup_api_config
    
    echo
    if test_installation; then
        log_success "Installation validation passed"
    else
        log_warning "Installation completed with warnings"
        log_info "Check the steps above and try manual installation if needed"
    fi
    
    show_completion
}

# Handle script interruption
trap 'echo -e "\n${RED}Installation interrupted${NC}"; exit 1' INT

# Run main function
main "$@"

