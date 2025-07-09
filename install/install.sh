#!/bin/bash
# UPID CLI Installation Script for Unix/Linux/macOS
# Installs UPID CLI like kubectl

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Version and release info
VERSION="1.0.0"
RELEASE_URL="https://github.com/kubilitics/upid-cli/releases/latest/download"
GITHUB_API="https://api.github.com/repos/kubilitics/upid-cli/releases/latest"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    UPID CLI Installation${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to detect OS and architecture
detect_system() {
    print_status "Detecting system information..."
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="darwin"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    # Detect architecture
    ARCH=$(uname -m)
    case $ARCH in
        x86_64) ARCH="x86_64" ;;
        amd64) ARCH="x86_64" ;;
        arm64) ARCH="arm64" ;;
        aarch64) ARCH="arm64" ;;
        *) 
            print_error "Unsupported architecture: $ARCH"
            exit 1
            ;;
    esac
    
    print_success "Detected: $OS $ARCH"
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check for curl
    if ! command -v curl &> /dev/null; then
        print_error "curl is required but not installed"
        exit 1
    fi
    
    # Check for tar
    if ! command -v tar &> /dev/null; then
        print_error "tar is required but not installed"
        exit 1
    fi
    
    # Check for gzip
    if ! command -v gzip &> /dev/null; then
        print_error "gzip is required but not installed"
        exit 1
    fi
    
    print_success "All dependencies are available"
}

# Function to get latest version
get_latest_version() {
    print_status "Getting latest version information..."
    
    if command -v jq &> /dev/null; then
        LATEST_VERSION=$(curl -s "$GITHUB_API" | jq -r '.tag_name' | sed 's/v//')
    else
        # Fallback without jq
        LATEST_VERSION=$(curl -s "$GITHUB_API" | grep -o '"tag_name":"[^"]*"' | cut -d'"' -f4 | sed 's/v//')
    fi
    
    if [[ -z "$LATEST_VERSION" ]]; then
        print_warning "Could not determine latest version, using default: $VERSION"
        LATEST_VERSION="$VERSION"
    fi
    
    print_success "Latest version: $LATEST_VERSION"
}

# Function to download binary
download_binary() {
    local version=$1
    local os=$2
    local arch=$3
    
    print_status "Downloading UPID CLI binary..."
    
    # Construct download URL
    BINARY_NAME="upid-$os-$arch"
    DOWNLOAD_URL="$RELEASE_URL/$BINARY_NAME"
    
    print_status "Download URL: $DOWNLOAD_URL"
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    BINARY_PATH="$TEMP_DIR/upid"
    
    # Download binary
    if curl -L -o "$BINARY_PATH" "$DOWNLOAD_URL"; then
        print_success "Binary downloaded successfully"
    else
        print_error "Failed to download binary"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    
    # Make executable
    chmod +x "$BINARY_PATH"
    
    # Verify binary
    if [[ -x "$BINARY_PATH" ]]; then
        print_success "Binary is executable"
    else
        print_error "Binary is not executable"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    
    echo "$BINARY_PATH"
}

# Function to install binary
install_binary() {
    local binary_path=$1
    local install_dir=$2
    
    print_status "Installing UPID CLI..."
    
    # Create installation directory if it doesn't exist
    sudo mkdir -p "$install_dir"
    
    # Install binary
    if sudo cp "$binary_path" "$install_dir/upid"; then
        print_success "Binary installed to $install_dir/upid"
    else
        print_error "Failed to install binary"
        rm -rf "$(dirname "$binary_path")"
        exit 1
    fi
    
    # Set permissions
    sudo chmod 755 "$install_dir/upid"
    
    # Create symlink if needed
    if [[ "$install_dir" != "/usr/local/bin" ]]; then
        if [[ -w "/usr/local/bin" ]] || sudo test -w "/usr/local/bin"; then
            sudo ln -sf "$install_dir/upid" "/usr/local/bin/upid"
            print_success "Created symlink in /usr/local/bin"
        fi
    fi
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check if upid is in PATH
    if command -v upid &> /dev/null; then
        print_success "UPID CLI is available in PATH"
    else
        print_warning "UPID CLI is not in PATH, you may need to add it manually"
    fi
    
    # Test version command
    if upid --version &> /dev/null; then
        VERSION_OUTPUT=$(upid --version)
        print_success "UPID CLI version: $VERSION_OUTPUT"
    else
        print_error "Failed to get UPID CLI version"
        exit 1
    fi
    
    # Test help command
    if upid --help &> /dev/null; then
        print_success "UPID CLI help command works"
    else
        print_error "UPID CLI help command failed"
        exit 1
    fi
}

# Function to create configuration directory
setup_config() {
    print_status "Setting up configuration directory..."
    
    CONFIG_DIR="$HOME/.upid"
    
    if [[ ! -d "$CONFIG_DIR" ]]; then
        mkdir -p "$CONFIG_DIR"
        print_success "Created configuration directory: $CONFIG_DIR"
    else
        print_status "Configuration directory already exists: $CONFIG_DIR"
    fi
    
    # Create default config file if it doesn't exist
    CONFIG_FILE="$CONFIG_DIR/config.yaml"
    if [[ ! -f "$CONFIG_FILE" ]]; then
        cat > "$CONFIG_FILE" << EOF
# UPID CLI Configuration
version: 1.0.0

# Default settings
defaults:
  output_format: table
  local_mode: false
  dry_run: true

# Authentication settings
auth:
  auto_detect: true
  timeout: 30

# Logging settings
logging:
  level: info
  file: ~/.upid/logs/upid.log

# Performance settings
performance:
  max_workers: 4
  timeout: 60
EOF
        print_success "Created default configuration file: $CONFIG_FILE"
    fi
    
    # Create logs directory
    LOGS_DIR="$CONFIG_DIR/logs"
    if [[ ! -d "$LOGS_DIR" ]]; then
        mkdir -p "$LOGS_DIR"
        print_success "Created logs directory: $LOGS_DIR"
    fi
}

# Function to display post-installation information
show_post_install_info() {
    print_success "UPID CLI installation completed!"
    echo
    echo -e "${CYAN}Next steps:${NC}"
    echo "1. Run 'upid --help' to see available commands"
    echo "2. Run 'upid auth login' to authenticate with your cluster"
    echo "3. Run 'upid analyze resources' to analyze your cluster"
    echo "4. Run 'upid optimize resources' to get optimization recommendations"
    echo
    echo -e "${CYAN}Documentation:${NC}"
    echo "  - GitHub: https://github.com/kubilitics/upid-cli"
    echo "  - Documentation: https://github.com/kubilitics/upid-cli#readme"
    echo
    echo -e "${CYAN}Configuration:${NC}"
    echo "  - Config file: $HOME/.upid/config.yaml"
    echo "  - Logs: $HOME/.upid/logs/"
    echo
    echo -e "${YELLOW}Note:${NC} Make sure you have kubectl configured and access to your Kubernetes cluster"
}

# Function to cleanup
cleanup() {
    local temp_dir=$1
    
    if [[ -n "$temp_dir" && -d "$temp_dir" ]]; then
        rm -rf "$temp_dir"
        print_status "Cleaned up temporary files"
    fi
}

# Function to handle errors
error_handler() {
    local exit_code=$?
    print_error "Installation failed with exit code $exit_code"
    cleanup "$TEMP_DIR"
    exit $exit_code
}

# Set error handler
trap error_handler ERR

# Main installation function
main() {
    print_header
    
    # Parse command line arguments
    INSTALL_DIR="/usr/local/bin"
    SKIP_VERIFY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install-dir)
                INSTALL_DIR="$2"
                shift 2
                ;;
            --skip-verify)
                SKIP_VERIFY=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo
                echo "Options:"
                echo "  --install-dir DIR    Installation directory (default: /usr/local/bin)"
                echo "  --skip-verify        Skip installation verification"
                echo "  --help               Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Run installation steps
    detect_system
    check_dependencies
    get_latest_version
    
    # Download and install
    TEMP_DIR=""
    BINARY_PATH=$(download_binary "$LATEST_VERSION" "$OS" "$ARCH")
    TEMP_DIR=$(dirname "$BINARY_PATH")
    
    install_binary "$BINARY_PATH" "$INSTALL_DIR"
    setup_config
    
    if [[ "$SKIP_VERIFY" != "true" ]]; then
        verify_installation
    fi
    
    cleanup "$TEMP_DIR"
    show_post_install_info
}

# Run main function
main "$@" 