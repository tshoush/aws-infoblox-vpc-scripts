# Quick Start Guide

Get started with AWS InfoBlox VPC Management Scripts in 5 minutes!

## 📋 Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] Git and [GitHub CLI (`gh`)](https://cli.github.com/) installed and authenticated
- [ ] Access to InfoBlox Grid Master
- [ ] InfoBlox credentials (username/password)
- [ ] AWS VPC data in CSV format (or access to the GitHub repo that holds it)

## 🚀 5-Minute Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/tshoush/aws-infoblox-vpc-scripts.git
cd aws-infoblox-vpc-scripts
```

### Step 2: Run Setup Script

```bash
cd setup && ./setup_v1.sh && cd ..
```

The setup script creates a virtual environment and installs all dependencies.

### Step 3: Configure

```bash
cp config.env.template config.env
```

Edit `config.env` with your values:

```env
GRID_MASTER=192.168.1.224
NETWORK_VIEW=default
USERNAME=admin
PASSWORD=your-password
CSV_FILE=vpc_data.csv

# Optional: fetch vpc_data.csv automatically from a private GitHub repo
GITHUB_REPO=tshoush/IBX-AWS_Sync
GITHUB_CSV_PATH=vpc_data.csv
```

> **Note:** The config key is `USERNAME`, not `INFOBLOX_USERNAME`.

### Step 4: Test Run

```bash
source venv/bin/activate
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run
```

**Expected output:**

```
🤖 Running in non-interactive mode - reading configuration from file...
✅ All configuration loaded from config.env

📥 Fetching vpc_data.csv from GitHub: tshoush/IBX-AWS_Sync
   ✅ Downloaded to: vpc_data.csv

🔗 Connecting to InfoBlox Grid Master: 192.168.1.224
🔗 InfoBlox client initialized, proceeding with operations...

📊 ANALYSIS SUMMARY:
   📁 CSV file: vpc_data.csv
   🔢 Total VPCs loaded: 445
   🌐 Network view: default

🔍 COMPARISON RESULTS:
   ✅ Matching networks: 61
   🔴 Missing networks: 21
   🟡 Tag discrepancies: 326
   📦 Network containers: 37
   ❌ Processing errors: 0

🏷️  EXTENDED ATTRIBUTES ANALYSIS:
   🔢 Required EAs (from CSV Tags): 42
   ✅ Already exist in InfoBlox:   39
   ❌ Missing from InfoBlox:        3

   ⚠️  MISSING EXTENDED ATTRIBUTES (must exist before import):
      - environment
      - owner
      - project

   📄 EA report written to: missing_eas_20260219_140527.txt
   📄 Missing networks written to: missing_networks_20260219_140527.csv
```

### Step 5: Review Reports

```bash
# Which EAs are missing from InfoBlox
cat missing_eas_*.txt

# Which VPC networks will be created
cat missing_networks_*.csv
```

### Step 6: Execute

Once you're satisfied with the dry-run output:

```bash
python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing
```

This will:
1. Download the latest CSV from GitHub
2. Create any missing Extended Attributes in InfoBlox
3. Create the missing networks with AWS tags mapped to EAs

## 📥 GitHub CSV Source

If `GITHUB_REPO` is set in `config.env`, the script fetches the CSV automatically at each run using your `gh` CLI credentials. To update the data, push a new `vpc_data.csv` to the GitHub repo — the next script run will pick it up.

To bypass GitHub and use a local CSV instead, comment out `GITHUB_REPO` in `config.env`.

## 📖 Common Commands

```bash
# View help
python aws_infoblox_vpc_manager_complete_v1.py --help

# Use a specific local CSV file
python aws_infoblox_vpc_manager_complete_v1.py -q --csv-file my_vpcs.csv --dry-run

# Specify network view
python aws_infoblox_vpc_manager_complete_v1.py -q --network-view "AWS_Production" --dry-run

# Follow log in real-time
tail -f aws_infoblox_vpc_manager.log
```

## 🔧 Troubleshooting

### "Missing values: USERNAME"
The config key is `USERNAME`, not `INFOBLOX_USERNAME`. Check your `config.env`.

### "Could not get GitHub token via 'gh auth token'"
Run `gh auth login` to authenticate the GitHub CLI, then retry.

### "No such file or directory: 'vpc_data.csv'"
Either set `GITHUB_REPO` in `config.env` to fetch it automatically, or copy the CSV to the working directory manually.

### "Connection refused" or cannot connect to InfoBlox
Verify `GRID_MASTER` is reachable: `ping 192.168.1.224`. SSL verification is disabled by default for InfoBlox (common for internal servers).

### "Module not found" errors
```bash
source venv/bin/activate
pip install -r setup/requirements_v1.txt
```

## 📁 Output Files

All files are written to the working directory (not a `reports/` subdirectory):

| File | Description |
|------|-------------|
| `aws_infoblox_vpc_manager.log` | Full operation log |
| `missing_eas_<timestamp>.txt` | EAs required by CSV Tags vs InfoBlox |
| `missing_networks_<timestamp>.csv` | Networks in CSV not yet in InfoBlox |
| `rejected_networks_<timestamp>.csv` | Networks skipped during creation (e.g. overlaps) |

## 🔄 Daily Workflow

```bash
cd aws-infoblox-vpc-scripts
source venv/bin/activate

# 1. Dry-run to see what's changed (also downloads latest CSV from GitHub)
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run

# 2. Review
cat missing_networks_*.csv
cat missing_eas_*.txt

# 3. Sync
python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing
```

## 🤖 Automation Setup

```bash
# crontab -e
0 2 * * * cd /path/to/aws-infoblox-vpc-scripts && source venv/bin/activate && python aws_infoblox_vpc_manager_complete_v1.py --silent --create-missing >> /var/log/infoblox-sync.log 2>&1
```

---

**Last Updated**: 2026-02-19
