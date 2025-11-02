# AWS InfoBlox VPC Manager Scripts - Feature Comparison Table

| # | Script Name | Last Modified | Size | Location | --dry-run | -q/--quiet | -i/--interactive | Setup Script |
|---|-------------|---------------|------|----------|-----------|------------|------------------|--------------|
| 1 | aws_infoblox_vpc_manager_complete.py | 2025-08-24 16:55 | 44K | OldPC/...Marriot/ | ✅ YES | ✅ YES (explicit -q) | ❌ NO | setup.sh |
| 2 | prop_infoblox_import_enhanced.py | 2025-07-19 11:57 | 29K | Preso/Marriot/ | ✅ YES | ✅ YES (default) | ✅ YES | setup_prop_import_enhanced.sh |
| 3 | prop_infoblox_import_enhanced_complete.py | 2025-07-19 11:57 | 46K | Preso/Marriot/ | ✅ YES | ✅ YES (default) | ✅ YES | setup_prop_import_enhanced_complete.sh |
| 4 | prop_infoblox_import.py | 2025-07-19 11:57 | 62K | Preso/Marriot/ | ✅ YES | ✅ YES (default) | ✅ YES | setup_prop_import.sh |
| 5 | prop_infoblox_import_complete.py | 2025-07-19 11:57 | 30K | Preso/Marriot/ | ✅ YES | ✅ YES (default) | ✅ YES | setup_prop_import_complete.sh |
| 6 | aws_infoblox_vpc_manager_working.py | 2025-07-19 11:57 | 29K | Preso/Marriot/ | ✅ YES | ❌ NO | ❌ NO | setup_aws_vpc_manager_working.sh |
| 7 | aws_infoblox_vpc_manager_complete.py | 2025-07-19 11:57 | 62K | Preso/Marriot/ | ✅ YES | ✅ YES (default) | ✅ YES | setup_aws_vpc_manager_complete.sh |

## Full Paths

1. `/Users/tshoush/OldPC/excel_to_json_analysis/Marriot/aws_infoblox_vpc_manager_complete.py`
2. `/Users/tshoush/Preso/Marriot/prop_infoblox_import_enhanced.py`
3. `/Users/tshoush/Preso/Marriot/prop_infoblox_import_enhanced_complete.py`
4. `/Users/tshoush/Preso/Marriot/prop_infoblox_import.py`
5. `/Users/tshoush/Preso/Marriot/prop_infoblox_import_complete.py`
6. `/Users/tshoush/Preso/Marriot/aws_infoblox_vpc_manager_working.py`
7. `/Users/tshoush/Preso/Marriot/aws_infoblox_vpc_manager_complete.py`

## Legend

- **--dry-run**: Simulates operations without making actual changes
- **-q/--quiet**:
  - "explicit -q" = Has explicit `-q` or `--quiet` command-line flag
  - "default" = Runs in quiet mode by default (use `-i` for interactive)
- **-i/--interactive**: Enable interactive mode with prompts

## Command-Line Flags by Script

### Script #1 (OldPC - Most Recent) ⭐ RECOMMENDED
```bash
python aws_infoblox_vpc_manager_complete.py -q --dry-run
python aws_infoblox_vpc_manager_complete.py --quiet --create-missing
python aws_infoblox_vpc_manager_complete.py --no-interactive --dry-run
python aws_infoblox_vpc_manager_complete.py --batch --create-missing
python aws_infoblox_vpc_manager_complete.py --silent --dry-run
```

**Available flags:**
- `-q`, `--quiet` - Quiet mode (no prompts)
- `--no-interactive` - Non-interactive mode (alias for quiet)
- `--batch` - Batch mode (alias for quiet)
- `--silent` - Silent mode (minimal output, implies --no-interactive)
- `--dry-run` - Dry run (no changes made)
- `--create-missing` - Create missing networks
- `--csv-file <file>` - Specify CSV file
- `--network-view <view>` - Specify network view

### Scripts #2-5, #7 (Preso - Quiet by Default)
```bash
# Quiet mode (default - no prompts)
python prop_infoblox_import_enhanced.py --dry-run
python prop_infoblox_import_enhanced.py --create-missing

# Interactive mode (with prompts)
python prop_infoblox_import_enhanced.py -i --dry-run
python prop_infoblox_import_enhanced.py --interactive --create-missing
```

**Available flags:**
- `-i`, `--interactive` - Interactive mode (enable prompts)
- `--dry-run` - Dry run (no changes made)
- `--create-missing` - Create missing networks
- `--csv-file <file>` - Specify CSV file
- `--network-view <view>` - Specify network view

### Script #6 (aws_infoblox_vpc_manager_working.py)
```bash
python aws_infoblox_vpc_manager_working.py --dry-run
```

**Available flags:**
- `--dry-run` - Dry run (no changes made)

## Setup Instructions

### For Script #1 (OldPC):
```bash
cd /Users/tshoush/OldPC/excel_to_json_analysis/Marriot/
./setup.sh
source venv/bin/activate
python aws_infoblox_vpc_manager_complete.py --help
```

### For Scripts #2-7 (Preso):
```bash
cd /Users/tshoush/Preso/Marriot/
./setup_<script_name>.sh    # e.g., ./setup_prop_import_enhanced.sh
source venv_<name>/bin/activate
python <script_name>.py --help
```

## Key Differences

### Script #1 (OldPC - NEWEST) ⭐
- **Most recent**: August 24, 2025
- **Best for automation**: Explicit `-q` flag for clarity in scripts
- **Multiple automation options**: `--quiet`, `--silent`, `--no-interactive`, `--batch`
- **All features**: Complete implementation with all options
- **Explicit flags**: Clear what mode you're running in

### Scripts #2-5, #7 (Preso)
- **Quiet by default**: Automation-first design
- **Interactive mode**: Use `-i` flag when you need prompts
- **Modern approach**: Assumes non-interactive by default
- **Feature variations**: Different feature sets (enhanced, complete, etc.)

### Script #6 (aws_infoblox_vpc_manager_working.py)
- **No mode selection**: Always runs the same way
- **Simple**: Basic functionality
- **Has dry-run**: Can test safely

## Recommended Choice

**For automation and scripting: Script #1**
(`/Users/tshoush/OldPC/excel_to_json_analysis/Marriot/aws_infoblox_vpc_manager_complete.py`)

**Reasons:**
1. ✅ Most recent (August 24, 2025)
2. ✅ Explicit `-q` flag makes scripts self-documenting
3. ✅ Multiple automation modes (`--quiet`, `--silent`, `--no-interactive`, `--batch`)
4. ✅ Complete feature set
5. ✅ Clear command-line interface

## Dependencies (All Scripts)

All scripts use the same dependencies:
```txt
pandas>=2.0.0
requests>=2.31.0
urllib3>=2.0.0
python-dotenv>=1.0.0
```

Python 3.8+ required.

## Configuration

All scripts expect a `config.env` file with:
```env
GRID_MASTER=<infoblox_server>
NETWORK_VIEW=<network_view>
INFOBLOX_USERNAME=<username>
PASSWORD=<password>
CSV_FILE=vpc_data.csv
```

Generated: 2025-11-01
