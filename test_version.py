#!/usr/bin/env python3
"""Test script for version flag"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from upid.cli import cli
import click

def test_version():
    """Test the version flag"""
    try:
        # Create a context and invoke with --version
        ctx = click.Context(cli)
        result = ctx.invoke(cli, ['--version'])
        print("Version test passed")
        return True
    except Exception as e:
        print(f"Version test failed: {e}")
        return False

if __name__ == '__main__':
    test_version() 