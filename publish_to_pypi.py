#!/usr/bin/env python3
"""
Publish UPID CLI to PyPI
"""

import os
import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class PyPIPublisher:
    """Publish UPID CLI to PyPI"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        
    def clean_dist(self):
        """Clean previous distributions"""
        console.print("[cyan]Cleaning previous distributions...[/cyan]")
        
        if self.dist_dir.exists():
            for file in self.dist_dir.glob("*"):
                file.unlink()
            console.print("[green]✅ Cleaned dist directory[/green]")
        else:
            self.dist_dir.mkdir(exist_ok=True)
            console.print("[green]✅ Created dist directory[/green]")
    
    def build_package(self):
        """Build the package for distribution"""
        console.print("[cyan]Building package...[/cyan]")
        
        try:
            # Build source distribution and wheel
            cmd = [
                sys.executable, "setup.py",
                "sdist", "bdist_wheel"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                console.print("[green]✅ Package built successfully[/green]")
                
                # List built packages
                packages = list(self.dist_dir.glob("*"))
                if packages:
                    table = Table(title="Built Packages", box=box.ROUNDED)
                    table.add_column("Package", style="cyan")
                    table.add_column("Size", style="green")
                    
                    for package in packages:
                        size_mb = package.stat().st_size / (1024 * 1024)
                        table.add_row(
                            package.name,
                            f"{size_mb:.1f} MB"
                        )
                    
                    console.print(table)
                else:
                    console.print("[red]❌ No packages found in dist directory[/red]")
                    return False
                
                return True
            else:
                console.print(f"[red]❌ Build failed: {result.stderr}[/red]")
                return False
                
        except subprocess.TimeoutExpired:
            console.print("[yellow]⚠️  Build timed out[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]❌ Build error: {e}[/red]")
            return False
    
    def check_package(self):
        """Check the package before publishing"""
        console.print("[cyan]Checking package...[/cyan]")
        
        try:
            # Check with twine
            cmd = [
                sys.executable, "-m", "twine", "check",
                str(self.dist_dir / "*")
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                console.print("[green]✅ Package check passed[/green]")
                return True
            else:
                console.print(f"[red]❌ Package check failed: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Package check error: {e}[/red]")
            return False
    
    def publish_to_test_pypi(self):
        """Publish to Test PyPI first"""
        console.print("[cyan]Publishing to Test PyPI...[/cyan]")
        
        try:
            cmd = [
                sys.executable, "-m", "twine", "upload",
                "--repository", "testpypi",
                str(self.dist_dir / "*")
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                console.print("[green]✅ Published to Test PyPI successfully[/green]")
                console.print("[yellow]Test PyPI URL: https://test.pypi.org/project/upid-cli/[/yellow]")
                return True
            else:
                console.print(f"[red]❌ Test PyPI upload failed: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Test PyPI upload error: {e}[/red]")
            return False
    
    def publish_to_pypi(self):
        """Publish to PyPI"""
        console.print("[cyan]Publishing to PyPI...[/cyan]")
        
        try:
            cmd = [
                sys.executable, "-m", "twine", "upload",
                str(self.dist_dir / "*")
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                console.print("[green]✅ Published to PyPI successfully![/green]")
                console.print("[yellow]PyPI URL: https://pypi.org/project/upid-cli/[/yellow]")
                return True
            else:
                console.print(f"[red]❌ PyPI upload failed: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ PyPI upload error: {e}[/red]")
            return False
    
    def install_dependencies(self):
        """Install publishing dependencies"""
        console.print("[cyan]Installing publishing dependencies...[/cyan]")
        
        dependencies = [
            "twine>=4.0.0",
            "wheel>=0.37.0",
            "setuptools>=65.0.0"
        ]
        
        for dep in dependencies:
            try:
                cmd = [sys.executable, "-m", "pip", "install", dep]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    console.print(f"[green]✅ Installed {dep}[/green]")
                else:
                    console.print(f"[red]❌ Failed to install {dep}[/red]")
                    return False
                    
            except Exception as e:
                console.print(f"[red]❌ Error installing {dep}: {e}[/red]")
                return False
        
        return True
    
    def show_instructions(self):
        """Show installation instructions"""
        console.print("\n[bold cyan]📋 Installation Instructions[/bold cyan]")
        
        instructions = """
        # PyPI Installation
        pip install upid-cli
        
        # Usage
        upid --help
        
        # Binary Installation (Alternative)
        curl -L https://github.com/upid/upid-cli/releases/latest/download/install.sh | bash
        
        # Windows
        powershell -ExecutionPolicy Bypass -File install.ps1
        """
        
        console.print(instructions)
    
    def publish(self, test_only=False):
        """Main publishing process"""
        console.print("\n" + "="*80)
        console.print("[bold blue]📦 UPID CLI - PyPI Publisher[/bold blue]")
        console.print("="*80)
        
        # Install dependencies
        if not self.install_dependencies():
            console.print("[red]❌ Failed to install dependencies[/red]")
            return False
        
        # Clean previous builds
        self.clean_dist()
        
        # Build package
        if not self.build_package():
            console.print("[red]❌ Failed to build package[/red]")
            return False
        
        # Check package
        if not self.check_package():
            console.print("[red]❌ Package check failed[/red]")
            return False
        
        # Publish to Test PyPI
        if not self.publish_to_test_pypi():
            console.print("[red]❌ Failed to publish to Test PyPI[/red]")
            return False
        
        if not test_only:
            # Publish to PyPI
            if not self.publish_to_pypi():
                console.print("[red]❌ Failed to publish to PyPI[/red]")
                return False
        
        # Show instructions
        self.show_instructions()
        
        # Summary
        summary_panel = Panel(
            "✅ Package built successfully\n"
            "✅ Package check passed\n"
            "✅ Published to Test PyPI\n"
            f"{'✅ Published to PyPI' if not test_only else '⏸️  Skipped PyPI (test only)'}\n"
            "🎉 Ready for users!",
            title="[bold blue]Publishing Summary[/bold blue]",
            border_style="blue"
        )
        
        console.print(summary_panel)
        console.print("\n" + "="*80)
        
        return True

def main():
    """Main publisher"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Publish UPID CLI to PyPI")
    parser.add_argument("--test-only", action="store_true", help="Only publish to Test PyPI")
    
    args = parser.parse_args()
    
    try:
        publisher = PyPIPublisher()
        success = publisher.publish(test_only=args.test_only)
        
        if success:
            console.print("\n[bold green]🎉 Publishing completed successfully![/bold green]")
        else:
            console.print("\n[bold red]❌ Publishing failed![/bold red]")
            sys.exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Publishing interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Publishing failed: {e}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main() 