# UPID CLI Windows Installation Script
# Run with: powershell -ExecutionPolicy Bypass -File install.ps1

param(
    [string]$Version = "latest"
)

# Colors for output
$Red = "\033[0;31m"
$Green = "\033[0;32m"
$Yellow = "\033[1;33m"
$NC = "\033[0m"

Write-Host "Installing UPID CLI..." -ForegroundColor Green

# Detect architecture
$Arch = if ([Environment]::Is64BitOperatingSystem) { "x86_64" } else { "x86" }

# GitHub release URL
$ReleaseUrl = "https://github.com/upid/upid-cli/releases/latest/download"
$BinaryName = "upid-windows-$Arch.exe"

Write-Host "Architecture: $Arch" -ForegroundColor Yellow

# Download binary
Write-Host "Downloading UPID CLI binary..." -ForegroundColor Yellow
$TempPath = "$env:TEMP\upid.exe"
Invoke-WebRequest -Uri "$ReleaseUrl/$BinaryName" -OutFile $TempPath

# Install to system path
$InstallPath = "$env:ProgramFiles\upid\upid.exe"
New-Item -ItemType Directory -Force -Path "$env:ProgramFiles\upid" | Out-Null
Move-Item -Path $TempPath -Destination $InstallPath -Force

# Add to PATH
$CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
if ($CurrentPath -notlike "*upid*") {
    [Environment]::SetEnvironmentVariable("PATH", "$CurrentPath;$env:ProgramFiles\upid", "Machine")
}

Write-Host "✅ UPID CLI installed successfully!" -ForegroundColor Green
Write-Host "Please restart your terminal to use 'upid' command" -ForegroundColor Yellow
