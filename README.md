# AWS InfoBlox VPC Management Scripts

A collection of Python scripts for synchronizing AWS VPC data with InfoBlox IPAM systems. These scripts support automated and interactive modes, with dry-run capabilities for safe testing.

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[QUICKSTART.md](./QUICKSTART.md)** | ⚡ **Start here!** Get up and running in 5 minutes |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | 🏗️ System architecture, data flow, and technical details |
| **[SCRIPTS_COMPARISON.md](./SCRIPTS_COMPARISON.md)** | 📊 Detailed feature comparison of all scripts |
| **[README.md](./README.md)** | 📖 This file - comprehensive documentation |

**👉 New users:** Start with [QUICKSTART.md](./QUICKSTART.md) for the fastest path to success!

## 📋 Overview

This repository contains 7 Python scripts for managing AWS VPC data imports to InfoBlox:

1. **aws_infoblox_vpc_manager_complete_v1.py** ⭐ **RECOMMENDED**
   - Most recent version (2025-08-24)
   - Explicit `-q/--quiet` flag for automation
   - Additional modes: `--silent`, `--no-interactive`, `--batch`
   - Full feature set with network overlap detection

2. **aws_infoblox_vpc_manager_complete_v2.py**
   - Quiet by default (use `-i` for interactive)
   - Complete feature set
   - Alternative version with different quiet mode approach

3. **aws_infoblox_vpc_manager_working.py**
   - Stable working version
   - Basic functionality with dry-run support

4. **prop_infoblox_import_enhanced.py**
   - Enhanced with network overlap detection
   - Automatic container creation for larger networks
   - Hierarchical network creation support

5. **prop_infoblox_import_enhanced_complete.py**
   - Most complete enhanced version
   - All overlap detection features
   - Comprehensive reporting

6. **prop_infoblox_import.py**
   - Full-featured properties import
   - Extended attributes support
   - CSV-based import

7. **prop_infoblox_import_complete.py**
   - Complete properties import version
   - Priority-based network creation
   - Configurable container detection

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Access to InfoBlox Grid Master
- AWS VPC data in CSV format

### Installation

Each script has its own setup script in the `setup/` directory:

```bash
# For the recommended script (v1)
cd setup
./setup_v1.sh

# For other scripts, use their respective setup scripts:
# ./setup_prop_import_enhanced.sh
# ./setup_aws_vpc_manager_complete.sh
# etc.
```

The setup script will:
1. Prompt for your Python path (default: python3)
2. Verify Python 3.8+ is installed
3. Create a virtual environment
4. Install all dependencies
5. Display usage instructions

### Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r setup/requirements_v1.txt
```

## 📖 Usage

### Configuration

Create a `config.env` file with your InfoBlox credentials:

```env
GRID_MASTER=your-infoblox-server.com
NETWORK_VIEW=default
INFOBLOX_USERNAME=your-username
PASSWORD=your-password
CSV_FILE=vpc_data.csv
```

### Running Scripts

#### Recommended Script (v1) - Best for Automation

```bash
# Activate virtual environment
source venv/bin/activate

# Quiet mode with dry-run (safe testing)
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run

# Silent mode (minimal output)
python aws_infoblox_vpc_manager_complete_v1.py --silent --dry-run

# Create missing networks (after testing)
python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing

# Non-interactive batch mode
python aws_infoblox_vpc_manager_complete_v1.py --batch --create-missing
```

#### Scripts with Default Quiet Mode (v2 and prop_* scripts)

```bash
# Default quiet mode (no prompts)
python aws_infoblox_vpc_manager_complete_v2.py --dry-run

# Interactive mode (with prompts)
python aws_infoblox_vpc_manager_complete_v2.py -i --create-missing
```

#### Working Version (Basic)

```bash
# Simple dry-run
python aws_infoblox_vpc_manager_working.py --dry-run
```

## 🎯 Features by Script

| Script | --dry-run | -q/--quiet | -i/--interactive | Best For |
|--------|-----------|------------|------------------|----------|
| v1 (RECOMMENDED) | ✅ | ✅ Explicit | ❌ | Automation, CI/CD |
| v2 | ✅ | ✅ Default | ✅ | Automation, Interactive |
| working | ✅ | ❌ | ❌ | Simple operations |
| prop_enhanced | ✅ | ✅ Default | ✅ | Network overlap detection |
| prop_enhanced_complete | ✅ | ✅ Default | ✅ | Full overlap features |
| prop_import | ✅ | ✅ Default | ✅ | Properties import |
| prop_complete | ✅ | ✅ Default | ✅ | Complete properties |

## 📊 Detailed Comparison

See [SCRIPTS_COMPARISON.md](./SCRIPTS_COMPARISON.md) for a detailed feature comparison table.

## 🔧 Command-Line Options

### Common Options (Most Scripts)

```
--dry-run              Simulate operations without making changes
--create-missing       Create networks that don't exist in InfoBlox
--csv-file FILE        Specify CSV file with VPC data
--network-view VIEW    Specify InfoBlox network view
```

### Script v1 Specific Options

```
-q, --quiet           Quiet mode (no prompts, read from config)
--no-interactive      Non-interactive mode (alias for quiet)
--batch               Batch processing mode (alias for quiet)
--silent              Silent mode (minimal output, implies --no-interactive)
```

### Scripts v2 and prop_* Specific Options

```
-i, --interactive     Interactive mode (enables prompts)
                      Note: These scripts are quiet by default
```

## 📁 Repository Structure

```
aws-infoblox-vpc-scripts/
├── README.md                                    # This file
├── SCRIPTS_COMPARISON.md                        # Detailed comparison table
├── aws_infoblox_vpc_manager_complete_v1.py     # ⭐ Recommended script
├── aws_infoblox_vpc_manager_complete_v2.py     # Alternative version
├── aws_infoblox_vpc_manager_working.py         # Basic version
├── prop_infoblox_import_enhanced.py            # Enhanced with overlap detection
├── prop_infoblox_import_enhanced_complete.py   # Complete enhanced version
├── prop_infoblox_import.py                     # Properties import
├── prop_infoblox_import_complete.py            # Complete properties version
└── setup/                                       # Setup scripts and requirements
    ├── setup_v1.sh                             # Setup for v1 (recommended)
    ├── setup_aws_vpc_manager_complete.sh       # Setup for v2
    ├── setup_aws_vpc_manager_working.sh        # Setup for working version
    ├── setup_prop_import_enhanced.sh           # Setup for enhanced import
    ├── setup_prop_import_enhanced_complete.sh  # Setup for complete enhanced
    ├── setup_prop_import.sh                    # Setup for prop import
    ├── setup_prop_import_complete.sh           # Setup for complete prop
    ├── requirements_v1.txt                     # Dependencies for v1
    ├── requirements_aws_complete.txt           # Dependencies for v2
    ├── requirements_aws_working.txt            # Dependencies for working
    ├── requirements_prop_enhanced.txt          # Dependencies for enhanced
    ├── requirements_prop_enhanced_complete.txt # Dependencies for complete enhanced
    ├── requirements_prop.txt                   # Dependencies for prop import
    └── requirements_prop_complete.txt          # Dependencies for complete prop
```

## 🔒 Security Notes

- **Always test with --dry-run first** before making actual changes
- Store credentials in `config.env` (add to `.gitignore`)
- Never commit credentials to version control
- Use environment variables in production environments

## 🤝 Contributing

This is a collection of working scripts. Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## 📝 License

[Add your license here]

## 📞 Support

For questions or issues:
- Check [SCRIPTS_COMPARISON.md](./SCRIPTS_COMPARISON.md) for detailed documentation
- Review the help text: `python [script].py --help`
- Open an issue in this repository

## 🎯 Recommended Workflow

1. **Setup**: Run the appropriate setup script
   ```bash
   cd setup && ./setup_v1.sh
   ```

2. **Configure**: Create your `config.env` file
   ```bash
   cp config.env.template config.env
   nano config.env
   ```

3. **Test**: Always start with dry-run
   ```bash
   source venv/bin/activate
   python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run
   ```

4. **Execute**: Run for real after verifying dry-run output
   ```bash
   python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing
   ```

5. **Automate**: Use in cron jobs or CI/CD pipelines
   ```bash
   # Example cron job (daily at 2 AM)
   0 2 * * * cd /path/to/scripts && source venv/bin/activate && python aws_infoblox_vpc_manager_complete_v1.py --silent --create-missing
   ```

## 📈 Version History

- **v1** (2025-08-24): Most recent, recommended for automation
- **v2** (2025-07-19): Alternative with quiet-by-default approach
- **working** (2025-07-19): Stable basic version
- **prop_*** (2025-07-19): Various property import versions with different feature sets

---

**Last Updated**: 2025-11-02
