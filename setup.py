#!/usr/bin/env python3
"""
Setup script for UPID CLI
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Import centralized configuration
try:
    from upid_config import get_config
    config = get_config()
    product = config.product
except ImportError:
    # Fallback values if config system not available
    class FallbackProduct:
        name = "upid-cli"
        version = "1.0.0"
        author = "UPID Team"
        author_email = "hello@kubilitics.com"
        description = "Universal Kubernetes Resource Optimization Platform - CLI Tool"
        homepage = "https://github.com/kubilitics/upid-cli"
        repository = "https://github.com/kubilitics/upid-cli"
        license = "MIT"
    product = FallbackProduct()

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
def read_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name=product.name.lower().replace(" ", "-"),
    version=product.version,
    author=product.author,
    author_email=product.author_email,
    description=product.description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=product.repository,
    project_urls={
        "Bug Reports": f"{product.repository}/issues",
        "Source": product.repository,
        "Documentation": product.documentation,
        "Homepage": product.homepage,
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
    },
    entry_points={
        "console_scripts": [
            "upid=upid.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="kubernetes,cli,optimization,resource-management,cluster-management",
    platforms=["any"],
    license=product.license,
) 