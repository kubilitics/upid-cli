#!/usr/bin/env python3
"""
UPID CLI Binary Builder
Builds production-ready binaries using PyInstaller
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
import argparse

def get_version():
    """Get version from upid package"""
    try:
        from upid import __version__
        return __version__
    except ImportError:
        return "1.0.0"

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ Cleaned {dir_name}/")

def get_platform_info():
    """Get platform-specific information"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":
        if machine in ["arm64", "aarch64"]:
            return "macos-arm64"
        else:
            return "macos-x64"
    elif system == "linux":
        if machine in ["arm64", "aarch64"]:
            return "linux-arm64"
        else:
            return "linux-x64"
    elif system == "windows":
        if machine in ["amd64", "x86_64"]:
            return "windows-x64"
        else:
            return "windows-x86"
    else:
        return f"{system}-{machine}"

def build_binary(debug=False, output_dir="."):
    """Build the binary using PyInstaller"""
    version = get_version()
    platform_info = get_platform_info()
    
    print(f"🚀 Building UPID CLI v{version} for {platform_info}")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", f"upid-{version}-{platform_info}",
        "--distpath", output_dir,  # Output to specified directory
        "--console",
        "--add-data", "models:models",
        "--add-data", "upid:upid",
        "--hidden-import", "upid.cli",
        "--hidden-import", "upid.commands",
        "--hidden-import", "upid.core",
        "--hidden-import", "upid.auth",
        "--hidden-import", "lightgbm",
        "--hidden-import", "sklearn",
        "--hidden-import", "pandas",
        "--hidden-import", "numpy",
        "--hidden-import", "kubernetes",
        "--hidden-import", "click",
        "--hidden-import", "rich",
        "--hidden-import", "fastapi",
        "--hidden-import", "uvicorn",
        "--clean",
        "upid/cli.py"
    ]
    
    if debug:
        cmd.extend(["--debug", "all"])
    
    try:
        print("🔨 Running PyInstaller...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Binary build successful!")
        
        # Check if binary was created
        binary_name = f"upid-{version}-{platform_info}"
        if platform.system().lower() == "windows":
            binary_name += ".exe"
        
        binary_path = Path(output_dir) / binary_name
        if binary_path.exists():
            file_size = binary_path.stat().st_size / (1024 * 1024)  # MB
            print(f"📦 Binary created: {binary_path} ({file_size:.1f}MB)")
            
            # Create a symlink for easier access
            symlink_name = "upid"
            if platform.system().lower() == "windows":
                symlink_name += ".exe"
            
            symlink_path = Path(output_dir) / symlink_name
            if symlink_path.exists():
                symlink_path.unlink()
            
            try:
                symlink_path.symlink_to(binary_name)
                print(f"🔗 Created symlink: {symlink_path} -> {binary_name}")
            except OSError:
                # Fallback: copy the file if symlink fails
                shutil.copy2(binary_path, symlink_path)
                print(f"📋 Created copy: {symlink_path}")
            
            return True
        else:
            print("❌ Binary not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def test_binary():
    """Test the built binary"""
    platform_info = get_platform_info()
    version = get_version()
    binary_name = f"upid-{version}-{platform_info}"
    
    if platform.system().lower() == "windows":
        binary_name += ".exe"
    
    binary_path = Path(".") / binary_name
    
    if not binary_path.exists():
        print(f"❌ Binary not found: {binary_path}")
        return False
    
    print(f"🧪 Testing binary: {binary_path}")
    
    # Test version command
    try:
        result = subprocess.run([str(binary_path), "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Version test passed: {result.stdout.strip()}")
        else:
            print(f"❌ Version test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Binary test timed out")
        return False
    except Exception as e:
        print(f"❌ Binary test error: {e}")
        return False
    
    # Test help command
    try:
        result = subprocess.run([str(binary_path), "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and "UPID CLI" in result.stdout:
            print("✅ Help test passed")
            return True
        else:
            print(f"❌ Help test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Help test timed out")
        return False
    except Exception as e:
        print(f"❌ Help test error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Build UPID CLI binary")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--test", action="store_true", help="Test the binary after building")
    parser.add_argument("--clean", action="store_true", help="Clean build directories before building")
    parser.add_argument("--output-dir", default=".", help="Output directory for binary (default: current directory)")
    args = parser.parse_args()
    
    if args.clean:
        clean_build_dirs()
    
    # Check if PyInstaller is available
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller not found. Please install it with: pip install pyinstaller")
        sys.exit(1)
    
    # Build the binary
    if build_binary(debug=args.debug, output_dir=args.output_dir):
        print("🎉 Build completed successfully!")
        
        if args.test:
            if test_binary():
                print("🎉 Binary test passed!")
            else:
                print("❌ Binary test failed!")
                sys.exit(1)
    else:
        print("❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()