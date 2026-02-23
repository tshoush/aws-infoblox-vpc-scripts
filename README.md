# AWS InfoBlox VPC Management Scripts

A collection of Python scripts for synchronizing AWS VPC data with InfoBlox IPAM systems. These scripts support automated and interactive modes, with dry-run capabilities for safe testing.

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[QUICKSTART.md](./QUICKSTART.md)** | ⚡ **Start here!** Get up and running in 5 minutes |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | 🏗️ System architecture, data flow, and technical details |
| **[SCRIPTS_COMPARISON.md](./SCRIPTS_COMPARISON.md)** | 📊 Detailed feature comparison of all scripts |

## 📋 Overview

This repository contains 7 Python scripts for managing AWS VPC data imports to InfoBlox:

1. **aws_infoblox_vpc_manager_complete_v1.py** ⭐ **RECOMMENDED**
   - Explicit `-q/--quiet` flag for automation
   - GitHub CSV fetch: downloads `vpc_data.csv` from a configured private repo at startup
   - EA analysis on every run with file reports for missing attributes and networks
   - Additional modes: `--silent`, `--no-interactive`, `--batch`

2. **aws_infoblox_vpc_manager_complete_v2.py**
   - Quiet by default (use `-i` for interactive)
   - Complete feature set

3. **aws_infoblox_vpc_manager_working.py**
   - Stable working version with basic dry-run support

4. **prop_infoblox_import_enhanced.py** — Enhanced with network overlap detection
5. **prop_infoblox_import_enhanced_complete.py** — Complete overlap detection and reporting
6. **prop_infoblox_import.py** — Full-featured properties import
7. **prop_infoblox_import_complete.py** — Priority-based network creation

## 🚀 Quick Start

### Installation

```bash
cd setup && ./setup_v1.sh
```

The setup script:
1. Creates a Python virtual environment
2. Installs all dependencies (`pip install -r requirements_v1.txt`)
3. Creates `config.env` from template (if missing)

### Configuration

Copy and edit `config.env`:

```env
GRID_MASTER=your-infoblox-server.com
NETWORK_VIEW=default
USERNAME=your-username
PASSWORD=your-password
CSV_FILE=vpc_data.csv

# Optional: fetch vpc_data.csv from a remote source (SSH or HTTPS)
CSV_SOURCE_URL=git@github.com:owner/private-repo.git
# CSV_SOURCE_URL=https://raw.githubusercontent.com/owner/repo/main/vpc_data.csv
# CSV_SOURCE_TOKEN=your_github_token  # Only needed for HTTPS without gh CLI
```

### Running

```bash
source venv/bin/activate

# Test safely first
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run

# Create missing networks (after reviewing dry-run output)
python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing
```

## 📥 Remote CSV Source

The script supports downloading `vpc_data.csv` from remote sources:

### SSH URLs (Private Repos)
```env
CSV_SOURCE_URL=git@github.com:owner/private-repo.git
```
Uses SSH keys from `~/.ssh` — ensure your SSH key is in ssh-agent:
```bash
ssh-add ~/.ssh/your-key
```

### HTTPS URLs (Public or with Token)
```env
CSV_SOURCE_URL=https://raw.githubusercontent.com/owner/repo/main/vpc_data.csv
CSV_SOURCE_URL=https://api.github.com/repos/owner/repo/contents/vpc_data.csv
# GitHub API URLs automatically use 'gh auth token' if available
```

To disable temporarily, comment out `CSV_SOURCE_URL` in `config.env`.

## 🏷️ Extended Attributes Analysis

Every run (including dry-run) analyzes which InfoBlox Extended Attributes are required by the Tags in your CSV, compares against what exists in InfoBlox, and writes two report files:

- **`missing_eas_<timestamp>.txt`** — full list of required EAs with `[MISSING]` / `[exists]` status
- **`missing_networks_<timestamp>.csv`** — all missing networks with CIDR, Name, VpcId, AccountId, Region

Console output example:
```
🏷️  EXTENDED ATTRIBUTES ANALYSIS:
   🔢 Required EAs (from CSV Tags): 42
   ✅ Already exist in InfoBlox:   39
   ❌ Missing from InfoBlox:        3

   ⚠️  MISSING EXTENDED ATTRIBUTES (must exist before import):
      - environment
      - owner
      - project
```

Running `--create-missing` automatically creates missing EAs before creating networks.

## 🔧 Command-Line Options

### v1 (Recommended)

```
--dry-run              Simulate operations without changes
--create-missing       Create missing EAs and networks
--csv-file FILE        Override CSV_FILE from config
--network-view VIEW    Override NETWORK_VIEW from config
-q, --quiet            Non-interactive; read all config from config.env
--silent               Minimal output, implies --no-interactive
--batch                Alias for quiet mode
```

### v2 and prop_* scripts

```
-i, --interactive      Enable prompts (these scripts are quiet by default)
```

## 📁 Output Files

All output files are written to the working directory:

| File | Created when |
|------|-------------|
| `aws_infoblox_vpc_manager.log` | Always |
| `missing_eas_<timestamp>.txt` | Always (on every run) |
| `missing_networks_<timestamp>.csv` | When missing networks exist |
| `rejected_networks_<timestamp>.csv` | When networks are rejected during creation |

## 🎯 Recommended Workflow

1. Configure `config.env` (set `GITHUB_REPO` if using GitHub as CSV source)
2. Dry-run: `python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run`
3. Review `missing_eas_<timestamp>.txt` and `missing_networks_<timestamp>.csv`
4. Execute: `python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing`

## 🤖 Automation

### Cron Job Example

```bash
# Example cron job (daily at 2 AM)
0 2 * * * cd /path/to/scripts && source venv/bin/activate && python aws_infoblox_vpc_manager_complete_v1.py --silent --create-missing >> /var/log/infoblox-sync.log 2>&1
```

### For SSH-based CSV Sources

If using SSH URLs for `CSV_SOURCE_URL`, ensure SSH agent is available in the cron environment:

```bash
# In crontab, add SSH_AUTH_SOCK and SSH_AGENT_PID before the job
0 2 * * * export SSH_AUTH_SOCK=/tmp/ssh-agent-sock && cd /path/to/scripts && source venv/bin/activate && python aws_infoblox_vpc_manager_complete_v1.py --silent --create-missing >> /var/log/infoblox-sync.log 2>&1
```

Or use a systemd timer with the user's SSH agent socket.

---

**Last Updated**: 2026-02-23
