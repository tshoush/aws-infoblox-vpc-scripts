# Quick Start Guide

Get started with AWS InfoBlox VPC Management Scripts in 5 minutes!

## 📋 Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] Git installed and authenticated (with SSH key setup if using private repos)
- [ ] SSH key in `~/.ssh` (for SSH-based CSV sources)
- [ ] Access to InfoBlox Grid Master
- [ ] InfoBlox credentials (username/password)
- [ ] AWS VPC data in CSV format (or access to a GitHub repo that holds it)
- [ ] [GitHub CLI (`gh`)](https://cli.github.com/) installed (optional, only needed for GitHub HTTPS API URLs)

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

# Optional: fetch vpc_data.csv automatically from a remote source
# SSH URL (uses keys from ~/.ssh - recommended for private repos)
CSV_SOURCE_URL=git@github.com:owner/private-repo.git

# OR HTTPS URL (for public repos or with GitHub token)
# CSV_SOURCE_URL=https://raw.githubusercontent.com/owner/repo/main/vpc_data.csv
# CSV_SOURCE_TOKEN=ghp_xxxxxxxxxxxxx  # Only needed if repo is private
```

**Important notes:**
- The config key is `USERNAME`, not `INFOBLOX_USERNAME`
- For SSH URLs, ensure your SSH key is registered: `ssh-add ~/.ssh/your-key`
- For GitHub HTTPS URLs, the script automatically uses `gh auth token` if available
- If `CSV_SOURCE_URL` is not set, the script looks for a local `vpc_data.csv` file

### Step 4: Test Run

```bash
source venv/bin/activate
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run
```

**Expected output (with SSH CSV source):**

```
🤖 Running in non-interactive mode - reading configuration from file...
✅ All configuration loaded from config.env

📥 Fetching CSV from: git@github.com:owner/private-repo.git
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

## 📥 Remote CSV Source Setup

### SSH-based Private Repos (Recommended)

For private GitHub repos using SSH:

```bash
# 1. Add your SSH key to the agent
ssh-add ~/.ssh/your-github-key

# 2. Set in config.env
CSV_SOURCE_URL=git@github.com:owner/private-repo.git

# 3. Script fetches on each run
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run
```

### HTTPS-based Public Repos

```bash
# Public repo - no token needed
CSV_SOURCE_URL=https://raw.githubusercontent.com/owner/repo/main/vpc_data.csv

# Private repo - with token
CSV_SOURCE_URL=https://api.github.com/repos/owner/repo/contents/vpc_data.csv
CSV_SOURCE_TOKEN=ghp_your_github_token
```

### Update Strategy

To update the data:
1. Push a new `vpc_data.csv` to your remote repo
2. The next script run automatically fetches the latest version
3. Comment out `CSV_SOURCE_URL` to use a local CSV instead

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

### SSH: "Permission denied (publickey)"
Your SSH key isn't registered. Add it to the SSH agent:
```bash
ssh-add ~/.ssh/your-github-key
ssh-add -l  # Verify it's registered
```

### SSH: "No CSV file found in SSH repository"
The script clones the repo but couldn't find a CSV file. Ensure `vpc_data.csv` exists in the root of your repo.

### HTTPS: "Failed to fetch CSV from remote source: 404"
- For public HTTPS URLs: Verify the URL is correct
- For GitHub API URLs: Ensure the repo is public or add `CSV_SOURCE_TOKEN=ghp_...`
- For GitHub HTTPS: Run `gh auth login` if using HTTPS API endpoint

### "No such file or directory: 'vpc_data.csv'"
Either set `CSV_SOURCE_URL` in `config.env` to fetch it automatically, or copy the CSV to the working directory manually.

### "Connection refused" or cannot connect to InfoBlox
Verify `GRID_MASTER` is reachable: `ping 192.168.1.224`. SSL verification is disabled by default for InfoBlox (common for internal servers).

### "Module not found" errors
The setup script should have installed dependencies, but if needed:
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

## 🚀 Deploying to Another System

To move this project to a new system, you only need:

```bash
# 1. Clone the repo
git clone https://github.com/tshoush/aws-infoblox-vpc-scripts.git
cd aws-infoblox-vpc-scripts

# 2. Run setup (creates venv and installs dependencies automatically)
cd setup && ./setup_v1.sh && cd ..

# 3. Configure
cp config.env.template config.env
# Edit config.env with your InfoBlox credentials and CSV source

# 4. Set up SSH key if using SSH-based CSV source
ssh-add ~/.ssh/your-github-key

# 5. Test
source venv/bin/activate
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run
```

**That's it!** The `setup_v1.sh` script handles everything:
- Creates Python virtual environment (`venv/`)
- Runs `pip install -r setup/requirements_v1.txt`
- Creates `config.env` if missing

No need to manually run `pip install` — it's done by the setup script.

## 🔄 Daily Workflow

```bash
cd aws-infoblox-vpc-scripts
source venv/bin/activate

# 1. Dry-run to see what's changed (also downloads latest CSV)
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

**Last Updated**: 2026-02-23
