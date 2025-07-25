#!/bin/bash
# UPID CLI Runtime Installer
# Installs UPID CLI with embedded Python runtime

set -e

INSTALL_DIR="/opt/upid"
BIN_DIR="/usr/local/bin"
RUNTIME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Installing UPID CLI with Python runtime..."

# Create installation directory
sudo mkdir -p "$INSTALL_DIR"

# Copy runtime files
echo "📦 Copying runtime files..."
sudo cp -r "$RUNTIME_DIR"/* "$INSTALL_DIR/"

# Create executable wrapper
echo "🔧 Creating executable wrapper..."
sudo tee "$BIN_DIR/upid" > /dev/null << 'EOF'
#!/bin/bash
# UPID CLI Executable Wrapper
UPID_ROOT="/opt/upid"
cd "$UPID_ROOT" && python3 upid_runtime.py "$@"
EOF

# Make executable
sudo chmod +x "$BIN_DIR/upid"

# Verify installation
echo "✅ Verifying installation..."
if upid --help > /dev/null 2>&1; then
    echo "✅ UPID CLI installed successfully!"
    echo "📍 Installation location: $INSTALL_DIR"
    echo "🔗 Executable: $BIN_DIR/upid"
    echo ""
    echo "Quick start:"
    echo "  upid auth login"
    echo "  upid analyze cluster"
    echo "  upid --help"
else
    echo "❌ Installation verification failed"
    exit 1
fi
