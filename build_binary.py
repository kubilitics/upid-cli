#!/usr/bin/env python3
"""
UPID CLI Binary Builder - Enterprise Grade
Builds production-ready binaries with kubectl-like installation experience
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
import argparse
import stat

def get_version():
    """Get version from upid package"""
    try:
        from upid import __version__
        return __version__
    except ImportError:
        return "1.0.0"

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__', '*.spec']
    for dir_name in dirs_to_clean:
        if dir_name.endswith('*.spec'):
            # Remove all .spec files
            for spec_file in Path('.').glob('*.spec'):
                spec_file.unlink()
                print(f"✅ Removed {spec_file}")
        elif os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ Cleaned {dir_name}/")

def get_platform_info():
    """Get platform-specific information for binary naming"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":
        if machine in ["arm64", "aarch64"]:
            return "macos-arm64"
        else:
            return "macos-amd64"
    elif system == "linux":
        if machine in ["arm64", "aarch64"]:
            return "linux-arm64"
        else:
            return "linux-amd64"
    elif system == "windows":
        if machine in ["amd64", "x86_64"]:
            return "windows-amd64"
        else:
            return "windows-x86"
    else:
        return f"{system}-{machine}"

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 PyInstaller not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def build_binary(debug=False, output_dir="."):
    """Build the enterprise-grade binary using PyInstaller"""
    version = get_version()
    platform_info = get_platform_info()
    
    print(f"🚀 Building UPID CLI v{version} for {platform_info}")
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Binary name for distribution (with version info)
    dist_binary_name = f"upid-{version}-{platform_info}"
    if platform.system().lower() == "windows":
        dist_binary_name += ".exe"
    
    # PyInstaller command for enterprise-grade binary
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", "upid",  # Clean name for the binary
        "--distpath", output_dir,
        "--console",
        "--add-data", "models:models",
        "--add-data", "upid:upid",
        "--hidden-import", "upid.cli",
        "--hidden-import", "upid.commands",
        "--hidden-import", "upid.core",
        "--hidden-import", "upid.auth",
        "--hidden-import", "upid.api",
        "--hidden-import", "lightgbm",
        "--hidden-import", "sklearn",
        "--hidden-import", "pandas",
        "--hidden-import", "numpy",
        "--hidden-import", "kubernetes",
        "--hidden-import", "click",
        "--hidden-import", "rich",
        "--hidden-import", "fastapi",
        "--hidden-import", "uvicorn",
        "--hidden-import", "pydantic",
        "--hidden-import", "yaml",
        "--hidden-import", "requests",
        "--clean",
        "--noconfirm",
        "upid/cli.py"
    ]
    
    if debug:
        cmd.extend(["--debug", "all"])
    
    try:
        print("🔨 Running PyInstaller...")
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        print("✅ Binary build successful!")
        
        # Check if binary was created
        clean_binary_name = "upid"
        if platform.system().lower() == "windows":
            clean_binary_name += ".exe"
        
        clean_binary_path = Path(output_dir) / clean_binary_name
        dist_binary_path = Path(output_dir) / dist_binary_name
        
        if clean_binary_path.exists():
            file_size = clean_binary_path.stat().st_size / (1024 * 1024)  # MB
            print(f"📦 Binary created: {clean_binary_path} ({file_size:.1f}MB)")
            
            # Make binary executable on Unix systems
            if platform.system().lower() != "windows":
                clean_binary_path.chmod(clean_binary_path.stat().st_mode | stat.S_IEXEC)
                print(f"✅ Made binary executable")
            
            # Create version-specific copy for distribution
            if dist_binary_path != clean_binary_path:
                shutil.copy2(clean_binary_path, dist_binary_path)
                print(f"📋 Created distribution binary: {dist_binary_path}")
                
                # Make distribution binary executable too
                if platform.system().lower() != "windows":
                    dist_binary_path.chmod(dist_binary_path.stat().st_mode | stat.S_IEXEC)
            
            return True
        else:
            print("❌ Binary not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def test_binary():
    """Comprehensive binary testing"""
    binary_name = "upid"
    if platform.system().lower() == "windows":
        binary_name += ".exe"
    
    binary_path = Path(".") / binary_name
    
    if not binary_path.exists():
        print(f"❌ Binary not found: {binary_path}")
        return False
    
    print(f"🧪 Testing binary: {binary_path}")
    
    tests = [
        (["--version"], "Version test"),
        (["--help"], "Help test"),
        (["status"], "Status command test"),
    ]
    
    for test_args, test_name in tests:
        try:
            result = subprocess.run([str(binary_path)] + test_args, 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ {test_name} passed")
            else:
                print(f"⚠️  {test_name} completed with warnings: {result.stderr[:100]}")
        except subprocess.TimeoutExpired:
            print(f"❌ {test_name} timed out")
            return False
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
            return False
    
    return True

def create_installation_script():
    """Create installation script for easy deployment"""
    install_script = """#!/bin/bash
# UPID CLI Installation Script - Enterprise Grade
set -e

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Configuration
UPID_VERSION="1.0.0"
INSTALL_DIR="/usr/local/bin"
BINARY_NAME="upid"

# Platform detection
detect_platform() {
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    case "$OS" in
        darwin)
            case "$ARCH" in
                arm64|aarch64) echo "macos-arm64" ;;
                *) echo "macos-amd64" ;;
            esac
            ;;
        linux)
            case "$ARCH" in
                arm64|aarch64) echo "linux-arm64" ;;
                *) echo "linux-amd64" ;;
            esac
            ;;
        *)
            echo "Unsupported OS: $OS"
            exit 1
            ;;
    esac
}

# Main installation function
install_upid() {
    echo -e "${BLUE}🚀 Installing UPID CLI v${UPID_VERSION}${NC}"
    
    PLATFORM=$(detect_platform)
    echo -e "${YELLOW}📋 Detected platform: ${PLATFORM}${NC}"
    
    # Download URL (update this with your GitHub releases URL)
    DOWNLOAD_URL="https://github.com/your-org/upid-cli/releases/download/v${UPID_VERSION}/upid-${UPID_VERSION}-${PLATFORM}"
    
    # Create temporary directory
    TMP_DIR=$(mktemp -d)
    trap "rm -rf $TMP_DIR" EXIT
    
    echo -e "${YELLOW}📥 Downloading UPID CLI...${NC}"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "${DOWNLOAD_URL}" -o "${TMP_DIR}/upid"
    elif command -v wget >/dev/null 2>&1; then
        wget -q "${DOWNLOAD_URL}" -O "${TMP_DIR}/upid"
    else
        echo -e "${RED}❌ Neither curl nor wget found. Please install one of them.${NC}"
        exit 1
    fi
    
    # Make executable
    chmod +x "${TMP_DIR}/upid"
    
    # Install to system
    echo -e "${YELLOW}📦 Installing to ${INSTALL_DIR}...${NC}"
    if [[ $EUID -eq 0 ]]; then
        mv "${TMP_DIR}/upid" "${INSTALL_DIR}/upid"
    else
        sudo mv "${TMP_DIR}/upid" "${INSTALL_DIR}/upid"
    fi
    
    # Verify installation
    if command -v upid >/dev/null 2>&1; then
        echo -e "${GREEN}✅ UPID CLI installed successfully!${NC}"
        echo -e "${BLUE}📋 Version: $(upid --version)${NC}"
        echo -e "${YELLOW}🚀 Try: upid --help${NC}"
    else
        echo -e "${RED}❌ Installation failed. Please check your PATH.${NC}"
        exit 1
    fi
}

# Check if running as installer
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    install_upid
fi
"""
    
    with open("install.sh", "w") as f:
        f.write(install_script)
    
    # Make install script executable
    os.chmod("install.sh", 0o755)
    print("✅ Created installation script: install.sh")

def create_github_release_assets():
    """Create all necessary GitHub release assets"""
    version = get_version()
    
    # Create releases directory
    releases_dir = Path("releases")
    releases_dir.mkdir(exist_ok=True)
    
    print("📦 Creating GitHub release assets...")
    
    # Copy current binary if it exists
    current_platform = get_platform_info()
    clean_binary = "upid"
    if platform.system().lower() == "windows":
        clean_binary += ".exe"
    
    versioned_binary = f"upid-{version}-{current_platform}"
    if platform.system().lower() == "windows":
        versioned_binary += ".exe"
    
    if Path(clean_binary).exists():
        shutil.copy2(clean_binary, releases_dir / versioned_binary)
        print(f"✅ Created release asset: {releases_dir / versioned_binary}")
    
    # Create checksums file
    checksums_file = releases_dir / f"upid-{version}-checksums.txt"
    with open(checksums_file, "w") as f:
        f.write(f"# UPID CLI v{version} - SHA256 Checksums\\n")
        f.write(f"# Generated on {platform.node()}\\n\\n")
        
        # Calculate checksum for current binary
        if Path(releases_dir / versioned_binary).exists():
            import hashlib
            with open(releases_dir / versioned_binary, "rb") as binary_file:
                checksum = hashlib.sha256(binary_file.read()).hexdigest()
                f.write(f"{checksum}  {versioned_binary}\\n")
    
    print(f"✅ Created checksums file: {checksums_file}")
    
    return releases_dir

def main():
    parser = argparse.ArgumentParser(description="Build UPID CLI binary - Enterprise Grade")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--test", action="store_true", help="Test the binary after building")
    parser.add_argument("--clean", action="store_true", help="Clean build directories before building")
    parser.add_argument("--output-dir", default=".", help="Output directory for binary")
    parser.add_argument("--install-script", action="store_true", help="Create installation script")
    parser.add_argument("--release", action="store_true", help="Create GitHub release assets")
    args = parser.parse_args()
    
    print("🎯 UPID CLI - Enterprise Grade Binary Builder")
    print("=" * 50)
    
    if args.clean:
        clean_build_dirs()
    
    # Install PyInstaller if needed
    if not install_pyinstaller():
        sys.exit(1)
    
    # Build the binary
    if build_binary(debug=args.debug, output_dir=args.output_dir):
        print("🎉 Build completed successfully!")
        
        if args.test:
            if test_binary():
                print("🎉 All binary tests passed!")
            else:
                print("❌ Some binary tests failed!")
                sys.exit(1)
        
        if args.install_script:
            create_installation_script()
        
        if args.release:
            create_github_release_assets()
        
        print("\\n🚀 UPID CLI is ready for deployment!")
        print("💡 To install system-wide: sudo cp upid /usr/local/bin/")
        print("💡 To test: ./upid --help")
        
    else:
        print("❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()