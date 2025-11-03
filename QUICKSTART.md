# Quick Start Guide

Get started with AWS InfoBlox VPC Management Scripts in 5 minutes!

## 📋 Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] Git installed
- [ ] Access to InfoBlox Grid Master
- [ ] InfoBlox credentials (username/password)
- [ ] AWS VPC data exported to CSV
- [ ] Terminal/command line access

## 🚀 5-Minute Quick Start

### Step 1: Clone the Repository (30 seconds)

```bash
git clone https://github.com/tshoush/aws-infoblox-vpc-scripts.git
cd aws-infoblox-vpc-scripts
```

### Step 2: Run Setup Script (2 minutes)

We recommend starting with the **v1** script (most recent, best for automation):

```bash
cd setup
./setup_v1.sh
```

**What the setup script does:**
- Prompts for your Python path (just press Enter for default)
- Creates a virtual environment
- Installs all dependencies
- Shows you next steps

**Expected output:**
```
==========================================
AWS InfoBlox VPC Manager Setup
==========================================

Enter the path to your Python executable (default: python3):
✅ Found Python 3.11.5
...
✅ Setup completed successfully!
```

### Step 3: Configure Your Credentials (1 minute)

```bash
# Go back to the main directory
cd ..

# Copy the template
cp config.env.template config.env

# Edit with your credentials
nano config.env
# OR
vim config.env
# OR open in your favorite editor
```

**Edit these values:**
```env
GRID_MASTER=your-infoblox-server.com
NETWORK_VIEW=default
INFOBLOX_USERNAME=your-username
PASSWORD=your-password
CSV_FILE=vpc_data.csv
```

**Save and close** the file.

### Step 4: Prepare Your CSV File (1 minute)

Your CSV file should contain AWS VPC data with these columns:

```csv
VpcId,CidrBlock,State,Tags,Region,IsDefault
vpc-12345,10.0.0.0/16,available,"{""Name"": ""Production VPC""}",us-east-1,False
vpc-67890,10.1.0.0/16,available,"{""Name"": ""Development VPC""}",us-west-2,False
```

**Place your CSV file** in the repository directory (or specify path in config.env).

### Step 5: Test Run (30 seconds)

```bash
# Activate the virtual environment
source venv/bin/activate

# Run in dry-run mode (safe - no changes made)
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run
```

**What you should see:**
```
🔗 Connecting to InfoBlox Grid Master: your-infoblox-server.com
🔗 InfoBlox client initialized, proceeding with operations...

📊 ANALYSIS SUMMARY:
   📁 CSV file: vpc_data.csv
   🔢 Total VPCs loaded: 10
   🌐 Network view: default

🔍 COMPARISON RESULTS:
   ✅ Matching networks: 5
   🔴 Missing networks: 5
   ⚠️ Mismatches: 0

[DRY-RUN] Would create network: 10.2.0.0/16
[DRY-RUN] Would create network: 10.3.0.0/16
...
```

**🎉 Congratulations!** If you see output like above, everything is working!

## 🎯 Next Steps

### Option A: Create Missing Networks

Once you've verified the dry-run output:

```bash
python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing
```

This will **actually create** the missing networks in InfoBlox.

### Option B: Run in Silent Mode (for automation)

```bash
python aws_infoblox_vpc_manager_complete_v1.py --silent --create-missing
```

Minimal output - perfect for cron jobs or scripts.

### Option C: Use Interactive Mode (v2 script)

```bash
python aws_infoblox_vpc_manager_complete_v2.py -i --create-missing
```

Interactive prompts guide you through the process.

## 📖 Common Commands

### View Help
```bash
python aws_infoblox_vpc_manager_complete_v1.py --help
```

### Use Different CSV File
```bash
python aws_infoblox_vpc_manager_complete_v1.py -q --csv-file my_vpcs.csv --dry-run
```

### Specify Network View
```bash
python aws_infoblox_vpc_manager_complete_v1.py -q --network-view "AWS_Production" --dry-run
```

### Check Logs
```bash
cat aws_infoblox_vpc_manager.log
# OR
tail -f aws_infoblox_vpc_manager.log  # Follow in real-time
```

## 🔧 Troubleshooting

### Problem: "Python executable not found"

**Solution:**
```bash
# Find your Python installation
which python3

# Use the full path in setup script
/usr/local/bin/python3 -m venv venv
```

### Problem: "Connection refused" or "Cannot connect to InfoBlox"

**Solution:**
1. Verify InfoBlox server address in config.env
2. Test connectivity: `ping your-infoblox-server.com`
3. Verify port 443 is accessible
4. Check credentials are correct

### Problem: "Permission denied" when running setup

**Solution:**
```bash
chmod +x setup/setup_v1.sh
./setup/setup_v1.sh
```

### Problem: "Module not found" errors

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r setup/requirements_v1.txt
```

### Problem: CSV parsing errors

**Solution:**
1. Check CSV file format matches expected structure
2. Ensure Tags column uses proper JSON format with double quotes
3. Verify no special characters in CSV

**Valid format:**
```csv
vpc-123,10.0.0.0/16,available,"{""Name"": ""VPC""}",us-east-1,False
```

**Invalid format:**
```csv
vpc-123,10.0.0.0/16,available,{'Name': 'VPC'},us-east-1,False  ❌
```

## 📚 Learn More

### Understanding the Scripts

| Script | Best For | Key Feature |
|--------|----------|-------------|
| v1 (recommended) | Automation, CI/CD | Explicit `-q` flag |
| v2 | Manual ops, Interactive | Quiet by default |
| working | Simple tasks | Basic functionality |
| prop_enhanced | Advanced needs | Overlap detection |

**See [SCRIPTS_COMPARISON.md](./SCRIPTS_COMPARISON.md)** for detailed comparison.

### Understand the Architecture

**See [ARCHITECTURE.md](./ARCHITECTURE.md)** for:
- System architecture diagrams
- Data flow explanations
- Component details
- Integration patterns

### Read Full Documentation

**See [README.md](./README.md)** for:
- Complete feature list
- All command-line options
- Configuration details
- Advanced usage patterns

## 🔄 Daily Workflow

### 1. Morning Check (Dry-Run)
```bash
cd aws-infoblox-vpc-scripts
source venv/bin/activate
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run > daily_check.log
```

### 2. Review Output
```bash
grep "Missing networks" daily_check.log
grep "ERROR" daily_check.log
```

### 3. Sync if Needed
```bash
python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing
```

### 4. Verify
```bash
# Check the log for success
tail -50 aws_infoblox_vpc_manager.log
```

## 🤖 Automation Setup

### Schedule with Cron

```bash
# Edit crontab
crontab -e

# Add this line for daily sync at 2 AM
0 2 * * * cd /path/to/aws-infoblox-vpc-scripts && source venv/bin/activate && python aws_infoblox_vpc_manager_complete_v1.py --silent --create-missing >> /var/log/infoblox-sync.log 2>&1
```

### Schedule with systemd Timer

Create `/etc/systemd/system/infoblox-sync.service`:
```ini
[Unit]
Description=InfoBlox VPC Sync Service

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/path/to/aws-infoblox-vpc-scripts
ExecStart=/path/to/aws-infoblox-vpc-scripts/venv/bin/python aws_infoblox_vpc_manager_complete_v1.py --silent --create-missing
```

Create `/etc/systemd/system/infoblox-sync.timer`:
```ini
[Unit]
Description=InfoBlox VPC Sync Timer

[Timer]
OnCalendar=daily
OnCalendar=02:00

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable infoblox-sync.timer
sudo systemctl start infoblox-sync.timer
```

## 💡 Tips and Tricks

### 1. Always Test First
```bash
# ALWAYS use --dry-run first!
python script.py --dry-run
# Only then run for real
python script.py --create-missing
```

### 2. Use Descriptive CSV Filenames
```bash
vpc_data_2025-11-02.csv  # Good - includes date
vpc_data.csv             # OK - generic
data.csv                 # Bad - too generic
```

### 3. Keep Backups
```bash
# Before major sync
cp config.env config.env.backup
cp vpc_data.csv vpc_data_backup_$(date +%Y%m%d).csv
```

### 4. Monitor Logs
```bash
# Watch logs in real-time
tail -f aws_infoblox_vpc_manager.log | grep -i error
```

### 5. Use Environment-Specific Configs
```bash
# Development
python script.py --network-view "dev" --dry-run

# Production
python script.py --network-view "prod" --create-missing
```

## 🎓 Examples

### Example 1: First-Time Setup (Full Walkthrough)

```bash
# 1. Clone
git clone https://github.com/tshoush/aws-infoblox-vpc-scripts.git
cd aws-infoblox-vpc-scripts

# 2. Setup
cd setup && ./setup_v1.sh && cd ..

# 3. Configure
cp config.env.template config.env
nano config.env  # Edit credentials

# 4. Test
source venv/bin/activate
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run

# 5. Execute
python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing

# 6. Verify
grep "SUCCESS" aws_infoblox_vpc_manager.log
```

### Example 2: Update Existing Networks

```bash
# Get latest VPC data
# (export from AWS to csv)

# Dry run to see what changed
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run

# Review output
less aws_infoblox_vpc_manager.log

# Apply changes
python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing
```

### Example 3: Multi-Region Sync

```bash
# Process each region separately
for region in us-east-1 us-west-2 eu-west-1; do
    echo "Processing $region..."
    python aws_infoblox_vpc_manager_complete_v1.py \
        --csv-file "vpc_data_${region}.csv" \
        --network-view "AWS_${region}" \
        --create-missing
done
```

### Example 4: Testing with Sample Data

```bash
# Create small test dataset
head -5 vpc_data.csv > vpc_test.csv

# Test with sample
python aws_infoblox_vpc_manager_complete_v1.py \
    --csv-file vpc_test.csv \
    --dry-run

# If successful, run on full dataset
python aws_infoblox_vpc_manager_complete_v1.py \
    --csv-file vpc_data.csv \
    --dry-run
```

## ✅ Success Criteria

You've successfully set up the scripts when:

- [ ] Setup script completes without errors
- [ ] Virtual environment activates successfully
- [ ] Config file contains your credentials
- [ ] Dry-run completes and shows your VPCs
- [ ] No connection errors to InfoBlox
- [ ] Log file is created and populated

## 🆘 Getting Help

1. **Check the logs**: `cat aws_infoblox_vpc_manager.log`
2. **Run with --help**: `python script.py --help`
3. **Review documentation**:
   - [README.md](./README.md) - Full documentation
   - [ARCHITECTURE.md](./ARCHITECTURE.md) - Technical details
   - [SCRIPTS_COMPARISON.md](./SCRIPTS_COMPARISON.md) - Feature comparison
4. **Open an issue**: [GitHub Issues](https://github.com/tshoush/aws-infoblox-vpc-scripts/issues)

## 🎉 You're Ready!

You now have a working AWS InfoBlox VPC synchronization setup!

**Next recommended reading:**
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Understand how it works
- [SCRIPTS_COMPARISON.md](./SCRIPTS_COMPARISON.md) - Choose the right script
- [README.md](./README.md) - Explore advanced features

---

**Happy Syncing! 🚀**

*Last Updated: 2025-11-02*
