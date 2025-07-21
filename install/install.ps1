# UPID CLI Installation Script for Windows
# Version: 2.0.0
# Platform: Windows

param(
    [switch]$Help,
    [switch]$Version,
    [switch]$Uninstall,
    [string]$InstallDir = "$env:ProgramFiles\UPID"
)

# Configuration
$RepoUrl = "https://github.com/your-org/upid-cli"
$Version = "v2.0.0"
$ConfigDir = "$env:USERPROFILE\.upid"

# Function to write colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to print banner
function Show-Banner {
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║                    UPID CLI v2.0.0                          ║" -ForegroundColor Blue
    Write-Host "║              Kubernetes Intelligence Platform                 ║" -ForegroundColor Blue
    Write-Host "║                                                              ║" -ForegroundColor Blue
    Write-Host "║  Production Ready • Enterprise Security • ML-Powered        ║" -ForegroundColor Blue
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
}

# Function to detect Windows architecture
function Get-WindowsArchitecture {
    if ([Environment]::Is64BitOperatingSystem) {
        return "x86_64"
    } else {
        return "x86"
    }
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    # Check if kubectl is available
    try {
        $kubectlVersion = kubectl version --client --short 2>$null
        if ($kubectlVersion) {
            Write-Status "kubectl found: $kubectlVersion"
        } else {
            Write-Warning "kubectl not found. Please install kubectl first:"
            Write-Host "  https://kubernetes.io/docs/tasks/tools/install-kubectl/"
        }
    } catch {
        Write-Warning "kubectl not found. Please install kubectl first:"
        Write-Host "  https://kubernetes.io/docs/tasks/tools/install-kubectl/"
    }
    
    # Check if Python is available (for optional features)
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            Write-Status "Python found: $pythonVersion"
        } else {
            Write-Warning "Python not found. Some features may be limited."
        }
    } catch {
        Write-Warning "Python not found. Some features may be limited."
    }
}

# Function to download binary
function Download-Binary {
    param([string]$Platform)
    
    $BinaryName = "upid-$Platform.exe"
    $DownloadUrl = "$RepoUrl/releases/download/$Version/$BinaryName"
    
    Write-Status "Downloading UPID CLI binary for $Platform..."
    
    # Create temporary directory
    $TempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
    
    try {
        # Download binary
        $BinaryPath = Join-Path $TempDir $BinaryName
        Invoke-WebRequest -Uri $DownloadUrl -OutFile $BinaryPath
        
        # Verify download
        if (Test-Path $BinaryPath) {
            Write-Status "Binary downloaded successfully"
            
            # Create installation directory
            if (!(Test-Path $InstallDir)) {
                New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
            }
            
            # Install binary
            $InstallPath = Join-Path $InstallDir "upid.exe"
            Copy-Item $BinaryPath $InstallPath -Force
            
            # Add to PATH if not already there
            $CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
            if ($CurrentPath -notlike "*$InstallDir*") {
                $NewPath = "$CurrentPath;$InstallDir"
                [Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
                Write-Status "Added UPID CLI to PATH"
            }
            
            Write-Status "Binary installed to $InstallPath"
        } else {
            throw "Failed to download binary"
        }
    } catch {
        Write-Error "Failed to download binary: $($_.Exception.Message)"
        throw
    } finally {
        # Clean up
        if (Test-Path $TempDir) {
            Remove-Item $TempDir -Recurse -Force
        }
    }
}

# Function to setup configuration
function Setup-Configuration {
    Write-Status "Setting up configuration..."
    
    if (!(Test-Path $ConfigDir)) {
        New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
    }
    
    # Create default config if it doesn't exist
    $ConfigFile = Join-Path $ConfigDir "config.yaml"
    if (!(Test-Path $ConfigFile)) {
        $ConfigContent = @"
# UPID CLI Configuration
auth:
  default_provider: "local"
  mfa_required: false

storage:
  database_path: "$ConfigDir\upid_data.db"
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
"@
        $ConfigContent | Out-File -FilePath $ConfigFile -Encoding UTF8
        Write-Status "Configuration file created: $ConfigFile"
    }
}

# Function to initialize UPID CLI
function Initialize-UPID {
    Write-Status "Initializing UPID CLI..."
    
    # Check if binary is in PATH
    try {
        $upidPath = Get-Command upid -ErrorAction SilentlyContinue
        if ($upidPath) {
            # Initialize with default settings
            upid init --yes 2>$null
            Write-Status "UPID CLI initialized successfully"
        } else {
            Write-Warning "UPID CLI binary not found in PATH. Please restart your terminal or add $InstallDir to your PATH"
        }
    } catch {
        Write-Warning "Could not initialize UPID CLI: $($_.Exception.Message)"
    }
}

# Function to verify installation
function Test-Installation {
    Write-Status "Verifying installation..."
    
    try {
        $upidPath = Get-Command upid -ErrorAction SilentlyContinue
        if ($upidPath) {
            $version = upid --version 2>$null
            if ($version) {
                Write-Status "UPID CLI installed successfully: $version"
            } else {
                Write-Status "UPID CLI installed successfully"
            }
            
            # Test basic functionality
            $helpOutput = upid --help 2>$null
            if ($helpOutput) {
                Write-Status "Basic functionality test passed"
            } else {
                Write-Warning "Basic functionality test failed"
            }
        } else {
            Write-Error "UPID CLI not found in PATH"
            Write-Status "Please add $InstallDir to your PATH or restart your terminal"
        }
    } catch {
        Write-Error "Installation verification failed: $($_.Exception.Message)"
    }
}

# Function to print next steps
function Show-NextSteps {
    Write-Host ""
    Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host "Installation Complete!" -ForegroundColor Green
    Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Restart your terminal or run: refreshenv"
    Write-Host "2. Authenticate with UPID CLI:"
    Write-Host "   upid auth login"
    Write-Host "3. Analyze your cluster:"
    Write-Host "   upid analyze cluster"
    Write-Host "4. View the dashboard:"
    Write-Host "   upid dashboard"
    Write-Host ""
    Write-Host "Documentation:"
    Write-Host "- User Manual: https://docs.upid.io/user-manual"
    Write-Host "- Quick Reference: https://docs.upid.io/quick-reference"
    Write-Host "- Installation Guide: https://docs.upid.io/installation"
    Write-Host ""
    Write-Host "Support:"
    Write-Host "- GitHub Issues: https://github.com/your-org/upid-cli/issues"
    Write-Host "- Community: https://community.upid.io"
    Write-Host "- Email: support@upid.io"
    Write-Host ""
}

# Function to uninstall UPID CLI
function Uninstall-UPID {
    Write-Status "Uninstalling UPID CLI..."
    
    # Remove binary
    $BinaryPath = Join-Path $InstallDir "upid.exe"
    if (Test-Path $BinaryPath) {
        Remove-Item $BinaryPath -Force
        Write-Status "Removed binary: $BinaryPath"
    }
    
    # Remove from PATH
    $CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    $NewPath = ($CurrentPath -split ';' | Where-Object { $_ -ne $InstallDir }) -join ';'
    [Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
    Write-Status "Removed from PATH"
    
    # Remove configuration
    if (Test-Path $ConfigDir) {
        Remove-Item $ConfigDir -Recurse -Force
        Write-Status "Removed configuration directory: $ConfigDir"
    }
    
    Write-Status "UPID CLI uninstalled successfully"
}

# Main installation function
function Install-UPID {
    Show-Banner
    
    # Check if running as administrator
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (!$isAdmin) {
        Write-Warning "Running without administrator privileges. Some features may be limited."
    }
    
    # Detect platform
    $architecture = Get-WindowsArchitecture
    $platform = "windows-$architecture"
    Write-Status "Detected platform: $platform"
    
    # Check prerequisites
    Test-Prerequisites
    
    # Download and install binary
    Download-Binary $platform
    
    # Setup configuration
    Setup-Configuration
    
    # Initialize UPID CLI
    Initialize-UPID
    
    # Verify installation
    Test-Installation
    
    # Print next steps
    Show-NextSteps
}

# Handle command line arguments
if ($Help) {
    Write-Host "UPID CLI Installation Script for Windows"
    Write-Host "Usage: .\install.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Help        Show this help message"
    Write-Host "  -Version     Show version information"
    Write-Host "  -Uninstall   Remove UPID CLI"
    Write-Host "  -InstallDir  Installation directory (default: ProgramFiles\UPID)"
    exit 0
}

if ($Version) {
    Write-Host "UPID CLI Installation Script v2.0.0"
    exit 0
}

if ($Uninstall) {
    Uninstall-UPID
    exit 0
}

# Run main installation
try {
    Install-UPID
} catch {
    Write-Error "Installation failed: $($_.Exception.Message)"
    exit 1
} 