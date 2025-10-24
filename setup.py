#!/usr/bin/env python3
"""
MEGA DeFi Profit Machine - Setup Script
=======================================

This setup script enables installation of the MEGA DeFi Profit Machine package.
"""

from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mega-defi",
    version="1.0.0",
    author="FX Genius LLC",
    author_email="contact@fxgeniusllc.com",
    description="An unstoppable profit-generating system for decentralized finance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fxgeniusllc-oss/MEGA_-DEFI-",
    project_urls={
        "Bug Tracker": "https://github.com/fxgeniusllc-oss/MEGA_-DEFI-/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - pure Python implementation
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
