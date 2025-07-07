#!/usr/bin/env python3
"""
Improved Binary Builder for UPID CLI
Handles Python 3.13 compatibility and provides better error handling
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class ImprovedBinaryBuilder:
    """Build standalone binaries for UPID CLI with better error handling"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.dist_dir.mkdir(exist_ok=True)
        self.build_dir = self.project_root / "build"
        self.build_dir.mkdir(exist_ok=True)
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        console.print("\n[bold cyan]🔍 Checking dependencies...[/bold cyan]")
        
        required_packages = ['pyinstaller', 'rich', 'click', 'requests', 'pyyaml']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                console.print(f"[green]✅ {package}[/green]")
            except ImportError:
                missing_packages.append(package)
                console.print(f"[red]❌ {package} (missing)[/red]")
        
        if missing_packages:
            console.print(f"\n[yellow]Installing missing packages: {', '.join(missing_packages)}[/yellow]")
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
            console.print("[green]✅ Dependencies installed[/green]")
        
        return True
    
    def build_binaries(self):
        """Build binaries for current platform with better error handling"""
        console.print("\n" + "="*80)
        console.print("[bold blue]🔨 UPID CLI - Improved Binary Builder[/bold blue]")
        console.print("="*80)
        
        # Check dependencies first
        self.check_dependencies()
        
        # Get current platform
        current_platform = platform.system().lower()
        current_arch = platform.machine().lower()
        
        console.print(f"[cyan]Current platform: {current_platform} {current_arch}[/cyan]")
        console.print(f"[cyan]Python version: {sys.version}[/cyan]")
        
        # Build for current platform only (cross-compilation not supported)
        self.build_for_current_platform()
        
        self.show_results()
        self.create_install_scripts()
        
    def build_for_current_platform(self):
        """Build binary for current platform with improved error handling"""
        platform_name = platform.system().lower()
        arch = platform.machine().lower()
        
        console.print(f"\n[bold cyan]Building for {platform_name} {arch}...[/bold cyan]")
        
        # Determine binary name
        if platform_name == "darwin":
            target = f"upid-{platform_name}-{arch}"
        elif platform_name == "linux":
            target = f"upid-{platform_name}-{arch}"
        elif platform_name == "windows":
            target = f"upid-{platform_name}-{arch}.exe"
        else:
            target = f"upid-{platform_name}-{arch}"
        
        try:
            # Clean previous builds
            if (self.dist_dir / target).exists():
                (self.dist_dir / target).unlink()
            
            # Build command with simplified options
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--name", target,
                "--distpath", str(self.dist_dir),
                "--workpath", str(self.build_dir),
                "--specpath", str(self.build_dir),
                "--clean",
                "--noconfirm",
                "--log-level", "WARN",  # Reduce log noise
                str(self.project_root / "upid_main.py")
            ]
            
            # Remove problematic options for Python 3.13
            console.print(f"Running: {' '.join(cmd[:10])}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode == 0:
                binary_path = self.dist_dir / target
                if platform_name == "windows":
                    binary_path = binary_path.with_suffix(".exe")
                
                if binary_path.exists():
                    # Make executable on Unix systems
                    if platform_name != "windows":
                        os.chmod(binary_path, 0o755)
                    
                    size = binary_path.stat().st_size / (1024 * 1024)  # MB
                    console.print(f"[green]✅ Built {target} ({size:.1f} MB)[/green]")
                    console.print(f"[green]   Location: {binary_path}[/green]")
                    
                    # Test the binary
                    self.test_binary(binary_path)
                    
                else:
                    console.print(f"[red]❌ Binary not found at {binary_path}[/red]")
                    if result.stderr:
                        console.print(f"Error: {result.stderr}")
            else:
                console.print(f"[red]❌ Build failed for {platform_name} {arch}[/red]")
                if result.stderr:
                    console.print(f"Error: {result.stderr}")
                if result.stdout:
                    console.print(f"Output: {result.stdout}")
                    
        except subprocess.TimeoutExpired:
            console.print(f"[yellow]⚠️  Build timed out for {platform_name} {arch}[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Build error for {platform_name} {arch}: {e}[/red]")
    
    def test_binary(self, binary_path):
        """Test the built binary"""
        console.print(f"\n[bold cyan]Testing binary: {binary_path.name}[/bold cyan]")
        
        try:
            # Test help command
            result = subprocess.run(
                [str(binary_path), "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                console.print("[green]✅ Binary test successful - help command works[/green]")
                
                # Test version command
                version_result = subprocess.run(
                    [str(binary_path), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if version_result.returncode == 0:
                    console.print(f"[green]✅ Version: {version_result.stdout.strip()}[/green]")
                else:
                    console.print("[yellow]⚠️  Version command failed[/yellow]")
            else:
                console.print(f"[red]❌ Binary test failed: {result.stderr}[/red]")
                
        except Exception as e:
            console.print(f"[red]❌ Binary test error: {e}[/red]")
    
    def create_install_scripts(self):
        """Create installation scripts for all platforms"""
        console.print(f"\n[bold cyan]Creating installation scripts...[/bold cyan]")
        
        # Create shell installer
        install_script = self.project_root / "install.sh"
        install_content = """#!/bin/bash
# UPID CLI Installation Script
set -e

# Colors
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

# Detect OS and architecture
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m | tr '[:upper:]' '[:lower:]')"

# Map architecture
case $ARCH in
    x86_64) ARCH="x86_64" ;;
    amd64) ARCH="x86_64" ;;
    arm64) ARCH="arm64" ;;
    aarch64) ARCH="arm64" ;;
    *) echo -e "${RED}Unsupported architecture: $ARCH${NC}" && exit 1 ;;
esac

# Map OS
case $OS in
    darwin) OS="darwin" ;;
    linux) OS="linux" ;;
    *) echo -e "${RED}Unsupported OS: $OS${NC}" && exit 1 ;;
esac

echo -e "${GREEN}Installing UPID CLI...${NC}"
echo -e "${YELLOW}OS: $OS, Architecture: $ARCH${NC}"

# Check if binary exists locally
BINARY_PATH="./dist/upid-$OS-$ARCH"
if [ -f "$BINARY_PATH" ]; then
    echo -e "${YELLOW}Using local binary: $BINARY_PATH${NC}"
    sudo cp "$BINARY_PATH" /usr/local/bin/upid
    sudo chmod +x /usr/local/bin/upid
else
    echo -e "${RED}Local binary not found: $BINARY_PATH${NC}"
    echo -e "${YELLOW}Please build the binary first using: python3 build_binary_fixed.py${NC}"
    exit 1
fi

# Verify installation
if command -v upid &> /dev/null; then
    echo -e "${GREEN}✅ UPID CLI installed successfully!${NC}"
    echo -e "${GREEN}Version: $(upid --version)${NC}"
    echo -e "${YELLOW}Run 'upid --help' to get started${NC}"
else
    echo -e "${RED}❌ Installation failed${NC}"
    exit 1
fi
"""
        
        with open(install_script, 'w') as f:
            f.write(install_content)
        
        os.chmod(install_script, 0o755)
        console.print(f"[green]✅ Created installation script: {install_script}[/green]")
        
        # Create Windows installer
        install_ps1 = self.project_root / "install.ps1"
        ps1_content = """# UPID CLI Windows Installation Script
param(
    [string]$Architecture = "x86_64"
)

Write-Host "Installing UPID CLI..." -ForegroundColor Green

# Check if binary exists locally
$BinaryPath = ".\\dist\\upid-windows-$Architecture.exe"
if (Test-Path $BinaryPath) {
    Write-Host "Using local binary: $BinaryPath" -ForegroundColor Yellow
    
    # Copy to system path
    $SystemPath = "$env:ProgramFiles\\UPID CLI"
    if (!(Test-Path $SystemPath)) {
        New-Item -ItemType Directory -Path $SystemPath -Force
    }
    
    Copy-Item $BinaryPath "$SystemPath\\upid.exe" -Force
    
    # Add to PATH
    $CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    if ($CurrentPath -notlike "*UPID CLI*") {
        [Environment]::SetEnvironmentVariable("PATH", "$CurrentPath;$SystemPath", "Machine")
    }
    
    Write-Host "✅ UPID CLI installed successfully!" -ForegroundColor Green
    Write-Host "Please restart your terminal to use 'upid' command" -ForegroundColor Yellow
} else {
    Write-Host "Local binary not found: $BinaryPath" -ForegroundColor Red
    Write-Host "Please build the binary first using: python build_binary_fixed.py" -ForegroundColor Yellow
    exit 1
}
"""
        
        with open(install_ps1, 'w') as f:
            f.write(ps1_content)
        
        console.print(f"[green]✅ Created Windows installer: {install_ps1}[/green]")
    
    def show_results(self):
        """Show build results"""
        console.print("\n" + "="*80)
        console.print("[bold blue]📊 Binary Build Results[/bold blue]")
        console.print("="*80)
        
        binaries = list(self.dist_dir.glob("upid-*"))
        
        if binaries:
            table = Table(title="Built Binaries")
            table.add_column("Binary", style="cyan")
            table.add_column("Size", style="green")
            table.add_column("Status", style="yellow")
            
            for binary in binaries:
                size = binary.stat().st_size / (1024 * 1024)  # MB
                table.add_row(binary.name, f"{size:.1f} MB", "✅ Ready")
            
            console.print(table)
        else:
            console.print("[red]❌ No binaries were built successfully[/red]")
        
        console.print("\n[bold cyan]Next Steps:[/bold cyan]")
        console.print("1. For Mac/Linux: Run ./install.sh")
        console.print("2. For Windows: Run .\\install.ps1")
        console.print("3. Test the binary: ./dist/upid-<platform>-<arch> --help")

def main():
    """Main function"""
    builder = ImprovedBinaryBuilder()
    builder.build_binaries()

if __name__ == "__main__":
    main() 