#!/usr/bin/env python3
"""
Build standalone binaries for UPID CLI
Creates platform-specific binaries like kubectl
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import ROUNDED

console = Console()

class BinaryBuilder:
    """Build standalone binaries for UPID CLI"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.dist_dir.mkdir(exist_ok=True)
        
    def build_binaries(self):
        """Build binaries for all supported platforms"""
        console.print("\n" + "="*80)
        console.print("[bold blue]🔨 UPID CLI - Binary Builder[/bold blue]")
        console.print("="*80)
        
        # Get current platform
        current_platform = platform.system().lower()
        current_arch = platform.machine().lower()
        
        console.print(f"[cyan]Current platform: {current_platform} {current_arch}[/cyan]")
        
        # Build for current platform
        self.build_for_platform(current_platform, current_arch)
        
        # Optionally build for other platforms
        if current_platform == "darwin":
            self.build_for_platform("linux", "x86_64")
        elif current_platform == "linux":
            self.build_for_platform("darwin", "x86_64")
        
        self.show_results()
        
    def build_for_platform(self, platform_name: str, arch: str):
        """Build binary for specific platform"""
        console.print(f"\n[bold cyan]Building for {platform_name} {arch}...[/bold cyan]")
        
        try:
            # Set environment variables for cross-compilation
            env = os.environ.copy()
            
            if platform_name == "darwin":
                env["PYTHONPATH"] = str(self.project_root)
                target = f"upid-{platform_name}-{arch}"
            elif platform_name == "linux":
                env["PYTHONPATH"] = str(self.project_root)
                target = f"upid-{platform_name}-{arch}"
            else:
                target = f"upid-{platform_name}-{arch}"
            
            # Build command
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--name", target,
                "--distpath", str(self.dist_dir),
                "--workpath", str(self.project_root / "build"),
                "--specpath", str(self.project_root / "build"),
                "--clean",
                "--noconfirm",
                str(self.project_root / "upid" / "cli.py")
            ]
            
            # Add platform-specific options
            if platform_name == "darwin":
                cmd.extend(["--target-architecture", "universal2"])
            elif platform_name == "linux":
                cmd.extend(["--target-architecture", "x86_64"])
            
            console.print(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
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
                else:
                    console.print(f"[red]❌ Binary not found at {binary_path}[/red]")
            else:
                console.print(f"[red]❌ Build failed for {platform_name} {arch}[/red]")
                if result.stderr:
                    console.print(f"Error: {result.stderr[:200]}...")
                    
        except subprocess.TimeoutExpired:
            console.print(f"[yellow]⚠️  Build timed out for {platform_name} {arch}[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Build error for {platform_name} {arch}: {e}[/red]")
    
    def create_install_script(self):
        """Create installation script like kubectl"""
        console.print(f"\n[bold cyan]Creating installation script...[/bold cyan]")
        
        install_script = self.project_root / "install.sh"
        
        script_content = f"""#!/bin/bash
# UPID CLI Installation Script
# Installs UPID CLI like kubectl

set -e

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Detect OS and architecture
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m | tr '[:upper:]' '[:lower:]')"

# Map architecture
case $ARCH in
    x86_64) ARCH="x86_64" ;;
    amd64) ARCH="x86_64" ;;
    arm64) ARCH="arm64" ;;
    aarch64) ARCH="arm64" ;;
    *) echo -e "${{RED}}Unsupported architecture: $ARCH${{NC}}" && exit 1 ;;
esac

# Map OS
case $OS in
    darwin) OS="darwin" ;;
    linux) OS="linux" ;;
    *) echo -e "${{RED}}Unsupported OS: $OS${{NC}}" && exit 1 ;;
esac

# GitHub release URL
RELEASE_URL="https://github.com/upid/upid-cli/releases/latest/download"
BINARY_NAME="upid-$OS-$ARCH"

echo -e "${{GREEN}}Installing UPID CLI...${{NC}}"
echo -e "${{YELLOW}}OS: $OS, Architecture: $ARCH${{NC}}"

# Download binary
echo -e "${{YELLOW}}Downloading UPID CLI binary...${{NC}}"
curl -L -o /tmp/upid "$RELEASE_URL/$BINARY_NAME"

# Make executable
chmod +x /tmp/upid

# Install to system path
if [[ "$OS" == "darwin" ]]; then
    sudo mv /tmp/upid /usr/local/bin/upid
else
    sudo mv /tmp/upid /usr/local/bin/upid
fi

# Verify installation
if command -v upid &> /dev/null; then
    echo -e "${{GREEN}}✅ UPID CLI installed successfully!${{NC}}"
    echo -e "${{GREEN}}Version: $(upid --version)${{NC}}"
    echo -e "${{YELLOW}}Run 'upid --help' to get started${{NC}}"
else
    echo -e "${{RED}}❌ Installation failed${{NC}}"
    exit 1
fi
"""
        
        with open(install_script, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(install_script, 0o755)
        
        console.print(f"[green]✅ Created installation script: {install_script}[/green]")
    
    def create_windows_installer(self):
        """Create Windows installer script"""
        console.print(f"\n[bold cyan]Creating Windows installer...[/bold cyan]")
        
        install_ps1 = self.project_root / "install.ps1"
        
        script_content = f"""# UPID CLI Windows Installation Script
# Run with: powershell -ExecutionPolicy Bypass -File install.ps1

param(
    [string]$Version = "latest"
)

# Colors for output
$Red = "\\033[0;31m"
$Green = "\\033[0;32m"
$Yellow = "\\033[1;33m"
$NC = "\\033[0m"

Write-Host "Installing UPID CLI..." -ForegroundColor Green

# Detect architecture
$Arch = if ([Environment]::Is64BitOperatingSystem) {{ "x86_64" }} else {{ "x86" }}

# GitHub release URL
$ReleaseUrl = "https://github.com/upid/upid-cli/releases/latest/download"
$BinaryName = "upid-windows-$Arch.exe"

Write-Host "Architecture: $Arch" -ForegroundColor Yellow

# Download binary
Write-Host "Downloading UPID CLI binary..." -ForegroundColor Yellow
$TempPath = "$env:TEMP\\upid.exe"
Invoke-WebRequest -Uri "$ReleaseUrl/$BinaryName" -OutFile $TempPath

# Install to system path
$InstallPath = "$env:ProgramFiles\\upid\\upid.exe"
New-Item -ItemType Directory -Force -Path "$env:ProgramFiles\\upid" | Out-Null
Move-Item -Path $TempPath -Destination $InstallPath -Force

# Add to PATH
$CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
if ($CurrentPath -notlike "*upid*") {{
    [Environment]::SetEnvironmentVariable("PATH", "$CurrentPath;$env:ProgramFiles\\upid", "Machine")
}}

Write-Host "✅ UPID CLI installed successfully!" -ForegroundColor Green
Write-Host "Please restart your terminal to use 'upid' command" -ForegroundColor Yellow
"""
        
        with open(install_ps1, 'w') as f:
            f.write(script_content)
        
        console.print(f"[green]✅ Created Windows installer: {install_ps1}[/green]")
    
    def show_results(self):
        """Show build results"""
        console.print("\n" + "="*80)
        console.print("[bold blue]📊 Binary Build Results[/bold blue]")
        console.print("="*80)
        
        # List built binaries
        binaries = list(self.dist_dir.glob("upid-*"))
        
        if binaries:
            table = Table(title="Built Binaries", box=ROUNDED)
            table.add_column("Binary", style="cyan")
            table.add_column("Size", style="green")
            table.add_column("Platform", style="yellow")
            
            for binary in binaries:
                size_mb = binary.stat().st_size / (1024 * 1024)
                platform_name = binary.name.replace("upid-", "").replace(".exe", "")
                
                table.add_row(
                    binary.name,
                    f"{size_mb:.1f} MB",
                    platform_name
                )
            
            console.print(table)
            
            # Summary
            total_size = sum(b.stat().st_size for b in binaries) / (1024 * 1024)
            
            summary_panel = Panel(
                f"Total Binaries: {len(binaries)}\n"
                f"Total Size: {total_size:.1f} MB\n"
                f"Location: {self.dist_dir}",
                title="[bold blue]Build Summary[/bold blue]",
                border_style="blue"
            )
            
            console.print(summary_panel)
            
            # Installation instructions
            console.print("\n[bold cyan]📋 Installation Instructions[/bold cyan]")
            console.print("1. Download the appropriate binary for your platform")
            console.print("2. Make it executable: chmod +x upid-<platform>")
            console.print("3. Move to PATH: sudo mv upid-<platform> /usr/local/bin/upid")
            console.print("4. Test: upid --help")
            
        else:
            console.print("[red]❌ No binaries were built successfully[/red]")
        
        console.print("\n" + "="*80)

def main():
    """Main binary builder"""
    try:
        builder = BinaryBuilder()
        builder.build_binaries()
        builder.create_install_script()
        builder.create_windows_installer()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Build interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Build failed: {e}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main() 