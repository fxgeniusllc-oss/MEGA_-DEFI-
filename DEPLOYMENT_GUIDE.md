# System Launch & Deployment Scripts

## Overview

This directory contains comprehensive deployment and system launch scripts for the MEGA DeFi Profit Machine. These scripts automate the entire setup, verification, and launch process across multiple platforms.

## Available Scripts

### 1. **system_launch.bat** (Windows)
Comprehensive deployment script for Windows systems (Windows 10+).

**Usage:**
```cmd
system_launch.bat
```

### 2. **system_launch.sh** (Linux/macOS)
Comprehensive deployment script for Unix-based systems.

**Usage:**
```bash
chmod +x system_launch.sh
./system_launch.sh
```

## What These Scripts Do

The deployment scripts perform the following operations in sequence:

### Phase 1: Pre-Flight System Checks ✈️
- Verifies Python 3.8+ installation
- Verifies Node.js 20+ installation
- Verifies npm package manager
- Checks for Rust/Cargo (optional)
- Validates Git installation
- Reports any missing dependencies

### Phase 2: Python Package Installation 🐍
- Installs the MEGA DeFi Python package in editable mode
- Verifies package installation
- Tests import functionality
- Confirms all Python modules are accessible

### Phase 3: Node.js Dependencies & TypeScript Build 📦
- Installs all Node.js dependencies via npm
- Compiles TypeScript components
- Builds production-ready JavaScript files
- Verifies build artifacts

### Phase 4: Rust Compilation (Optional) 🦀
- Compiles Rust high-performance components in release mode
- Creates optimized binaries
- Reports build status
- Gracefully skips if Rust is not available

### Phase 5: System Testing & Validation 🧪
- Runs the complete test suite (99 tests)
- Validates system integrity
- Reports test results
- Identifies any issues

### Phase 6: System Health Check ❤️
- Verifies all Python modules can be imported
- Checks TypeScript build artifacts
- Validates example scripts exist
- Confirms system readiness

### Phase 7: Example Demonstration 🎬
- Runs the basic usage example
- Demonstrates system functionality
- Shows real trading simulation
- Validates end-to-end operation

### Phase 8: Final Status & Summary 📊
- Displays comprehensive system status
- Lists all available commands
- Shows performance targets
- Provides documentation links
- Confirms operational readiness

## Terminal Output Features

The scripts provide rich, colorized terminal output with:

- ✅ **Success indicators** (green)
- ❌ **Error messages** (red)
- ⚠️ **Warnings** (yellow)
- 📊 **Progress indicators** (cyan/blue)
- 🎯 **Status updates** (magenta)
- **Detailed logging** with timestamps
- **Visual separators** for clarity
- **Component-by-component tracking**

## Output Example

```
============================================================================
    🚀 MEGA DEFI PROFIT MACHINE - SYSTEM LAUNCH UTILITY 🚀
============================================================================
    Ultimate DeFi Trading System Deployment
    Multi-Language Integration: Python + Rust + TypeScript
============================================================================

[21:47:24] Starting system initialization...

═══════════════════════════════════════════════════════════════════════════
  PHASE 1: PRE-FLIGHT SYSTEM CHECKS
═══════════════════════════════════════════════════════════════════════════

[CHECK] Verifying Python installation...
  ✅ SUCCESS: Python 3.12.3 detected

[CHECK] Verifying Node.js installation...
  ✅ SUCCESS: Node.js v20.19.5 detected

[CHECK] Verifying npm package manager...
  ✅ SUCCESS: npm 10.8.2 detected

[CHECK] Verifying Rust/Cargo installation (optional)...
  ✅ SUCCESS: Cargo 1.90.0 detected

[CHECK] Verifying Git installation...
  ✅ SUCCESS: Git 2.51.0 detected

───────────────────────────────────────────────────────────────────────────
  ✅ PRE-FLIGHT CHECK COMPLETE - ALL SYSTEMS GO!
───────────────────────────────────────────────────────────────────────────
```

## Prerequisites

Before running these scripts, ensure you have:

### Required:
- **Python 3.8+** (3.12 recommended)
- **Node.js 20+**
- **npm** (comes with Node.js)
- **Git**

### Optional (but recommended):
- **Rust/Cargo** - For high-performance components

## Installation Guides

If any prerequisites are missing:

- **Python**: https://www.python.org/downloads/
- **Node.js**: https://nodejs.org/
- **Rust**: https://rustup.rs/
- **Git**: https://git-scm.com/downloads

## Troubleshooting

### Script Fails on Pre-Flight Check
**Issue**: Missing dependencies reported in Phase 1

**Solution**: Install the missing components listed in the error messages and re-run the script.

### Python Package Installation Fails
**Issue**: pip install errors

**Solution**: 
```bash
# Try with user installation
pip install --user -e .

# Or upgrade pip first
python -m pip install --upgrade pip
```

### npm Install Fails
**Issue**: Node.js dependencies fail to install

**Solution**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and try again
rm -rf node_modules
npm install
```

### TypeScript Build Fails
**Issue**: tsc compilation errors

**Solution**:
```bash
# Reinstall TypeScript
npm install -D typescript

# Clean and rebuild
rm -rf dist
npm run build
```

### Rust Build Fails
**Issue**: Cargo compilation errors

**Solution**:
```bash
# Update Rust toolchain
rustup update

# Clean and rebuild
cargo clean
cargo build --release
```

### Tests Fail
**Issue**: Some unit tests don't pass

**Solution**:
- Review the test output for specific failures
- Ensure all dependencies are installed
- Check if it's a known issue in the repository
- The system may still work for basic functionality

## Post-Launch Commands

After successful deployment, use these commands:

### Python Examples:
```bash
python3 examples/basic_usage.py           # Basic trading demo
python3 examples/advanced_simulation.py   # Advanced simulation
```

### TypeScript Commands:
```bash
npm start                                 # Start main application
npm run simulate                          # Run opportunity detector
```

### Testing:
```bash
python3 -m unittest discover tests/ -v    # Run full test suite
```

### Build Commands:
```bash
npm run build                             # Rebuild TypeScript
cargo build --release                     # Rebuild Rust
```

## System Requirements

### Minimum:
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: 4GB
- **Disk Space**: 2GB
- **CPU**: Dual-core processor

### Recommended:
- **OS**: Windows 11, macOS 13+, or Linux (Ubuntu 22.04+)
- **RAM**: 8GB+
- **Disk Space**: 5GB+
- **CPU**: Quad-core processor or better

## Features

✅ **Automated Setup** - Complete system deployment in one command
✅ **Multi-Platform** - Works on Windows, Linux, and macOS
✅ **Error Handling** - Comprehensive error detection and reporting
✅ **Visual Feedback** - Colorized output with progress indicators
✅ **Health Checks** - Validates every component
✅ **Documentation** - Built-in help and status information
✅ **Testing** - Runs full test suite automatically
✅ **Demo Mode** - Includes example demonstration

## Performance Targets

After successful deployment:
- **500-2000% APY** with intelligent risk management
- Multi-strategy approach (Arbitrage, Sandwich, Liquidation, etc.)
- Advanced ML-powered market analysis
- Real-time profit optimization

## Documentation

For more information:
- **README.md** - System overview
- **QUICKSTART.md** - Quick start guide
- **INSTALL.md** - Installation details
- **OPERATIONAL_READINESS.md** - System capabilities
- **TESTING.md** - Testing guide

## Support

If you encounter issues:
1. Check the error messages in the script output
2. Review this README for troubleshooting steps
3. Ensure all prerequisites are installed correctly
4. Check the repository documentation
5. Open an issue on GitHub with detailed error logs

## License

MIT License - See LICENSE file for details

---

**🚀 Ready to dominate DeFi markets!**
