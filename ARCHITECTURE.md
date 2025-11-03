# Architecture Documentation

## System Overview

This repository contains a collection of Python scripts designed to synchronize AWS VPC network data with InfoBlox IPAM (IP Address Management) systems. The architecture is modular, allowing different scripts to address specific use cases while sharing common patterns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Environment                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   VPC    │  │   VPC    │  │   VPC    │  │   VPC    │       │
│  │ 10.0.0.0 │  │ 10.1.0.0 │  │ 10.2.0.0 │  │ 10.3.0.0 │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ CSV Export
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CSV Data Files                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ VPC_ID, CIDR, Name, Tags, Region, ...                    │ │
│  │ vpc-12345, 10.0.0.0/16, Production, {...}, us-east-1, ... │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Input
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│           Python Import Scripts (This Repository)                │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Data Processing Layer                                  │    │
│  │  • CSV parsing                                          │    │
│  │  • Data validation                                      │    │
│  │  • Network overlap detection                            │    │
│  │  • CIDR block analysis                                  │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Business Logic Layer                                   │    │
│  │  • Network comparison                                   │    │
│  │  • Container hierarchy management                       │    │
│  │  • Extended attribute mapping                           │    │
│  │  • Dry-run simulation                                   │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  InfoBlox Integration Layer                             │    │
│  │  • REST API client                                      │    │
│  │  • Authentication                                       │    │
│  │  • WAPI operations                                      │    │
│  │  • Error handling & retry logic                         │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    InfoBlox Grid Master                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  IPAM Database                                           │  │
│  │  • Network objects                                       │  │
│  │  • Network containers                                    │  │
│  │  • Extended attributes                                   │  │
│  │  • Network views                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Core Components

#### InfoBloxClient Class
Handles all communication with InfoBlox WAPI (Web API).

```python
class InfoBloxClient:
    - grid_master: str          # InfoBlox server address
    - username: str             # Authentication username
    - password: str             # Authentication password
    - session: requests.Session # Persistent HTTP session

    Methods:
    - _make_request()          # Low-level HTTP request handler
    - get_networks()           # Retrieve network objects
    - create_network()         # Create new network
    - create_container()       # Create network container
    - update_network()         # Update existing network
    - get_network_views()      # List available network views
```

#### VPCManager / PropertyManager Class
Manages VPC/property data processing and synchronization logic.

```python
class VPCManager:
    - ib_client: InfoBloxClient # InfoBlox API client
    - logger: Logger            # Logging instance

    Methods:
    - load_vpc_data()          # Load and parse CSV data
    - parse_vpc_tags()         # Extract AWS tags
    - compare_vpc_with_infoblox() # Compare AWS vs InfoBlox
    - create_missing_networks()   # Sync missing networks
    - detect_overlaps()        # Find overlapping CIDRs
    - generate_reports()       # Create detailed reports
```

### 2. Data Flow

#### Step 1: Data Ingestion
```
CSV File → pandas DataFrame → Data Validation → Parsed Objects
```

**Key Operations:**
- CSV file reading with pandas
- Data type validation
- Required field checks
- CIDR block validation using `ipaddress` module

#### Step 2: Analysis
```
Parsed Data → Overlap Detection → Hierarchy Analysis → Comparison
```

**Key Operations:**
- Network overlap detection using IP network math
- Container hierarchy determination
- Comparison with existing InfoBlox networks
- Identification of missing/changed networks

#### Step 3: Synchronization
```
Missing Networks → Priority Sorting → Container Creation → Network Creation
```

**Key Operations:**
- Priority-based ordering (larger networks first)
- Container creation for parent networks
- Network object creation with extended attributes
- Transaction rollback on errors (in dry-run mode)

#### Step 4: Reporting
```
Operation Results → Report Generation → CSV/JSON/Log Output
```

**Key Operations:**
- Success/failure tracking
- Detailed operation logs
- CSV export of rejected networks
- Summary statistics

### 3. Script Variants

#### Version 1 (Recommended): aws_infoblox_vpc_manager_complete_v1.py
```
┌────────────────────────────────────────────┐
│  Explicit Mode Control                     │
│  • -q/--quiet flag                         │
│  • --silent flag                           │
│  • --no-interactive flag                   │
│  • --batch flag                            │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  Configuration Manager                     │
│  • Environment variables (config.env)      │
│  • Command-line overrides                  │
│  • Validation & defaults                   │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  VPC Manager (Core Logic)                  │
│  • CSV parsing                             │
│  • Network comparison                      │
│  • InfoBlox synchronization                │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  InfoBlox Client (API Layer)               │
│  • REST API calls                          │
│  • Authentication                          │
│  • Error handling                          │
└────────────────────────────────────────────┘
```

**Design Philosophy:**
- Automation-first approach
- Explicit mode flags for clarity
- Backward compatible with older systems
- Best for CI/CD pipelines

#### Version 2: aws_infoblox_vpc_manager_complete_v2.py
```
┌────────────────────────────────────────────┐
│  Interactive Mode Control                  │
│  • Quiet by default                        │
│  • -i/--interactive for prompts            │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  Enhanced Configuration UI                 │
│  • Interactive network view selection      │
│  • Dynamic CSV file picker                 │
│  • Configuration editor                    │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  VPC Manager (Same Core)                   │
└────────────────────────────────────────────┘
```

**Design Philosophy:**
- Modern quiet-by-default approach
- Interactive mode as opt-in feature
- Enhanced user experience for manual operations

#### Property Import Scripts (prop_infoblox_import_*.py)
```
┌────────────────────────────────────────────┐
│  Property Data Ingestion                   │
│  • Properties file parsing                 │
│  • Extended attributes extraction          │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  Network Overlap Detection                 │
│  • CIDR overlap analysis                   │
│  • Container identification                │
│  • Hierarchical relationships              │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  Smart Container Management                │
│  • Auto-container creation                 │
│  • Parent-child relationships              │
│  • Overlap resolution strategies           │
└────────────────────────────────────────────┘
```

**Design Philosophy:**
- Focus on property-based imports
- Advanced overlap detection and resolution
- Hierarchical network container management

## Data Models

### Network Object
```python
{
    'cidr': '10.0.0.0/16',              # CIDR block
    'network_view': 'default',          # InfoBlox network view
    'comment': 'Production VPC',        # Description
    'extattrs': {                       # Extended attributes
        'AWS_VPC_ID': 'vpc-12345',
        'AWS_Region': 'us-east-1',
        'Environment': 'production',
        'Owner': 'infrastructure-team'
    }
}
```

### Container Object
```python
{
    'cidr': '10.0.0.0/8',              # Parent CIDR block
    'network_view': 'default',          # InfoBlox network view
    'comment': 'AWS Networks Container',
    'extattrs': {
        'Type': 'Container',
        'Purpose': 'AWS VPC Organization'
    }
}
```

### VPC Data (from CSV)
```python
{
    'VpcId': 'vpc-12345',
    'CidrBlock': '10.0.0.0/16',
    'State': 'available',
    'Tags': {
        'Name': 'Production VPC',
        'Environment': 'prod',
        'Owner': 'team-name'
    },
    'Region': 'us-east-1',
    'IsDefault': False
}
```

## Integration Points

### 1. InfoBlox WAPI Integration

**Endpoint Structure:**
```
https://{grid_master}/wapi/v2.10/{object_type}
```

**Common Object Types:**
- `network`: Network objects
- `networkcontainer`: Network containers
- `networkview`: Network views
- `extensibleattributedef`: Extended attribute definitions

**Authentication:**
- HTTP Basic Authentication
- Username/Password credentials
- Session persistence for performance

**API Operations:**
```python
# GET - Query objects
GET /wapi/v2.10/network?network_view=default

# POST - Create object
POST /wapi/v2.10/network
Body: {"network": "10.0.0.0/16", "network_view": "default"}

# PUT - Update object
PUT /wapi/v2.10/network/{ref}
Body: {"comment": "Updated description"}

# DELETE - Remove object
DELETE /wapi/v2.10/network/{ref}
```

### 2. CSV Data Integration

**Expected CSV Format:**
```csv
VpcId,CidrBlock,State,Tags,Region,IsDefault
vpc-12345,"10.0.0.0/16",available,"{""Name"": ""Prod VPC""}",us-east-1,False
```

**Parsing Strategy:**
- pandas for CSV reading
- ast.literal_eval() for JSON-like tag parsing
- Data validation and cleaning
- Error handling for malformed data

### 3. Configuration Integration

**Configuration Sources (Priority Order):**
1. Command-line arguments (highest priority)
2. Environment variables
3. config.env file
4. Default values (lowest priority)

**Configuration Loading:**
```python
from dotenv import load_dotenv
load_dotenv('config.env')

grid_master = args.grid_master or os.getenv('GRID_MASTER')
```

## Error Handling Strategy

### 1. Validation Errors
```python
try:
    network = ipaddress.ip_network(cidr, strict=False)
except ValueError as e:
    logger.error(f"Invalid CIDR: {cidr}")
    # Add to rejected networks list
    continue
```

### 2. API Errors
```python
try:
    response = session.post(url, json=data)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 409:
        logger.warning("Network already exists")
    else:
        logger.error(f"API error: {e}")
        # Retry logic or rollback
```

### 3. Dry-Run Mode
```python
if dry_run:
    logger.info(f"[DRY-RUN] Would create network: {cidr}")
    # Simulate success
    return {'success': True, 'ref': 'simulated-ref'}
else:
    # Actual API call
    return ib_client.create_network(cidr)
```

## Performance Considerations

### 1. Batch Processing
- Process networks in batches
- Use connection pooling (requests.Session)
- Implement parallel processing where applicable

### 2. Caching
- Cache InfoBlox network views
- Cache existing networks for comparison
- Minimize redundant API calls

### 3. Logging Strategy
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- Structured logging for easier parsing
- Log rotation for long-running processes

## Security Architecture

### 1. Credential Management
```
config.env (gitignored) → Environment Variables → Application
```

**Best Practices:**
- Never commit credentials to git
- Use environment variables in production
- Rotate credentials regularly
- Use read-only accounts where possible

### 2. SSL/TLS
- All API communications over HTTPS
- SSL verification enabled by default
- Option to disable for testing (not recommended)

### 3. Input Validation
- Validate all CIDR blocks
- Sanitize user inputs
- Prevent injection attacks
- Validate file paths

## Testing Strategy

### 1. Dry-Run Testing
```bash
# Test without making changes
python script.py --dry-run
```

### 2. Incremental Testing
```bash
# Test with small dataset first
python script.py --csv-file sample_10_vpcs.csv --dry-run
```

### 3. Validation Testing
```bash
# Compare results
python script.py --dry-run > expected_output.txt
diff expected_output.txt actual_output.txt
```

## Deployment Patterns

### 1. Manual Execution
```bash
source venv/bin/activate
python aws_infoblox_vpc_manager_complete_v1.py -q --dry-run
```

### 2. Scheduled Execution (Cron)
```bash
# crontab -e
0 2 * * * cd /path/to/scripts && source venv/bin/activate && python aws_infoblox_vpc_manager_complete_v1.py --silent --create-missing >> /var/log/infoblox-sync.log 2>&1
```

### 3. CI/CD Pipeline
```yaml
# Example GitLab CI
infoblox-sync:
  script:
    - pip install -r requirements.txt
    - python aws_infoblox_vpc_manager_complete_v1.py -q --create-missing
  only:
    - schedules
```

## Monitoring and Observability

### 1. Logging
- File logging: `aws_infoblox_vpc_manager.log`
- Console logging: Real-time feedback
- Log levels for filtering

### 2. Metrics
- Networks processed
- Networks created
- Networks updated
- Errors encountered
- Execution time

### 3. Reporting
- CSV reports for rejected networks
- Summary reports
- Extended attribute analysis

## Future Architecture Considerations

### 1. Potential Enhancements
- Database backend for state management
- Web UI for monitoring and control
- REST API wrapper for remote execution
- Multi-region support
- AWS API integration (direct VPC querying)

### 2. Scalability
- Message queue for large-scale processing
- Distributed execution
- Microservices architecture
- Containerization (Docker)

### 3. High Availability
- Multiple InfoBlox Grid Master support
- Failover mechanisms
- Transaction rollback
- State persistence

---

**Document Version**: 1.0
**Last Updated**: 2025-11-02
**Maintained By**: Repository Contributors
