# Architecture Documentation

## System Overview

Python scripts that synchronize AWS VPC network data with InfoBlox IPAM. The recommended script (`aws_infoblox_vpc_manager_complete_v1.py`) follows a three-layer design: data ingestion, business logic, and InfoBlox API integration.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  GitHub Repo (tshoush/IBX-AWS_Sync)             │
│                       vpc_data.csv                              │
└──────────────────────────────┬──────────────────────────────────┘
                               │ gh CLI (GitHub API)
                               │ fetch_csv_from_github()
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CSV Data File (vpc_data.csv)                  │
│  AccountId, Region, VpcId, Name, CidrBlock, Tags, ...           │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│           Python Import Scripts (This Repository)                │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Data Processing Layer                                  │    │
│  │  • CSV parsing (pandas)                                 │    │
│  │  • AWS Tags parsing (ast.literal_eval)                  │    │
│  │  • CIDR block validation                                │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Business Logic Layer                                   │    │
│  │  • Network comparison (AWS vs InfoBlox)                 │    │
│  │  • Extended Attribute analysis & mapping                │    │
│  │  • Container hierarchy management                       │    │
│  │  • Priority-based creation (larger CIDRs first)         │    │
│  │  • Dry-run simulation                                   │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  InfoBlox Integration Layer                             │    │
│  │  • REST API client (requests, Basic Auth)               │    │
│  │  • SSL verification disabled (internal servers)         │    │
│  │  • WAPI operations                                      │    │
│  │  • EA definition management                             │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTPS/REST (WAPI)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    InfoBlox Grid Master                          │
│  • Network objects  • Network containers                        │
│  • Extended attribute definitions  • Network views              │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Output Files (working directory)              │
│  aws_infoblox_vpc_manager.log      (always)                     │
│  missing_eas_<timestamp>.txt       (always)                     │
│  missing_networks_<timestamp>.csv  (when missing networks exist) │
│  rejected_networks_<timestamp>.csv (when networks are rejected)  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Classes

### `fetch_csv_from_github(repo, path, dest)`
Module-level function. Uses `gh auth token` to obtain a GitHub API token, then downloads the file via the GitHub Contents API (base64-decoded). Runs before VPC comparison when `GITHUB_REPO` is set in `config.env`.

### `InfoBloxClient`
REST API wrapper for InfoBlox WAPI. Uses `requests.Session` with Basic Auth; SSL verification is hardcoded off (`session.verify = False`).

Key methods:
- `get_network_by_cidr()` / `get_network_container_by_cidr()` — existence checks
- `create_network()` / `create_extensible_attribute()` — write operations
- `get_extensible_attributes()` — cached EA definition fetch
- `ensure_required_eas_exist()` — create missing EAs in bulk

### `VPCManager`
Core synchronization logic. Holds an `InfoBloxClient` and an `AWSTagParser`.

Key methods:
- `load_vpc_data()` — reads CSV with pandas
- `parse_vpc_tags()` — applies `AWSTagParser` to every row's Tags column
- `map_aws_tags_to_infoblox_eas()` — maps known AWS tag keys to EA names; unknown keys become `aws_<key>`
- `compare_vpc_with_infoblox()` — classifies each VPC as matching / missing / discrepancy / container
- `ensure_required_eas()` — collects all EA names needed by the dataset, checks InfoBlox, returns missing list; in non-dry-run mode calls `ensure_required_eas_exist()`
- `create_missing_networks()` — creates networks sorted by prefix length (larger first)

### `AWSTagParser`
Parses the Tags column from the AWS CSV export format (`[{'Key': ..., 'Value': ...}, ...]`) into a plain `{key: value}` dict using `ast.literal_eval`.

## Data Flow

```
1. GitHub fetch (if GITHUB_REPO set)
       │
       ▼
2. load_vpc_data()  →  parse_vpc_tags()
       │
       ▼
3. compare_vpc_with_infoblox()
   ├── matches      (CIDR exists, EAs match)
   ├── discrepancies (CIDR exists, EAs differ)
   ├── missing      (CIDR not in InfoBlox)
   ├── containers   (CIDR exists as networkcontainer)
   └── errors
       │
       ▼
4. ensure_required_eas()  →  missing_eas_<ts>.txt
       │
       ▼
5. missing networks  →  missing_networks_<ts>.csv
       │
       ▼
6. (if --create-missing)
   ensure_required_eas_exist()  →  create EAs
   create_missing_networks()    →  create networks (largest CIDR first)
   rejected networks            →  rejected_networks_<ts>.csv
```

## Extended Attributes (EA) Mapping

AWS Tags from the CSV `Tags` column are mapped to InfoBlox EA names:

| AWS Tag Key | InfoBlox EA Name |
|-------------|-----------------|
| Name | aws_name |
| environment / Environment | environment |
| owner / Owner | owner |
| project / Project | project |
| location | aws_location |
| cloudservice | aws_cloudservice |
| createdby | aws_created_by |
| RequestedBy | aws_requested_by |
| dud | aws_dud |
| AccountId | aws_account_id |
| Region | aws_region |
| VpcId | aws_vpc_id |
| Description | description |
| *(any other key)* | aws_<key_lowercased> |

EA values are truncated to 255 characters. EAs are created as `STRING` type if missing.

## Configuration

**Sources (first match wins):**
1. CLI flags (`--csv-file`, `--network-view`)
2. `config.env` file (loaded via `python-dotenv`)
3. Defaults

**Key config variables:**

| Variable | Required | Description |
|----------|----------|-------------|
| `GRID_MASTER` | Yes | InfoBlox server IP or hostname |
| `USERNAME` | Yes | InfoBlox username |
| `PASSWORD` | Yes | InfoBlox password |
| `NETWORK_VIEW` | No | InfoBlox network view (default: `default`) |
| `CSV_FILE` | No | Local CSV path (default: `vpc_data.csv`) |
| `GITHUB_REPO` | No | GitHub repo to fetch CSV from (e.g. `owner/repo`) |
| `GITHUB_CSV_PATH` | No | Path within repo (default: `vpc_data.csv`) |
| `PARENT_CONTAINER_PREFIXES` | No | Comma-separated prefix lengths for container creation |
| `CONTAINER_HIERARCHY_MODE` | No | `strict` or `flexible` |

## Script Variants

| Script | Mode default | EA analysis | GitHub fetch | Best for |
|--------|-------------|-------------|--------------|---------|
| v1 ⭐ | interactive (use `-q` to suppress) | Always | Yes | Automation, CI/CD |
| v2 | quiet (use `-i` for prompts) | No | No | Interactive ops |
| working | interactive | No | No | Simple tasks |
| prop_enhanced* | quiet | No | No | Overlap detection |

## Security Notes

- `config.env` is gitignored; never commit credentials
- SSL verification is disabled for InfoBlox (`session.verify = False`) — standard for internal WAPI endpoints
- GitHub access uses `gh auth token`; no separate token storage required

## Deployment Patterns

### Manual
```bash
source venv/bin/activate
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run
python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing
```

### Cron
```bash
0 2 * * * cd /path/to/scripts && source venv/bin/activate && \
  python aws_infoblox_vpc_manager_complete_v1.py --silent --create-missing \
  >> /var/log/infoblox-sync.log 2>&1
```

### CI/CD (GitLab example)
```yaml
infoblox-sync:
  script:
    - pip install -r setup/requirements_v1.txt
    - python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing
  only:
    - schedules
```

---

**Document Version**: 2.0
**Last Updated**: 2026-02-19
