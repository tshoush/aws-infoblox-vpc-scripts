# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Python scripts to synchronize AWS VPC network data with InfoBlox IPAM. The core workflow: read VPC data from a CSV file, compare against InfoBlox networks via REST API, and create missing networks with AWS tags mapped to InfoBlox Extended Attributes (EAs).

## Setup and Running

```bash
# Install dependencies (creates venv in parent directory)
cd setup && ./setup_v1.sh

# Configure credentials
cp config.env.template config.env
# Edit config.env with GRID_MASTER, USERNAME, PASSWORD, CSV_FILE, NETWORK_VIEW

# Activate virtual environment (path set by setup script)
source ../venv/bin/activate

# Test safely with dry-run
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run

# Execute changes
python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing
```

There are no automated tests in this repository.

## Script Selection

**Recommended: `aws_infoblox_vpc_manager_complete_v1.py`** — explicit `-q/--quiet` flag required for non-interactive mode; best for CI/CD.

**Alternative: `aws_infoblox_vpc_manager_complete_v2.py`** — quiet by default, use `-i/--interactive` for prompts.

**`prop_infoblox_import*.py` variants** — for CSV-based properties import with network overlap detection and automatic container creation. All run quiet-by-default with `-i` for interactive.

The `_working.py` and base `prop_infoblox_import.py` are older/simpler versions without full feature sets.

## Key CLI Flags

```
--dry-run          Simulate all operations without changes (always test first)
--create-missing   Create networks absent from InfoBlox
-q / --quiet       Non-interactive; read all config from config.env
--silent           Minimal output, implies --no-interactive
--batch            Alias for quiet mode
-i / --interactive V2/prop scripts only: enable prompts
--csv-file FILE    Override CSV_FILE from config
--network-view     Override NETWORK_VIEW from config
```

## Architecture

Three-layer design common to all scripts:

1. **`InfoBloxClient`** — REST API wrapper for InfoBlox WAPI (Basic Auth, SSL verification disabled for internal servers). Key methods: `get_network_by_cidr()`, `create_network()`, `ensure_required_eas_exist()`.

2. **`VPCManager`** — Core sync logic. Loads CSV via pandas, parses AWS tags (`AWSTagParser`), compares VPCs against InfoBlox, detects CIDR overlaps, sorts by prefix length (larger networks first), creates containers then networks.

3. **`main()`** — Argument parsing, config loading from `config.env` via `python-dotenv`, mode selection, orchestration.

### Data Flow

```
CSV file (AWS VPC export)
  → pandas DataFrame
  → VPCManager.compare_vpc_with_infoblox()
  → detect overlaps → create containers
  → create_missing_networks() (sorted largest→smallest CIDR)
  → InfoBloxClient → InfoBlox WAPI (HTTPS)
  → logs: aws_infoblox_vpc_manager.log
  → rejected networks: CSV report
```

### Configuration Priority

`config.env` file → CLI flags override individual settings. The `config.env.template` documents all available variables including optional `PARENT_CONTAINER_PREFIXES` and `CONTAINER_HIERARCHY_MODE=strict`.

## Dependencies

- `pandas` — CSV parsing
- `requests` / `urllib3` — HTTP REST API
- `python-dotenv` — config.env loading

Each script has a corresponding `setup/requirements_*.txt` and `setup/setup_*.sh`.
