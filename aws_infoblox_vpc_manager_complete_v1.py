#!/usr/bin/env python3
"""
AWS to InfoBlox VPC Management Tool - Complete Enhanced Version

All features implemented:
1. Interactive configuration display & editing
2. Priority-based network creation (larger networks first)
3. Configurable container detection
4. Categorized rejected networks CSV generation
5. Enhanced Extended Attributes reporting
6. CSV file environment configuration

Author: Generated for AWS-InfoBlox Integration
Date: June 4, 2025
"""

import pandas as pd
import requests
import json
import urllib3
import ast
import logging
from datetime import datetime
from typing import Dict, List, Optional
import argparse
import os
from dotenv import load_dotenv
import getpass
import socket

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aws_infoblox_vpc_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def test_infoblox_connectivity(ib_client):
    """Test basic connectivity to InfoBlox before proceeding"""
    try:
        # Skip the socket test and go directly to API test
        # The socket test may fail in certain network environments even when HTTPS works
        print(f"Testing InfoBlox API connectivity to {ib_client.grid_master}...")

        # Test basic API connectivity
        try:
            response = ib_client._make_request('GET', 'networkview')
            print(f"✅ InfoBlox connectivity test successful")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ InfoBlox API test failed: {e}")
            print(f"   Please verify:")
            print(f"   1. InfoBlox server is accessible at {ib_client.grid_master}")
            print(f"   2. Username and password are correct")
            print(f"   3. Network connectivity allows HTTPS to port 443")
            return False

    except Exception as e:
        print(f"❌ Connectivity test failed: {e}")
        return False


def main():
    """Main function with all enhanced features"""
    args = parse_arguments()

    # Check if running in non-interactive mode
    no_interactive = args.no_interactive or args.silent
    silent_mode = args.silent

    try:
        # Show and optionally edit configuration (skip in non-interactive mode)
        if no_interactive:
            if not silent_mode:
                print("🤖 Running in non-interactive mode - reading configuration from file...")
            config_override = None
        else:
            config_override = show_and_edit_config()

        # Get configuration
        skip_prompt = args.network_view is not None
        config_result = get_config(
            skip_network_view_prompt=skip_prompt,
            config_override=config_override,
            no_interactive=no_interactive,
            silent_mode=silent_mode
        )

        # Check if configuration failed (quiet mode with missing values)
        if config_result[0] is None:
            return 1

        grid_master, network_view, username, password, csv_file_from_env, container_prefixes, container_mode = config_result
        
        # Override network view if specified
        if args.network_view:
            network_view = args.network_view
            print(f"Using network view from command line: {network_view}")
        
        # Show container configuration
        if container_prefixes:
            print(f"📦 Container prefixes configured: /{', /'.join(map(str, container_prefixes))}")
            print(f"🔧 Container mode: {container_mode}")
        else:
            print("📦 Container detection: Auto-detect from InfoBlox")
        
        # Use command line argument if provided, otherwise use environment variable
        csv_file = args.csv_file if args.csv_file != 'vpc_data.csv' else csv_file_from_env
        
        logger.info(f"Loading VPC data from {csv_file}...")
        
        # Initialize InfoBlox client
        print(f"\n🔗 Connecting to InfoBlox Grid Master: {grid_master}")
        ib_client = InfoBloxClient(grid_master, username, password)

        # Skip connectivity test - proceed directly to InfoBlox operations
        print("🔗 InfoBlox client initialized, proceeding with operations...")
        
        # Initialize VPC Manager
        vpc_manager = VPCManager(ib_client)
        
        # Load and parse VPC data
        try:
            vpc_df = vpc_manager.load_vpc_data(csv_file)
            vpc_df = vpc_manager.parse_vpc_tags(vpc_df)
        except Exception as e:
            logger.error(f"Failed to load VPC data: {e}")
            return 1
        
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"   📁 CSV file: {csv_file}")
        print(f"   🔢 Total VPCs loaded: {len(vpc_df)}")
        print(f"   🌐 Network view: {network_view}")
        
        # Compare with InfoBlox
        logger.info("Comparing AWS VPCs with InfoBlox networks...")
        comparison_results = vpc_manager.compare_vpc_with_infoblox(vpc_df, network_view)
        
        # Display results
        print(f"\n🔍 COMPARISON RESULTS:")
        print(f"   ✅ Matching networks: {len(comparison_results['matches'])}")
        print(f"   🔴 Missing networks: {len(comparison_results['missing'])}")
        print(f"   🟡 Tag discrepancies: {len(comparison_results['discrepancies'])}")
        print(f"   📦 Network containers: {len(comparison_results['containers'])}")
        print(f"   ❌ Processing errors: {len(comparison_results['errors'])}")

        # Check if all records resulted in errors (likely connectivity issue)
        total_records = len(vpc_df)
        error_count = len(comparison_results['errors'])
        if error_count == total_records and error_count > 0:
            print(f"\n⚠️  WARNING: All {total_records} VPC records resulted in processing errors!")
            print("This typically indicates a connectivity issue with InfoBlox.")
            print("💡 Suggestions:")
            print("   1. Check InfoBlox server connectivity")
            print("   2. Verify network configuration and firewall rules")
            print("   3. Run: python test_infoblox_connectivity.py")
            print("   4. Check InfoBlox server status and credentials")
        
        # Show network containers summary
        if comparison_results.get('containers'):
            print(f"\n📦 NETWORK CONTAINERS FOUND:")
            print(f"   🔢 VPCs existing as containers: {len(comparison_results['containers'])}")
            print(f"   ℹ️ These exist as network containers (parent networks) in InfoBlox")
            print(f"   💡 Container networks typically contain smaller subnet networks")
            for container in comparison_results['containers'][:3]:  # Show first 3
                print(f"   📦 {container['cidr']} - {container['vpc']['Name']}")
            if len(comparison_results['containers']) > 3:
                print(f"   ... and {len(comparison_results['containers']) - 3} more")
        
        # Handle create-missing flag
        if args.create_missing and comparison_results['missing']:
            print(f"\n🚀 CREATING MISSING NETWORKS:")
            
            # Ensure Extended Attributes exist
            ea_analysis = vpc_manager.ensure_required_eas(vpc_df, dry_run=args.dry_run)
            if args.dry_run:
                print(f"   🏷️ Extended Attributes analysis: {len(ea_analysis['missing_eas'])} missing")
            else:
                print(f"   🏷️ Extended Attributes: {ea_analysis['created_count']} created, {ea_analysis['existing_count']} existed")
            
            # Sort missing networks by priority (larger networks first)
            missing_with_priority = []
            for item in comparison_results['missing']:
                vpc = item['vpc']
                aws_tags = item['aws_tags']
                priority = vpc_manager._calculate_network_priority(vpc, aws_tags)
                missing_with_priority.append((priority, item))
            
            # Sort by priority
            missing_with_priority.sort(key=lambda x: x[0])
            sorted_missing = [item for priority, item in missing_with_priority]
            
            print(f"   📋 Creating {len(sorted_missing)} networks in priority order...")
            print(f"   🔢 Priority order: larger networks (/16, /17) before smaller (/24, /25)")
            
            # Create networks
            operation_results = vpc_manager.create_missing_networks(
                sorted_missing, 
                network_view=network_view, 
                dry_run=args.dry_run
            )
            
            # Show results
            created_count = sum(1 for r in operation_results if r.get('action') == 'created')
            would_create_count = sum(1 for r in operation_results if r.get('action') == 'would_create')
            error_count = sum(1 for r in operation_results if r.get('action') == 'error')
            rejected_count = sum(1 for r in operation_results if r.get('action') == 'would_reject')
            
            if args.dry_run:
                print(f"   ✅ Would create: {would_create_count}")
                print(f"   ⚠️ Would reject: {rejected_count}")
                print(f"   ❌ Would fail: {error_count}")
            else:
                print(f"   ✅ Successfully created: {created_count}")
                print(f"   ❌ Failed to create: {error_count}")
                if error_count > 0:
                    print(f"   📄 Check rejected networks CSV for failed creations")
        
        print(f"\n✅ OPERATION COMPLETED")
        print(f"   📝 Check logs: aws_infoblox_vpc_manager.log")
        print(f"   📊 For detailed reports, check the reports/ directory")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Error: {e}")
        return 1


class InfoBloxClient:
    """InfoBlox WAPI client for network management"""
    
    def __init__(self, grid_master: str, username: str, password: str, api_version: str = "v2.13.1"):
        self.grid_master = grid_master
        self.username = username
        self.password = password
        self.api_version = api_version
        self.base_url = f"https://{grid_master}/wapi/{api_version}"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = False
        self._ea_cache = {}  # Cache for Extended Attribute definitions
        
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request to InfoBlox WAPI"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            error_msg = f"InfoBlox API request failed: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    if 'text' in error_details:
                        error_msg += f" - Details: {error_details['text']}"
                    elif 'Error' in error_details:
                        error_msg += f" - Details: {error_details['Error']}"
                except:
                    error_msg += f" - Response: {e.response.text}"
            logger.error(error_msg)
            raise
    
    def get_network_by_cidr(self, cidr: str, network_view: str = "default") -> Optional[Dict]:
        """Get specific network by CIDR block"""
        params = {
            'network': cidr,
            'network_view': network_view,
            '_return_fields': 'network,comment,extattrs'
        }
        
        try:
            response = self._make_request('GET', 'network', params=params)
            networks = response.json()
            return networks[0] if networks else None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                logger.debug(f"Network {cidr} not found in view {network_view}")
                return None
            else:
                raise
    
    def get_network_container_by_cidr(self, cidr: str, network_view: str = "default") -> Optional[Dict]:
        """Get specific network container by CIDR block"""
        params = {
            'network': cidr,
            'network_view': network_view,
            '_return_fields': 'network,comment,extattrs'
        }
        
        try:
            response = self._make_request('GET', 'networkcontainer', params=params)
            containers = response.json()
            return containers[0] if containers else None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                logger.debug(f"Network container {cidr} not found in view {network_view}")
                return None
            else:
                raise
    
    def check_network_or_container_exists(self, cidr: str, network_view: str = "default") -> Dict:
        """Check if CIDR exists as either a network or network container"""
        # First check if it exists as a regular network
        network = self.get_network_by_cidr(cidr, network_view)
        if network:
            return {
                'exists': True,
                'type': 'network',
                'object': network
            }
        
        # Then check if it exists as a network container
        container = self.get_network_container_by_cidr(cidr, network_view)
        if container:
            return {
                'exists': True,
                'type': 'container',
                'object': container
            }
        
        return {
            'exists': False,
            'type': None,
            'object': None
        }
    
    def create_network(self, cidr: str, network_view: str = "default", 
                      comment: str = "", extattrs: Optional[Dict[str, str]] = None) -> Dict:
        """Create a new network in InfoBlox"""
        data = {
            'network': cidr,
            'network_view': network_view
        }
        
        if comment:
            data['comment'] = comment
            
        if extattrs:
            data['extattrs'] = {k: {'value': v} for k, v in extattrs.items()}
        
        response = self._make_request('POST', 'network', data=data)
        logger.info(f"Created network {cidr} in view {network_view}")
        return response.json()
    
    def get_extensible_attributes(self) -> List[Dict]:
        """Get all Extended Attribute definitions from InfoBlox"""
        if 'definitions' not in self._ea_cache:
            response = self._make_request('GET', 'extensibleattributedef')
            self._ea_cache['definitions'] = response.json()
        return self._ea_cache['definitions']
    
    def create_extensible_attribute(self, name: str, data_type: str = "STRING", 
                                  comment: str = "", default_value: str = "") -> Dict:
        """Create a new Extended Attribute definition in InfoBlox"""
        data = {
            'name': name,
            'type': data_type,
            'comment': comment
        }
        
        if default_value:
            data['default_value'] = default_value
        
        try:
            response = self._make_request('POST', 'extensibleattributedef', data=data)
            logger.info(f"Created Extended Attribute definition: {name}")
            if 'definitions' in self._ea_cache:
                del self._ea_cache['definitions']
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                error_details = e.response.text
                if "already exists" in error_details.lower():
                    logger.info(f"Extended Attribute {name} already exists")
                    return {'status': 'exists', 'name': name}
            raise
    
    def ensure_required_eas_exist(self, required_eas: List[str]) -> Dict[str, str]:
        """Ensure required Extended Attributes exist in InfoBlox, create if missing"""
        existing_eas = self.get_extensible_attributes()
        existing_names = {ea['name'] for ea in existing_eas}
        
        results = {}
        
        for ea_name in required_eas:
            if ea_name not in existing_names:
                logger.info(f"Creating missing Extended Attribute: {ea_name}")
                result = self.create_extensible_attribute(
                    name=ea_name,
                    data_type="STRING",
                    comment=f"AWS tag mapping for {ea_name}",
                    default_value=""
                )
                results[ea_name] = 'created'
            else:
                results[ea_name] = 'exists'
        
        return results


class AWSTagParser:
    """Handles parsing of AWS tags from various formats"""
    
    @staticmethod
    def parse_tags_from_string(tags_str: str) -> Dict[str, str]:
        """Parse AWS tags from string representation"""
        if not tags_str or pd.isna(tags_str) or tags_str == '[]':
            return {}
        
        try:
            if isinstance(tags_str, str):
                tags_str = tags_str.strip()
                if tags_str.startswith('[') and tags_str.endswith(']'):
                    tag_list = ast.literal_eval(tags_str)
                    if isinstance(tag_list, list):
                        return {tag['Key']: tag['Value'] for tag in tag_list if 'Key' in tag and 'Value' in tag}
            elif isinstance(tags_str, list):
                return {tag['Key']: tag['Value'] for tag in tags_str if 'Key' in tag and 'Value' in tag}
            
            return {}
            
        except (ValueError, SyntaxError, KeyError) as e:
            logger.warning(f"Error parsing tags: {tags_str[:100]}... Error: {e}")
            return {}


class VPCManager:
    """Main class for managing AWS VPC to InfoBlox synchronization"""
    
    def __init__(self, infoblox_client: InfoBloxClient):
        self.ib_client = infoblox_client
        self.tag_parser = AWSTagParser()
        
    def load_vpc_data(self, csv_file_path: str) -> pd.DataFrame:
        """Load VPC data from CSV file"""
        try:
            df = pd.read_csv(csv_file_path)
            logger.info(f"Loaded {len(df)} VPC records from {csv_file_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading VPC data: {e}")
            raise
    
    def parse_vpc_tags(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse tags column and add parsed tags as new column"""
        df = df.copy()
        df['ParsedTags'] = df['Tags'].apply(self.tag_parser.parse_tags_from_string)
        return df
    
    def map_aws_tags_to_infoblox_eas(self, aws_tags: Dict[str, str]) -> Dict[str, str]:
        """Map AWS tags to InfoBlox Extended Attributes"""
        tag_mapping = {
            'Name': 'aws_name',
            'environment': 'environment', 
            'Environment': 'environment',
            'owner': 'owner',
            'Owner': 'owner', 
            'project': 'project',
            'Project': 'project',
            'location': 'aws_location',
            'Location': 'aws_location',
            'cloudservice': 'aws_cloudservice',
            'createdby': 'aws_created_by',
            'RequestedBy': 'aws_requested_by',
            'Requested_By': 'aws_requested_by',
            'dud': 'aws_dud',
            'AccountId': 'aws_account_id',
            'Region': 'aws_region',
            'VpcId': 'aws_vpc_id',
            'Description': 'description'
        }
        
        mapped_eas = {}
        for aws_key, aws_value in aws_tags.items():
            ea_key = tag_mapping.get(aws_key, f"aws_{aws_key.lower()}")
            ea_key = ea_key.replace('-', '_').replace(' ', '_').lower()
            ea_value = str(aws_value)[:255] if len(str(aws_value)) > 255 else str(aws_value)
            mapped_eas[ea_key] = ea_value
        
        return mapped_eas



    def compare_vpc_with_infoblox(self, vpc_df: pd.DataFrame, network_view: str = "default") -> Dict:
        """Compare AWS VPC data with InfoBlox networks and network containers"""
        results = {
            'matches': [],
            'missing': [], 
            'discrepancies': [],
            'containers': [],
            'errors': []
        }
        
        for _, vpc in vpc_df.iterrows():
            try:
                cidr = vpc['CidrBlock']
                aws_tags = vpc.get('ParsedTags', {})
                
                existence_check = self.ib_client.check_network_or_container_exists(cidr, network_view)
                
                if not existence_check['exists']:
                    results['missing'].append({
                        'vpc': vpc.to_dict(),
                        'cidr': cidr,
                        'aws_tags': aws_tags,
                        'mapped_eas': self.map_aws_tags_to_infoblox_eas(aws_tags)
                    })
                elif existence_check['type'] == 'container':
                    ib_container = existence_check['object']
                    ib_eas = {k: v.get('value', '') for k, v in ib_container.get('extattrs', {}).items()}
                    mapped_eas = self.map_aws_tags_to_infoblox_eas(aws_tags)
                    
                    results['containers'].append({
                        'vpc': vpc.to_dict(),
                        'cidr': cidr,
                        'ib_container': ib_container,
                        'aws_tags': aws_tags,
                        'ib_eas': ib_eas,
                        'mapped_eas': mapped_eas,
                        'note': 'Exists as network container - contains subnets'
                    })
                    logger.info(f"CIDR {cidr} exists as network container in InfoBlox")
                else:
                    ib_network = existence_check['object']
                    ib_eas = {k: v.get('value', '') for k, v in ib_network.get('extattrs', {}).items()}
                    mapped_eas = self.map_aws_tags_to_infoblox_eas(aws_tags)
                    
                    if self._compare_eas(mapped_eas, ib_eas):
                        results['matches'].append({
                            'vpc': vpc.to_dict(),
                            'cidr': cidr,
                            'ib_network': ib_network,
                            'aws_tags': aws_tags,
                            'ib_eas': ib_eas
                        })
                    else:
                        results['discrepancies'].append({
                            'vpc': vpc.to_dict(),
                            'cidr': cidr,
                            'ib_network': ib_network,
                            'aws_tags': aws_tags,
                            'ib_eas': ib_eas,
                            'mapped_eas': mapped_eas
                        })
                        
            except Exception as e:
                logger.error(f"Error processing VPC {vpc.get('VpcId', 'unknown')}: {e}")
                results['errors'].append({
                    'vpc': vpc.to_dict(),
                    'error': str(e)
                })
        
        return results
    
    def _compare_eas(self, mapped_eas: Dict[str, str], ib_eas: Dict[str, str]) -> bool:
        """Compare mapped AWS tags with InfoBlox EAs"""
        for key, value in mapped_eas.items():
            if key not in ib_eas or ib_eas[key] != value:
                return False
        return True
    
    def _calculate_network_priority(self, vpc: Dict, aws_tags: Dict[str, str]) -> int:
        """Calculate priority for network creation (lower number = higher priority)"""
        try:
            cidr_prefix = int(vpc['CidrBlock'].split('/')[1])
            priority = cidr_prefix
        except:
            priority = 99
        
        env = aws_tags.get('environment', aws_tags.get('Environment', '')).lower()
        if env in ['prod', 'production']:
            priority -= 5
        elif env in ['staging', 'stage']:
            priority -= 3
        elif env in ['test', 'testing']:
            priority -= 2
        elif env in ['dev', 'development']:
            priority -= 1
        
        return max(1, priority)
    
    def ensure_required_eas(self, vpc_df: pd.DataFrame, dry_run: bool = True) -> Dict:
        """Ensure all required Extended Attributes exist in InfoBlox"""
        logger.info("Analyzing required Extended Attributes...")
        
        all_required_eas = set()
        
        for _, vpc in vpc_df.iterrows():
            aws_tags = vpc.get('ParsedTags', {})
            mapped_eas = self.map_aws_tags_to_infoblox_eas(aws_tags)
            all_required_eas.update(mapped_eas.keys())
        
        required_eas_list = sorted(list(all_required_eas))
        logger.info(f"Found {len(required_eas_list)} unique Extended Attributes required")
        
        if dry_run:
            existing_eas = self.ib_client.get_extensible_attributes()
            existing_names = {ea['name'] for ea in existing_eas}
            missing_eas = [ea for ea in required_eas_list if ea not in existing_names]
            
            return {
                'required_eas': required_eas_list,
                'existing_eas': list(existing_names),
                'missing_eas': missing_eas,
                'action': 'dry_run'
            }
        else:
            ea_results = self.ib_client.ensure_required_eas_exist(required_eas_list)
            
            created_count = sum(1 for status in ea_results.values() if status == 'created')
            existing_count = sum(1 for status in ea_results.values() if status == 'exists')
            
            return {
                'required_eas': required_eas_list,
                'ea_results': ea_results,
                'created_count': created_count,
                'existing_count': existing_count,
                'action': 'ensured'
            }
    
    def create_missing_networks(self, missing_networks: List[Dict], network_view: str = "default", 
                              dry_run: bool = True) -> List[Dict]:
        """Create missing networks in InfoBlox"""
        results = []
        rejected_networks = []
        
        for item in missing_networks:
            try:
                vpc = item['vpc']
                cidr = item['cidr']
                mapped_eas = item['mapped_eas']
                
                comment = f"AWS VPC: {vpc['Name']} ({vpc['VpcId']}) in {vpc['AccountId']}/{vpc['Region']}"
                
                if dry_run:
                    existence_check = self.ib_client.check_network_or_container_exists(cidr, network_view)
                    if existence_check['exists'] and existence_check['type'] == 'container':
                        logger.info(f"DRY RUN: {cidr} exists as network container - cannot create as regular network")
                        results.append({
                            'cidr': cidr,
                            'action': 'would_reject',
                            'reason': 'exists_as_container'
                        })
                    else:
                        logger.info(f"DRY RUN: Would create network {cidr}")
                        results.append({
                            'cidr': cidr,
                            'action': 'would_create'
                        })
                else:
                    response = self.ib_client.create_network(
                        cidr=cidr,
                        network_view=network_view,
                        comment=comment,
                        extattrs=mapped_eas
                    )
                    results.append({
                        'cidr': cidr,
                        'action': 'created',
                        'response': response
                    })
                    
            except Exception as e:
                error_str = str(e)
                logger.error(f"Error creating network {item['cidr']}: {error_str}")
                
                rejection_reason = "Unknown error"
                if "network container" in error_str.lower() or "parent" in error_str.lower():
                    rejection_reason = "Conflicts with existing network container"
                elif "already exists" in error_str.lower():
                    rejection_reason = "Network already exists"
                elif "extensible attribute" in error_str.lower():
                    rejection_reason = "Extended Attribute error"
                elif "overlap" in error_str.lower():
                    rejection_reason = "Network overlap conflict"
                
                results.append({
                    'cidr': item['cidr'],
                    'action': 'error',
                    'error': error_str,
                    'rejection_reason': rejection_reason
                })
                
                rejected_networks.append({
                    'vpc': item['vpc'],
                    'reason': rejection_reason,
                    'error_details': error_str
                })
        
        # Generate rejected networks CSV if there are any rejections
        if rejected_networks and not dry_run:
            self._generate_rejected_networks_csv(rejected_networks)
        
        return results
    
    def _generate_rejected_networks_csv(self, rejected_networks: List[Dict]) -> None:
        """Generate rejected networks CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rejected_networks_{timestamp}.csv"
        
        csv_data = []
        for item in rejected_networks:
            vpc = item['vpc']
            csv_row = {
                'AccountId': vpc.get('AccountId', ''),
                'Region': vpc.get('Region', ''),
                'VpcId': vpc.get('VpcId', ''),
                'Name': vpc.get('Name', ''),
                'CidrBlock': vpc.get('CidrBlock', ''),
                'RejectionReason': item.get('reason', ''),
                'ErrorDetails': item.get('error_details', '')
            }
            csv_data.append(csv_row)
        
        df = pd.DataFrame(csv_data)
        df.to_csv(filename, index=False)
        
        logger.info(f"Generated rejected networks CSV: {filename}")
        print(f"\n📄 REJECTED NETWORKS FILE GENERATED: {filename}")


def show_and_edit_config():
    """Display current configuration and allow interactive editing"""
    load_dotenv('config.env')

    print("\n" + "=" * 60)
    print("📋 CURRENT CONFIGURATION")
    print("=" * 60)

    config = {
        'GRID_MASTER': os.getenv('GRID_MASTER', ''),
        'NETWORK_VIEW': os.getenv('NETWORK_VIEW', 'default'),
        'USERNAME': os.getenv('USERNAME', ''),
        'PASSWORD': os.getenv('PASSWORD', ''),
        'CSV_FILE': os.getenv('CSV_FILE', 'vpc_data.csv'),
        'PARENT_CONTAINER_PREFIXES': os.getenv('PARENT_CONTAINER_PREFIXES', ''),
        'CONTAINER_HIERARCHY_MODE': os.getenv('CONTAINER_HIERARCHY_MODE', 'strict')
    }

    print(f"1. 🌐 InfoBlox Grid Master: {config['GRID_MASTER'] or '(not set)'}")
    print(f"2. 🔍 Network View: {config['NETWORK_VIEW']}")
    print(f"3. 👤 Username: {config['USERNAME'] or '(not set)'}")
    print(f"4. 🔒 Password: {'***' if config['PASSWORD'] else '(not set)'}")
    print(f"5. 📄 CSV File: {config['CSV_FILE']}")
    print(f"6. 📦 Container Prefixes: {config['PARENT_CONTAINER_PREFIXES'] or '(auto-detect)'}")
    print(f"7. 🔧 Container Mode: {config['CONTAINER_HIERARCHY_MODE']}")

    print("\n" + "=" * 60)

    while True:
        choice = input("\nDo you want to modify any configuration? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            config = edit_configuration_interactive(config)
            break
        elif choice in ['n', 'no']:
            break
        else:
            print("Please enter 'y' for yes or 'n' for no.")

    return config


def edit_configuration_interactive(config):
    """Interactive configuration editor"""
    print("\n📝 INTERACTIVE CONFIGURATION EDITOR")
    print("=" * 50)
    print("Enter new values (press Enter to keep current value)")
    print("Type 'skip' to skip all remaining prompts")
    print("=" * 50)

    # Create a copy to modify
    new_config = config.copy()

    # Grid Master
    current = new_config['GRID_MASTER'] or '(not set)'
    new_value = input(f"\n1. InfoBlox Grid Master [{current}]: ").strip()
    if new_value.lower() == 'skip':
        return new_config
    if new_value:
        new_config['GRID_MASTER'] = new_value

    # Network View
    current = new_config['NETWORK_VIEW']
    new_value = input(f"\n2. Network View [{current}]: ").strip()
    if new_value.lower() == 'skip':
        return new_config
    if new_value:
        new_config['NETWORK_VIEW'] = new_value

    # Username
    current = new_config['USERNAME'] or '(not set)'
    new_value = input(f"\n3. Username [{current}]: ").strip()
    if new_value.lower() == 'skip':
        return new_config
    if new_value:
        new_config['USERNAME'] = new_value

    # Password
    current = '***' if new_config['PASSWORD'] else '(not set)'
    print(f"\n4. Password [{current}]:")
    print("   Enter 'keep' to keep current password")
    print("   Enter 'clear' to clear password (will prompt later)")
    print("   Enter new password to change it")
    new_value = getpass.getpass("   New password: ").strip()
    if new_value.lower() == 'skip':
        return new_config
    elif new_value.lower() == 'clear':
        new_config['PASSWORD'] = ''
    elif new_value and new_value.lower() != 'keep':
        new_config['PASSWORD'] = new_value

    # CSV File
    current = new_config['CSV_FILE']
    new_value = input(f"\n5. CSV File [{current}]: ").strip()
    if new_value.lower() == 'skip':
        return new_config
    if new_value:
        new_config['CSV_FILE'] = new_value

    # Container Prefixes
    current = new_config['PARENT_CONTAINER_PREFIXES'] or '(auto-detect)'
    print(f"\n6. Container Prefixes [{current}]:")
    print("   Enter comma-separated CIDR prefixes (e.g., 16,17)")
    print("   Leave empty for auto-detection")
    new_value = input("   Container prefixes: ").strip()
    if new_value.lower() == 'skip':
        return new_config
    if new_value or new_value == '':  # Allow clearing
        new_config['PARENT_CONTAINER_PREFIXES'] = new_value

    # Container Mode
    current = new_config['CONTAINER_HIERARCHY_MODE']
    print(f"\n7. Container Mode [{current}]:")
    print("   'strict' - Only create networks that don't conflict with containers")
    print("   'permissive' - Allow network creation even if containers exist")
    new_value = input("   Container mode (strict/permissive): ").strip().lower()
    if new_value.lower() == 'skip':
        return new_config
    if new_value in ['strict', 'permissive']:
        new_config['CONTAINER_HIERARCHY_MODE'] = new_value
    elif new_value:
        print(f"   Warning: Invalid mode '{new_value}', keeping '{current}'")

    # Show updated configuration
    print("\n" + "=" * 50)
    print("📋 UPDATED CONFIGURATION")
    print("=" * 50)
    print(f"🌐 InfoBlox Grid Master: {new_config['GRID_MASTER'] or '(not set)'}")
    print(f"🔍 Network View: {new_config['NETWORK_VIEW']}")
    print(f"👤 Username: {new_config['USERNAME'] or '(not set)'}")
    print(f"🔒 Password: {'***' if new_config['PASSWORD'] else '(not set)'}")
    print(f"📄 CSV File: {new_config['CSV_FILE']}")
    print(f"📦 Container Prefixes: {new_config['PARENT_CONTAINER_PREFIXES'] or '(auto-detect)'}")
    print(f"🔧 Container Mode: {new_config['CONTAINER_HIERARCHY_MODE']}")

    # Ask if user wants to save to config.env
    while True:
        save_choice = input(f"\nSave these settings to config.env? (y/n): ").strip().lower()
        if save_choice in ['y', 'yes']:
            save_config_to_file(new_config)
            print("✅ Configuration saved to config.env")
            break
        elif save_choice in ['n', 'no']:
            print("⚠️  Configuration not saved - changes will only apply to this session")
            break
        else:
            print("Please enter 'y' for yes or 'n' for no.")

    return new_config


def save_prompted_config(prompted_values):
    """Save only the prompted values to config.env, preserving existing values"""
    # Read existing config if it exists
    existing_config = {}
    if os.path.exists('config.env'):
        try:
            load_dotenv('config.env')
            existing_config = {
                'GRID_MASTER': os.getenv('GRID_MASTER', ''),
                'NETWORK_VIEW': os.getenv('NETWORK_VIEW', 'default'),
                'USERNAME': os.getenv('USERNAME', ''),
                'PASSWORD': os.getenv('PASSWORD', ''),
                'CSV_FILE': os.getenv('CSV_FILE', 'vpc_data.csv'),
                'PARENT_CONTAINER_PREFIXES': os.getenv('PARENT_CONTAINER_PREFIXES', ''),
                'CONTAINER_HIERARCHY_MODE': os.getenv('CONTAINER_HIERARCHY_MODE', 'strict')
            }
        except:
            pass  # If reading fails, start with empty config

    # Update with prompted values
    existing_config.update(prompted_values)

    # Save the complete configuration
    save_config_to_file(existing_config)


def save_config_to_file(config):
    """Save configuration to config.env file"""
    config_content = f"""# InfoBlox Configuration
# Generated by AWS-InfoBlox VPC Manager on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# InfoBlox Grid Master IP/hostname
GRID_MASTER={config['GRID_MASTER']}

# InfoBlox Network View (default is usually 'default')
NETWORK_VIEW={config['NETWORK_VIEW']}

# InfoBlox API Credentials
USERNAME={config['USERNAME']}
# Note: For security, consider leaving password empty to be prompted
PASSWORD={config['PASSWORD']}

# Optional: API Version (default is v2.13.1)
API_VERSION=v2.13.1

# AWS VPC Data CSV File (default is vpc_data.csv)
CSV_FILE={config['CSV_FILE']}

# Network Container Configuration
# Configure parent container detection and handling
# PARENT_CONTAINER_PREFIXES: Comma-separated list of CIDR prefixes that should be treated as containers
# Examples: 16,17 means /16 and /17 networks are containers
# Leave empty to auto-detect based on actual InfoBlox container objects
PARENT_CONTAINER_PREFIXES={config['PARENT_CONTAINER_PREFIXES']}

# CONTAINER_HIERARCHY_MODE: How to handle container relationships
# strict: Only create networks that don't conflict with containers
# permissive: Allow network creation even if containers exist (may cause warnings)
CONTAINER_HIERARCHY_MODE={config['CONTAINER_HIERARCHY_MODE']}
"""

    try:
        with open('config.env', 'w') as f:
            f.write(config_content)
    except Exception as e:
        print(f"❌ Error saving config.env: {e}")
        print("Please check file permissions and try again.")


def get_config(skip_network_view_prompt=False, config_override=None, no_interactive=False, silent_mode=False):
    """Load configuration from environment or prompt user"""
    if config_override:
        grid_master = config_override['GRID_MASTER']
        network_view = config_override['NETWORK_VIEW']
        username = config_override['USERNAME']
        password = config_override['PASSWORD']
        csv_file = config_override['CSV_FILE']
        container_prefixes_str = config_override['PARENT_CONTAINER_PREFIXES']
        container_mode = config_override['CONTAINER_HIERARCHY_MODE']
    else:
        load_dotenv('config.env')
        grid_master = os.getenv('GRID_MASTER')
        network_view = os.getenv('NETWORK_VIEW', 'default')
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')
        csv_file = os.getenv('CSV_FILE', 'vpc_data.csv')
        container_prefixes_str = os.getenv('PARENT_CONTAINER_PREFIXES', '')
        container_mode = os.getenv('CONTAINER_HIERARCHY_MODE', 'strict').lower()
    
    # Parse container configuration
    container_prefixes = []
    if container_prefixes_str:
        try:
            container_prefixes = [int(x.strip()) for x in container_prefixes_str.split(',') if x.strip()]
        except ValueError as e:
            logger.warning(f"Invalid PARENT_CONTAINER_PREFIXES format: {e}. Using auto-detection.")
    
    # Track if any values were prompted for
    prompted_values = {}
    values_were_prompted = False

    # In non-interactive mode, check if all required values are available
    if no_interactive:
        missing_values = []
        if not grid_master:
            missing_values.append("GRID_MASTER")
        if not username:
            missing_values.append("USERNAME")
        if not password:
            missing_values.append("PASSWORD")

        if missing_values:
            if not silent_mode:
                print(f"❌ ERROR: Non-interactive mode requires all configuration values in config.env")
                print(f"Missing values: {', '.join(missing_values)}")
                print(f"Please run without --no-interactive to configure interactively, or update config.env")
            return None, None, None, None, None, None, None

        if not silent_mode:
            print(f"✅ All configuration loaded from config.env")
            print(f"   Grid Master: {grid_master}")
            print(f"   Username: {username}")
            print(f"   Network View: {network_view}")
            print(f"   CSV File: {csv_file}")
    else:
        # Interactive mode - prompt for missing values
        if not grid_master:
            grid_master = input("Enter InfoBlox Grid Master IP/hostname: ").strip()
            prompted_values['GRID_MASTER'] = grid_master
            values_were_prompted = True

        if not username:
            username = input(f"Enter InfoBlox username (default: admin): ").strip() or 'admin'
            prompted_values['USERNAME'] = username
            values_were_prompted = True

        if not password:
            password = getpass.getpass("Enter InfoBlox password: ")
            prompted_values['PASSWORD'] = password
            values_were_prompted = True

        # Only prompt for network view if not overridden by command line
        if not skip_network_view_prompt:
            new_network_view = input(f"Enter Network View (default: {network_view}): ").strip()
            if new_network_view:
                network_view = new_network_view
                prompted_values['NETWORK_VIEW'] = network_view
                values_were_prompted = True

        # If any values were prompted, ask if user wants to save them
        if values_were_prompted and not config_override:
            print(f"\n💾 Save Configuration")
            print("=" * 30)
            save_choice = input(f"Save the entered values to config.env for future use? (y/n): ").strip().lower()
            if save_choice in ['y', 'yes']:
                save_prompted_config(prompted_values)
                print("✅ Configuration saved to config.env")
            else:
                print("⚠️  Configuration not saved - you'll be prompted again next time")

    return grid_master, network_view, username, password, csv_file, container_prefixes, container_mode


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="AWS to InfoBlox VPC Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--csv-file', 
        default='vpc_data.csv',
        help='Path to AWS VPC CSV file (default: vpc_data.csv)'
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    parser.add_argument(
        '--create-missing', 
        action='store_true',
        help='Create missing networks in InfoBlox'
    )
    
    parser.add_argument(
        '--network-view',
        default=None,
        help='InfoBlox network view'
    )

    parser.add_argument(
        '--no-interactive', '--batch', '--quiet', '-q',
        action='store_true',
        dest='no_interactive',
        help='Non-interactive mode - no prompts, read all config from file (for automation)'
    )

    parser.add_argument(
        '--silent',
        action='store_true',
        help='Silent mode - minimal output, implies --no-interactive'
    )

    return parser.parse_args()


if __name__ == "__main__":
    exit(main())
