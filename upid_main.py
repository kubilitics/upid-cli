#!/usr/bin/env python3
"""
Standalone entry point for UPID CLI
This file is used by PyInstaller to create the binary
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the CLI module
from upid.cli import main

if __name__ == "__main__":
    main() 