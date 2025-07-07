# UPID CLI Windows Installation Script
param(
    [string]$Architecture = "x86_64"
)

Write-Host "Installing UPID CLI..." -ForegroundColor Green

# Check if binary exists locally
$BinaryPath = ".\dist\upid-windows-$Architecture.exe"
if (Test-Path $BinaryPath) {
    Write-Host "Using local binary: $BinaryPath" -ForegroundColor Yellow
    
    # Copy to system path
    $SystemPath = "$env:ProgramFiles\UPID CLI"
    if (!(Test-Path $SystemPath)) {
        New-Item -ItemType Directory -Path $SystemPath -Force
    }
    
    Copy-Item $BinaryPath "$SystemPath\upid.exe" -Force
    
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
