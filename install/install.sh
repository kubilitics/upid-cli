#!/bin/bash

# UPID CLI Installation Script
# Version: 2.0.0
# Platform: Linux/macOS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/your-org/upid-cli"
VERSION="v2.0.0"
INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="$HOME/.upid"

# Detect platform
detect_platform() {
    case "$(uname -s)" in
        Linux*)     
            case "$(uname -m)" in
                x86_64) echo "linux-x86_64" ;;
                aarch64|arm64) echo "linux-arm64" ;;
                *) echo "linux-x86_64" ;;
            esac
            ;;
        Darwin*)    
            case "$(uname -m)" in
                x86_64) echo "darwin-x86_64" ;;
                arm64) echo "darwin-arm64" ;;
                *) echo "darwin-arm64" ;;
            esac
            ;;
        *) echo "linux-x86_64" ;;
    esac
}

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    UPID CLI v2.0.0                          ║"
    echo "║              Kubernetes Intelligence Platform                 ║"
    echo "║                                                              ║"
    echo "║  Production Ready • Enterprise Security • ML-Powered        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print status message
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_warning "kubectl not found. Please install kubectl first:"
        echo "  https://kubernetes.io/docs/tasks/tools/install-kubectl/"
    else
        print_status "kubectl found: $(kubectl version --client --short)"
    fi
    
    # Check if Python is available (for optional features)
    if command -v python3 &> /dev/null; then
        print_status "Python 3 found: $(python3 --version)"
    else
        print_warning "Python 3 not found. Some features may be limited."
    fi
}

# Download binary
download_binary() {
    local platform=$1
    local binary_name="upid-$platform"
    local download_url="$REPO_URL/releases/download/$VERSION/$binary_name"
    
    print_status "Downloading UPID CLI binary for $platform..."
    
    # Create temporary directory
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    
    # Download binary
    if command -v curl &> /dev/null; then
        curl -L -o "$binary_name" "$download_url"
    elif command -v wget &> /dev/null; then
        wget -O "$binary_name" "$download_url"
    else
        print_error "Neither curl nor wget found. Please install one of them."
        exit 1
    fi
    
    # Make executable
    chmod +x "$binary_name"
    
    # Move to install directory
    if [ -w "$INSTALL_DIR" ]; then
        sudo mv "$binary_name" "$INSTALL_DIR/upid"
    else
        print_warning "Cannot write to $INSTALL_DIR. Installing to $HOME/.local/bin"
        mkdir -p "$HOME/.local/bin"
        mv "$binary_name" "$HOME/.local/bin/upid"
        INSTALL_DIR="$HOME/.local/bin"
    fi
    
    # Clean up
    cd - > /dev/null
    rm -rf "$temp_dir"
    
    print_status "Binary installed to $INSTALL_DIR/upid"
}

# Create configuration directory
setup_config() {
    print_status "Setting up configuration..."
    
    mkdir -p "$CONFIG_DIR"
    
    # Create default config if it doesn't exist
    if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
        cat > "$CONFIG_DIR/config.yaml" << EOF
# UPID CLI Configuration
auth:
  default_provider: "local"
  mfa_required: false

storage:
  database_path: "$CONFIG_DIR/upid_data.db"
  backup_enabled: true

monitoring:
  metrics_interval: 60
  alert_threshold: 0.8

cloud:
  aws:
    enabled: false
  gcp:
    enabled: false
  azure:
    enabled: false
EOF
        print_status "Configuration file created: $CONFIG_DIR/config.yaml"
    fi
}

# Initialize UPID CLI
initialize_upid() {
    print_status "Initializing UPID CLI..."
    
    # Check if binary is in PATH
    if command -v upid &> /dev/null; then
        # Initialize with default settings
        upid init --yes || true
        print_status "UPID CLI initialized successfully"
    else
        print_warning "UPID CLI binary not found in PATH. Please add $INSTALL_DIR to your PATH"
    fi
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    if command -v upid &> /dev/null; then
        local version=$(upid --version 2>/dev/null || echo "Unknown")
        print_status "UPID CLI installed successfully: $version"
        
        # Test basic functionality
        if upid --help &> /dev/null; then
            print_status "Basic functionality test passed"
        else
            print_warning "Basic functionality test failed"
        fi
    else
        print_error "UPID CLI not found in PATH"
        print_status "Please add $INSTALL_DIR to your PATH:"
        echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
        echo "  # Add to ~/.bashrc or ~/.zshrc for persistence"
    fi
}

# Print next steps
print_next_steps() {
    echo
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Installation Complete!${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo
    echo "Next steps:"
    echo "1. Add UPID CLI to your PATH (if not already done):"
    echo "   export PATH=\"$INSTALL_DIR:\$PATH\""
    echo
    echo "2. Authenticate with UPID CLI:"
    echo "   upid auth login"
    echo
    echo "3. Analyze your cluster:"
    echo "   upid analyze cluster"
    echo
    echo "4. View the dashboard:"
    echo "   upid dashboard"
    echo
    echo "Documentation:"
    echo "- User Manual: https://docs.upid.io/user-manual"
    echo "- Quick Reference: https://docs.upid.io/quick-reference"
    echo "- Installation Guide: https://docs.upid.io/installation"
    echo
    echo "Support:"
    echo "- GitHub Issues: https://github.com/your-org/upid-cli/issues"
    echo "- Community: https://community.upid.io"
    echo "- Email: support@upid.io"
    echo
}

# Main installation function
main() {
    print_banner
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root"
        exit 1
    fi
    
    # Detect platform
    local platform=$(detect_platform)
    print_status "Detected platform: $platform"
    
    # Check prerequisites
    check_prerequisites
    
    # Download and install binary
    download_binary "$platform"
    
    # Setup configuration
    setup_config
    
    # Initialize UPID CLI
    initialize_upid
    
    # Verify installation
    verify_installation
    
    # Print next steps
    print_next_steps
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "UPID CLI Installation Script"
        echo "Usage: $0 [--help|--version|--uninstall]"
        echo
        echo "Options:"
        echo "  --help      Show this help message"
        echo "  --version   Show version information"
        echo "  --uninstall Remove UPID CLI"
        exit 0
        ;;
    --version)
        echo "UPID CLI Installation Script v2.0.0"
        exit 0
        ;;
    --uninstall)
        print_status "Uninstalling UPID CLI..."
        sudo rm -f "$INSTALL_DIR/upid"
        rm -rf "$CONFIG_DIR"
        print_status "UPID CLI uninstalled"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac 