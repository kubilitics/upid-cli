# UPID CLI Installation Script for Windows
# Run with: powershell -ExecutionPolicy Bypass -File install.ps1

param(
    [string]$Version = "latest",
    [string]$InstallDir = "$env:ProgramFiles\UPID",
    [switch]$SkipVerify,
    [switch]$Help
)

# Function to write colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Header {
    Write-Host "=================================" -ForegroundColor Blue
    Write-Host "    UPID CLI Installation" -ForegroundColor Blue
    Write-Host "=================================" -ForegroundColor Blue
}

# Version and release info
$VERSION = "1.0.0"
$RELEASE_URL = "https://github.com/kubilitics/upid-cli/releases/latest/download"
$GITHUB_API = "https://api.github.com/repos/kubilitics/upid-cli/releases/latest"

# Function to show help
function Show-Help {
    Write-Host "Usage: .\install.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Version STRING     Version to install (default: latest)"
    Write-Host "  -InstallDir PATH    Installation directory (default: Program Files\UPID)"
    Write-Host "  -SkipVerify         Skip installation verification"
    Write-Host "  -Help               Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\install.ps1"
    Write-Host "  .\install.ps1 -InstallDir C:\Tools\UPID"
    Write-Host "  .\install.ps1 -SkipVerify"
}

# Function to detect system information
function Detect-System {
    Write-Status "Detecting system information..."
    
    # Detect OS
    $OS = "windows"
    
    # Detect architecture
    $ARCH = if ([Environment]::Is64BitOperatingSystem) { "x86_64" } else { "x86" }
    
    Write-Success "Detected: $OS $ARCH"
    
    return @{
        OS = $OS
        ARCH = $ARCH
    }
}

# Function to check dependencies
function Test-Dependencies {
    Write-Status "Checking dependencies..."
    
    # Check for PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Write-Error "PowerShell 5.0 or later is required"
        exit 1
    }
    
    # Check for .NET Framework
    try {
        $null = [System.Reflection.Assembly]::LoadWithPartialName("System.Web.Extensions")
        Write-Success ".NET Framework is available"
    }
    catch {
        Write-Error ".NET Framework is required but not available"
        exit 1
    }
    
    Write-Success "All dependencies are available"
}

# Function to get latest version
function Get-LatestVersion {
    Write-Status "Getting latest version information..."
    
    try {
        $response = Invoke-RestMethod -Uri $GITHUB_API -Method Get
        $LATEST_VERSION = $response.tag_name -replace "v", ""
    }
    catch {
        Write-Warning "Could not determine latest version, using default: $VERSION"
        $LATEST_VERSION = $VERSION
    }
    
    Write-Success "Latest version: $LATEST_VERSION"
    return $LATEST_VERSION
}

# Function to download binary
function Download-Binary {
    param(
        [string]$Version,
        [string]$OS,
        [string]$ARCH
    )
    
    Write-Status "Downloading UPID CLI binary..."
    
    # Construct download URL
    $BINARY_NAME = "upid-$OS-$ARCH.exe"
    $DOWNLOAD_URL = "$RELEASE_URL/$BINARY_NAME"
    
    Write-Status "Download URL: $DOWNLOAD_URL"
    
    # Create temporary directory
    $TEMP_DIR = [System.IO.Path]::GetTempPath()
    $BINARY_PATH = Join-Path $TEMP_DIR "upid.exe"
    
    try {
        # Download binary
        Invoke-WebRequest -Uri $DOWNLOAD_URL -OutFile $BINARY_PATH -UseBasicParsing
        Write-Success "Binary downloaded successfully"
    }
    catch {
        Write-Error "Failed to download binary: $($_.Exception.Message)"
        exit 1
    }
    
    # Verify binary exists
    if (Test-Path $BINARY_PATH) {
        Write-Success "Binary is available"
    }
    else {
        Write-Error "Binary was not downloaded"
        exit 1
    }
    
    return $BINARY_PATH
}

# Function to install binary
function Install-Binary {
    param(
        [string]$BinaryPath,
        [string]$InstallDir
    )
    
    Write-Status "Installing UPID CLI..."
    
    # Create installation directory if it doesn't exist
    if (!(Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
        Write-Success "Created installation directory: $InstallDir"
    }
    
    $INSTALL_PATH = Join-Path $InstallDir "upid.exe"
    
    try {
        # Copy binary
        Copy-Item -Path $BinaryPath -Destination $INSTALL_PATH -Force
        Write-Success "Binary installed to $INSTALL_PATH"
    }
    catch {
        Write-Error "Failed to install binary: $($_.Exception.Message)"
        exit 1
    }
    
    return $INSTALL_PATH
}

# Function to add to PATH
function Add-ToPath {
    param([string]$InstallDir)
    
    Write-Status "Adding UPID CLI to PATH..."
    
    $CURRENT_PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    
    if ($CURRENT_PATH -notlike "*$InstallDir*") {
        try {
            $NEW_PATH = "$CURRENT_PATH;$InstallDir"
            [Environment]::SetEnvironmentVariable("PATH", $NEW_PATH, "Machine")
            Write-Success "Added $InstallDir to system PATH"
        }
        catch {
            Write-Warning "Failed to add to system PATH: $($_.Exception.Message)"
            Write-Warning "You may need to add $InstallDir to your PATH manually"
        }
    }
    else {
        Write-Status "Installation directory is already in PATH"
    }
}

# Function to verify installation
function Test-Installation {
    param([string]$InstallPath)
    
    Write-Status "Verifying installation..."
    
    # Check if binary exists
    if (Test-Path $InstallPath) {
        Write-Success "UPID CLI binary is available"
    }
    else {
        Write-Error "UPID CLI binary not found at $InstallPath"
        exit 1
    }
    
    # Test version command
    try {
        $VERSION_OUTPUT = & $InstallPath --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "UPID CLI version: $VERSION_OUTPUT"
        }
        else {
            Write-Error "Failed to get UPID CLI version"
            exit 1
        }
    }
    catch {
        Write-Error "Failed to run UPID CLI version command: $($_.Exception.Message)"
        exit 1
    }
    
    # Test help command
    try {
        $HELP_OUTPUT = & $InstallPath --help 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "UPID CLI help command works"
        }
        else {
            Write-Error "UPID CLI help command failed"
            exit 1
        }
    }
    catch {
        Write-Error "Failed to run UPID CLI help command: $($_.Exception.Message)"
        exit 1
    }
}

# Function to create configuration directory
function Setup-Config {
    Write-Status "Setting up configuration directory..."
    
    $CONFIG_DIR = "$env:USERPROFILE\.upid"
    
    if (!(Test-Path $CONFIG_DIR)) {
        New-Item -ItemType Directory -Path $CONFIG_DIR -Force | Out-Null
        Write-Success "Created configuration directory: $CONFIG_DIR"
    }
    else {
        Write-Status "Configuration directory already exists: $CONFIG_DIR"
    }
    
    # Create default config file if it doesn't exist
    $CONFIG_FILE = Join-Path $CONFIG_DIR "config.yaml"
    if (!(Test-Path $CONFIG_FILE)) {
        $CONFIG_CONTENT = @"
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
"@
        
        $CONFIG_CONTENT | Out-File -FilePath $CONFIG_FILE -Encoding UTF8
        Write-Success "Created default configuration file: $CONFIG_FILE"
    }
    
    # Create logs directory
    $LOGS_DIR = Join-Path $CONFIG_DIR "logs"
    if (!(Test-Path $LOGS_DIR)) {
        New-Item -ItemType Directory -Path $LOGS_DIR -Force | Out-Null
        Write-Success "Created logs directory: $LOGS_DIR"
    }
}

# Function to display post-installation information
function Show-PostInstallInfo {
    Write-Success "UPID CLI installation completed!"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Open a new PowerShell window to refresh PATH"
    Write-Host "2. Run 'upid --help' to see available commands"
    Write-Host "3. Run 'upid auth login' to authenticate with your cluster"
    Write-Host "4. Run 'upid analyze resources' to analyze your cluster"
    Write-Host "5. Run 'upid optimize resources' to get optimization recommendations"
    Write-Host ""
    Write-Host "Documentation:" -ForegroundColor Cyan
    Write-Host "  - GitHub: https://github.com/kubilitics/upid-cli"
    Write-Host "  - Documentation: https://github.com/kubilitics/upid-cli#readme"
    Write-Host ""
    Write-Host "Configuration:" -ForegroundColor Cyan
    Write-Host "  - Config file: $env:USERPROFILE\.upid\config.yaml"
    Write-Host "  - Logs: $env:USERPROFILE\.upid\logs\"
    Write-Host ""
    Write-Host "Note:" -ForegroundColor Yellow " Make sure you have kubectl configured and access to your Kubernetes cluster"
}

# Function to cleanup
function Remove-TempFiles {
    param([string]$TempPath)
    
    if ($TempPath -and (Test-Path $TempPath)) {
        try {
            Remove-Item -Path $TempPath -Force -ErrorAction SilentlyContinue
            Write-Status "Cleaned up temporary files"
        }
        catch {
            Write-Warning "Failed to clean up temporary files: $($_.Exception.Message)"
        }
    }
}

# Main installation function
function Main {
    Write-Header
    
    # Show help if requested
    if ($Help) {
        Show-Help
        return
    }
    
    # Run installation steps
    $SYSTEM_INFO = Detect-System
    Test-Dependencies
    $LATEST_VERSION = Get-LatestVersion
    
    # Download and install
    $TEMP_PATH = ""
    $BINARY_PATH = Download-Binary $LATEST_VERSION $SYSTEM_INFO.OS $SYSTEM_INFO.ARCH
    $TEMP_PATH = Split-Path $BINARY_PATH -Parent
    
    $INSTALL_PATH = Install-Binary $BINARY_PATH $InstallDir
    Add-ToPath $InstallDir
    Setup-Config
    
    if (!$SkipVerify) {
        Test-Installation $INSTALL_PATH
    }
    
    Remove-TempFiles $TEMP_PATH
    Show-PostInstallInfo
}

# Run main function
try {
    Main
}
catch {
    Write-Error "Installation failed: $($_.Exception.Message)"
    Remove-TempFiles $TEMP_PATH
    exit 1
} 