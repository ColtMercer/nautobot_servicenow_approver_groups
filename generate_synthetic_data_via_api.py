import os
import requests
import getpass
import random

# Prompt for API URL and token if not set
API_URL = "http://localhost:8080/api/"
API_TOKEN = "b0dec6e1fa9346659e5920768343928897aabd80"

HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def api_post(endpoint, data):
    url = f"{API_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    resp = requests.post(url, json=data, headers=HEADERS)
    if resp.status_code not in (200, 201):
        print(f"Error POST {url}: {resp.status_code} {resp.text}")
    return resp.json() if resp.ok else None

def api_get(endpoint, params=None):
    url = f"{API_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    resp = requests.get(url, params=params, headers=HEADERS)
    return resp.json() if resp.ok else None

def get_or_create(endpoint, unique_fields, data):
    params = {k: data[k] for k in unique_fields}
    existing = api_get(endpoint, params)
    if existing and existing.get('count', 0) > 0:
        return existing['results'][0]
    return api_post(endpoint, data)

def ensure_location_types():
    # Ensure required location types exist, create if missing, with correct parent relationships
    # 1. Geo Region (no parent, nestable)
    geo_region = get_or_create(
        "dcim/location-types/",
        ["slug"],
        {"name": "Geo Region", "slug": "geo-region", "description": "Top-level region", "nestable": True}
    )
    if not geo_region:
        print("Failed to create or fetch LocationType: Geo Region")
        return {}
    # 2. Country (parent: Geo Region, not nestable)
    country = get_or_create(
        "dcim/location-types/",
        ["slug"],
        {"name": "Country", "slug": "country", "description": "Country within a region", "nestable": False, "parent": geo_region["id"]}
    )
    if not country:
        print("Failed to create or fetch LocationType: Country")
        return {}
    # PATCH if parent or nestable is wrong
    if (country.get("parent") != geo_region["id"] or country.get("nestable", True)):
        patch_url = country["url"]
        requests.patch(patch_url, json={"parent": geo_region["id"], "nestable": False}, headers=HEADERS)
        country = api_get(f"dcim/location-types/{country['id']}/")
    # 3. Campus (parent: Country, not nestable, allows devices)
    campus = get_or_create(
        "dcim/location-types/",
        ["slug"],
        {"name": "Campus", "slug": "campus", "description": "Campus or site within a country", "nestable": False, "parent": country["id"], "content_types": ["dcim.device"]}
    )
    if not campus:
        print("Failed to create or fetch LocationType: Campus")
        return {}
    if (campus.get("parent") != country["id"] or campus.get("nestable", True) or "dcim.device" not in campus.get("content_types", [])):
        patch_url = campus["url"]
        requests.patch(patch_url, json={"parent": country["id"], "nestable": False, "content_types": ["dcim.device"]}, headers=HEADERS)
        campus = api_get(f"dcim/location-types/{campus['id']}/")
    return {"geo-region": geo_region["id"], "country": country["id"], "campus": campus["id"]}

def ensure_dummy_site():
    # Create a dummy site for top-level locations if it doesn't exist
    site_data = {
        "name": "Synthetic Data Root Site",
        "slug": "synthetic-root-site",
        "status": "active",
        "description": "Dummy site for synthetic hierarchical locations"
    }
    site = get_or_create("dcim/sites/", ["slug"], site_data)
    if not site:
        raise Exception("Could not create or fetch dummy Site for top-level Locations.")
    return site["id"]

def ensure_device_infrastructure():
    """Create manufacturers, device types, device roles, and statuses needed for devices."""
    
    # Create manufacturers
    manufacturers = {
        "cisco": {"name": "Cisco", "slug": "cisco"},
        "arista": {"name": "Arista Networks", "slug": "arista"},
    }
    
    manufacturer_objs = {}
    for slug, data in manufacturers.items():
        obj = get_or_create("dcim/manufacturers/", ["slug"], data)
        if obj:
            manufacturer_objs[slug] = obj
        else:
            print(f"Failed to create manufacturer: {data['name']}")
    
    # Create device roles based on function codes
    device_roles = {
        "acc": {"name": "Campus Access Switch", "slug": "acc", "color": "4caf50"},
        "cor": {"name": "Campus Core Switch", "slug": "cor", "color": "2196f3"},
        "wan": {"name": "Campus WAN Switch", "slug": "wan", "color": "ff9800"},
        "lea": {"name": "Data Center Leaf Switch", "slug": "lea", "color": "9c27b0"},
        "spn": {"name": "Data Center Spine Switch", "slug": "spn", "color": "f44336"},
        "fw": {"name": "Firewall", "slug": "fw", "color": "e91e63"},
        "lb": {"name": "Load Balancer", "slug": "lb", "color": "673ab7"},
    }
    
    role_objs = {}
    for slug, data in device_roles.items():
        obj = get_or_create("dcim/device-roles/", ["slug"], data)
        if obj:
            role_objs[slug] = obj
        else:
            print(f"Failed to create device role: {data['name']}")
    
    # Create device types with model numbers
    device_types = {
        # Cisco Campus (all campus devices)
        "catalyst-9300": {
            "manufacturer": manufacturer_objs.get("cisco", {}).get("id"),
            "model": "Catalyst 9300",
            "slug": "catalyst-9300",
            "part_number": "C9300-48UXM",
            "u_height": 1,
            "is_full_depth": False,
        },
        "catalyst-9500": {
            "manufacturer": manufacturer_objs.get("cisco", {}).get("id"),
            "model": "Catalyst 9500",
            "slug": "catalyst-9500",
            "part_number": "C9500-48Y4C",
            "u_height": 1,
            "is_full_depth": True,
        },
        "asr-1000": {
            "manufacturer": manufacturer_objs.get("cisco", {}).get("id"),
            "model": "ASR 1000",
            "slug": "asr-1000",
            "part_number": "ASR1001-X",
            "u_height": 1,
            "is_full_depth": True,
        },
        # Data Center - Mix of Cisco and Arista
        "nexus-9000": {
            "manufacturer": manufacturer_objs.get("cisco", {}).get("id"),
            "model": "Nexus 9000",
            "slug": "nexus-9000",
            "part_number": "N9K-C93180YC-EX",
            "u_height": 1,
            "is_full_depth": True,
        },
        "arista-7280": {
            "manufacturer": manufacturer_objs.get("arista", {}).get("id"),
            "model": "7280SR",
            "slug": "arista-7280",
            "part_number": "DCS-7280SR4K-48C6",
            "u_height": 1,
            "is_full_depth": True,
        },
        "arista-7508": {
            "manufacturer": manufacturer_objs.get("arista", {}).get("id"),
            "model": "7508",
            "slug": "arista-7508",
            "part_number": "DCS-7508",
            "u_height": 8,
            "is_full_depth": True,
        },
    }
    
    device_type_objs = {}
    for slug, data in device_types.items():
        if data.get("manufacturer"):  # Only create if manufacturer exists
            obj = get_or_create("dcim/device-types/", ["slug"], data)
            if obj:
                device_type_objs[slug] = obj
            else:
                print(f"Failed to create device type: {data['model']}")
    
    return manufacturer_objs, role_objs, device_type_objs

def create_hierarchical_locations():
    # Ensure location types exist and get their IDs
    type_map = ensure_location_types()
    region_type = type_map.get("geo-region")
    country_type = type_map.get("country")
    site_type = type_map.get("campus")
    if not (region_type and country_type and site_type):
        print("Could not find or create required location types: geo-region, country, campus.")
        return {}, {}, {}
    # Ensure dummy site exists
    dummy_site_id = ensure_dummy_site()
    
    # Define 32 locations with 4-character codes
    locations_data = {
        "NAM": {
            "US": [
                {"name": "South West Data Center", "code": "SWDC"},
                {"name": "North East Data Center", "code": "NEDC"},
                {"name": "Central Data Center", "code": "CTDC"},
                {"name": "West Coast Campus", "code": "WCCP"},
                {"name": "East Coast Campus", "code": "ECCP"},
                {"name": "Midwest Campus", "code": "MWCP"},
                {"name": "Texas Campus", "code": "TXCP"},
                {"name": "Florida Campus", "code": "FLCP"},
                {"name": "California Campus", "code": "CACP"},
                {"name": "New York Campus", "code": "NYCP"},
            ],
            "CA": [
                {"name": "Toronto Data Center", "code": "TRDC"},
                {"name": "Vancouver Campus", "code": "VCCP"},
                {"name": "Montreal Campus", "code": "MCCP"},
            ],
            "MX": [
                {"name": "Mexico City Data Center", "code": "MXDC"},
                {"name": "Guadalajara Campus", "code": "GJCP"},
                {"name": "Monterrey Campus", "code": "MTCP"},
            ],
        },
        "ASPAC": {
            "SG": [
                {"name": "Singapore Data Center", "code": "SGDC"},
                {"name": "Singapore Campus", "code": "SGCP"},
            ],
            "JP": [
                {"name": "Tokyo Data Center", "code": "TKDC"},
                {"name": "Tokyo Campus", "code": "TKCP"},
            ],
            "AU": [
                {"name": "Sydney Data Center", "code": "SYDC"},
                {"name": "Melbourne Campus", "code": "MLCP"},
            ],
            "HK": [
                {"name": "Hong Kong Data Center", "code": "HKDC"},
                {"name": "Hong Kong Campus", "code": "HKCP"},
            ],
            "KR": [
                {"name": "Seoul Data Center", "code": "SLDC"},
                {"name": "Seoul Campus", "code": "SLCP"},
            ],
            "IN": [
                {"name": "Mumbai Data Center", "code": "MBDC"},
                {"name": "Bangalore Campus", "code": "BLCP"},
            ],
        },
        "EMEA": {
            "GB": [
                {"name": "London Data Center", "code": "LNDC"},
                {"name": "London Campus", "code": "LNCP"},
            ],
            "DE": [
                {"name": "Frankfurt Data Center", "code": "FRDC"},
                {"name": "Berlin Campus", "code": "BLCP"},
            ],
            "FR": [
                {"name": "Paris Data Center", "code": "PRDC"},
                {"name": "Paris Campus", "code": "PRCP"},
            ],
            "NL": [
                {"name": "Amsterdam Data Center", "code": "AMDC"},
                {"name": "Amsterdam Campus", "code": "AMCP"},
            ],
            "AE": [
                {"name": "Dubai Data Center", "code": "DUDC"},
                {"name": "Dubai Campus", "code": "DUCP"},
            ],
            "CH": [
                {"name": "Zurich Data Center", "code": "ZHDC"},
                {"name": "Zurich Campus", "code": "ZHCP"},
            ],
        },
    }
    
    country_names = {
        "US": "United States", "CA": "Canada", "MX": "Mexico", "SG": "Singapore", "JP": "Japan", "AU": "Australia", "HK": "Hong Kong", "KR": "South Korea", "IN": "India", "GB": "United Kingdom", "DE": "Germany", "FR": "France", "NL": "Netherlands", "AE": "United Arab Emirates", "CH": "Switzerland"
    }
    
    region_objs, country_objs, location_objs = {}, {}, {}
    
    # Regions
    for region in locations_data:
        region_data = {"name": region, "slug": region.lower(), "description": f"{region} region", "status": "active", "location_type": region_type, "site": dummy_site_id}
        region_obj = get_or_create("dcim/locations/", ["name"], region_data)
        if region_obj:
            region_objs[region] = region_obj
        else:
            print(f"Failed to create region: {region}")
            continue
    
    # Countries
    for region, countries in locations_data.items():
        if region not in region_objs:
            continue
        for country_code in countries:
            country_name = country_names[country_code]
            country_data = {"name": country_name, "slug": country_code.lower(), "parent": region_objs[region]["id"], "description": f"{country_name} in {region} region", "status": "active", "location_type": country_type}
            country_obj = get_or_create("dcim/locations/", ["name", "parent"], country_data)
            if country_obj:
                country_objs[country_code] = country_obj
            else:
                print(f"Failed to create country: {country_name}")
                continue
    
    # Locations
    for region, countries in locations_data.items():
        for country_code, locs in countries.items():
            if country_code not in country_objs:
                continue
            for loc in locs:
                slug = loc["name"].lower().replace(" ", "-")
                loc_data = {"name": loc["name"], "slug": slug, "parent": country_objs[country_code]["id"], "description": f"{loc['name']} in {country_names[country_code]}", "status": "active", "location_type": site_type}
                loc_obj = get_or_create("dcim/locations/", ["name", "parent"], loc_data)
                if loc_obj:
                    location_objs[loc["code"]] = loc_obj
                else:
                    print(f"Failed to create location: {loc['name']}")
    
    return region_objs, country_objs, location_objs

def create_devices(location_objs, role_objs, device_type_objs):
    """Create 1000 devices across locations following the naming standard."""
    
    # Get the dummy site ID
    dummy_site_id = ensure_dummy_site()
    
    # Device type mapping (1 character)
    device_types = {
        "s": "switch",
        "r": "router", 
        "f": "firewall",
        "l": "load-balancer"
    }
    
    # Function codes and their device types
    function_configs = {
        "acc": {"type": "s", "role": "acc", "device_type": "catalyst-9300", "model": "9300", "count_per_location": 8},
        "cor": {"type": "s", "role": "cor", "device_type": "catalyst-9500", "model": "9500", "count_per_location": 2},
        "wan": {"type": "r", "role": "wan", "device_type": "asr-1000", "model": "1000", "count_per_location": 2},
        "lea": {"type": "s", "role": "lea", "device_type": "nexus-9000", "model": "9000", "count_per_location": 12},
        "spn": {"type": "s", "role": "spn", "device_type": "arista-7508", "model": "7508", "count_per_location": 4},
        "fw": {"type": "f", "role": "fw", "device_type": "nexus-9000", "model": "9000", "count_per_location": 2},
        "lb": {"type": "l", "role": "lb", "device_type": "nexus-9000", "model": "9000", "count_per_location": 2},
    }
    
    # Location to country code mapping
    location_country_map = {
        # US locations
        "SWDC": "us", "NEDC": "us", "CTDC": "us", "WCCP": "us", "ECCP": "us", "MWCP": "us", "TXCP": "us", "FLCP": "us", "CACP": "us", "NYCP": "us",
        # CA locations  
        "TRDC": "ca", "VCCP": "ca", "MCCP": "ca",
        # MX locations
        "MXDC": "mx", "GJCP": "mx", "MTCP": "mx",
        # SG locations
        "SGDC": "sg", "SGCP": "sg",
        # JP locations
        "TKDC": "jp", "TKCP": "jp",
        # AU locations
        "SYDC": "au", "MLCP": "au",
        # HK locations
        "HKDC": "hk", "HKCP": "hk",
        # KR locations
        "SLDC": "kr", "SLCP": "kr",
        # IN locations
        "MBDC": "in", "BLCP": "in",
        # GB locations
        "LNDC": "gb", "LNCP": "gb",
        # DE locations
        "FRDC": "de", "BLCP": "de",
        # FR locations
        "PRDC": "fr", "PRCP": "fr",
        # NL locations
        "AMDC": "nl", "AMCP": "nl",
        # AE locations
        "DUDC": "ae", "DUCP": "ae",
        # CH locations
        "ZHDC": "ch", "ZHCP": "ch",
    }
    
    devices_created = 0
    
    for location_code, location_obj in location_objs.items():
        country_code = location_country_map.get(location_code, "us")
        is_datacenter = "Data Center" in location_obj["name"]
        
        # Determine which functions to create based on location type
        if is_datacenter:
            functions = ["lea", "spn", "fw", "lb"]  # Data center functions
        else:
            functions = ["acc", "cor", "wan"]  # Campus functions
        
        for function_code in functions:
            config = function_configs[function_code]
            count = config["count_per_location"]
            
            for i in range(1, count + 1):
                # Generate device number: 1xxx for campus, 1xxx for data center fabric 1
                device_num = f"1{i:03d}"  # 1001, 1002, etc.
                
                # Create device name following the standard
                device_name = f"{config['type']}{country_code}{location_code.lower()}-{function_code}{device_num}-{config['model']}"
                
                # Determine device type based on function and location
                if is_datacenter and function_code in ["lea", "spn"]:
                    # Mix of Cisco and Arista for data center
                    if function_code == "lea":
                        device_type_id = device_type_objs.get("nexus-9000", {}).get("id")
                    else:  # spn
                        device_type_id = device_type_objs.get("arista-7508", {}).get("id")
                else:
                    # All Cisco for campus
                    device_type_id = device_type_objs.get(config["device_type"], {}).get("id")
                
                if not device_type_id:
                    print(f"Missing device type for {config['device_type']}")
                    continue
                
                device_data = {
                    "name": device_name,
                    "device_type": device_type_id,
                    "device_role": role_objs.get(function_code, {}).get("id"),
                    "location": location_obj["id"],
                    "site": dummy_site_id,
                    "status": "active",
                }
                
                device = api_post("dcim/devices/", device_data)
                if device:
                    devices_created += 1
                    if devices_created % 100 == 0:
                        print(f"Created {devices_created} devices...")
                else:
                    print(f"Failed to create device: {device_name}")
    
    print(f"Total devices created: {devices_created}")
    return devices_created

def create_dynamic_groups():
    """Create Dynamic Groups based on device roles, locations, and manufacturers."""
    
    # Get existing data to reference
    roles = api_get("dcim/device-roles/")
    locations = api_get("dcim/locations/")
    manufacturers = api_get("dcim/manufacturers/")
    
    if not all([roles, locations, manufacturers]):
        print("Failed to fetch existing data for Dynamic Groups")
        return {}
    
    # Create Dynamic Groups based on device roles
    role_groups = {}
    for role in roles.get('results', []):
        group_name = f"All {role['name']} Devices"
        group_data = {
            "name": group_name,
            "slug": f"all-{role['slug']}-devices",
            "description": f"All devices with role: {role['name']}",
            "content_type": "dcim.device",
            "filter": {
                "role": [role['slug']]  # Use slug instead of ID
            }
        }
        
        group = get_or_create("extras/dynamic-groups/", ["slug"], group_data)
        if group:
            role_groups[role['slug']] = group
            print(f"Created Dynamic Group: {group_name}")
        else:
            print(f"Failed to create Dynamic Group for role: {role['name']}")
    
    # Create Dynamic Groups based on locations (top-level regions)
    location_groups = {}
    for location in locations.get('results', []):
        if location.get('location_type') and 'geo-region' in location.get('location_type', {}).get('slug', ''):
            group_name = f"All Devices in {location['name']}"
            group_data = {
                "name": group_name,
                "slug": f"all-devices-{location['slug']}",
                "description": f"All devices in region: {location['name']}",
                "content_type": "dcim.device",
                "filter": {
                    "location": [location['slug']]  # Use slug instead of ID
                }
            }
            
            group = get_or_create("extras/dynamic-groups/", ["slug"], group_data)
            if group:
                location_groups[location['slug']] = group
                print(f"Created Dynamic Group: {group_name}")
            else:
                print(f"Failed to create Dynamic Group for location: {location['name']}")
    
    # Create Dynamic Groups based on manufacturers
    manufacturer_groups = {}
    for manufacturer in manufacturers.get('results', []):
        group_name = f"All {manufacturer['name']} Devices"
        group_data = {
            "name": group_name,
            "slug": f"all-{manufacturer['slug']}-devices",
            "description": f"All devices from manufacturer: {manufacturer['name']}",
            "content_type": "dcim.device",
            "filter": {
                "manufacturer": [manufacturer['slug']]  # Use slug instead of ID
            }
        }
        
        group = get_or_create("extras/dynamic-groups/", ["slug"], group_data)
        if group:
            manufacturer_groups[manufacturer['slug']] = group
            print(f"Created Dynamic Group: {group_name}")
        else:
            print(f"Failed to create Dynamic Group for manufacturer: {manufacturer['name']}")
    
    return {
        'role_groups': role_groups,
        'location_groups': location_groups,
        'manufacturer_groups': manufacturer_groups
    }

def create_servicenow_groups(dynamic_groups):
    """Create ServiceNow Groups that reference Dynamic Groups."""
    
    # Create ServiceNow Groups for different scenarios
    servicenow_groups = []
    
    # 1. Network Operations Team - manages all campus devices
    campus_roles = ['acc', 'cor', 'wan']
    campus_dynamic_groups = [dynamic_groups['role_groups'].get(role) for role in campus_roles if dynamic_groups['role_groups'].get(role)]
    
    if campus_dynamic_groups:
        netops_group = {
            "name": "Network Operations Team",
            "description": "ServiceNow group for Network Operations team managing campus infrastructure",
            "dynamic_groups": [group['id'] for group in campus_dynamic_groups if group]
        }
        
        group = api_post("plugins/service_now_groups/groups/", netops_group)
        if group:
            servicenow_groups.append(group)
            print(f"Created ServiceNow Group: {netops_group['name']}")
        else:
            print(f"Failed to create ServiceNow Group: {netops_group['name']}")
    
    # 2. Data Center Team - manages all data center devices
    dc_roles = ['lea', 'spn']
    dc_dynamic_groups = [dynamic_groups['role_groups'].get(role) for role in dc_roles if dynamic_groups['role_groups'].get(role)]
    
    if dc_dynamic_groups:
        dc_group = {
            "name": "Data Center Operations Team",
            "description": "ServiceNow group for Data Center Operations team managing DC infrastructure",
            "dynamic_groups": [group['id'] for group in dc_dynamic_groups if group]
        }
        
        group = api_post("plugins/service_now_groups/groups/", dc_group)
        if group:
            servicenow_groups.append(group)
            print(f"Created ServiceNow Group: {dc_group['name']}")
        else:
            print(f"Failed to create ServiceNow Group: {dc_group['name']}")
    
    # 3. Security Team - manages all security devices
    security_roles = ['fw', 'lb']
    security_dynamic_groups = [dynamic_groups['role_groups'].get(role) for role in security_roles if dynamic_groups['role_groups'].get(role)]
    
    if security_dynamic_groups:
        security_group = {
            "name": "Security Operations Team",
            "description": "ServiceNow group for Security Operations team managing security infrastructure",
            "dynamic_groups": [group['id'] for group in security_dynamic_groups if group]
        }
        
        group = api_post("plugins/service_now_groups/groups/", security_group)
        if group:
            servicenow_groups.append(group)
            print(f"Created ServiceNow Group: {security_group['name']}")
        else:
            print(f"Failed to create ServiceNow Group: {security_group['name']}")
    
    # 4. Regional Teams - one for each major region
    for region_slug, region_group in dynamic_groups['location_groups'].items():
        if region_slug in ['na', 'eu', 'ap']:  # North America, Europe, Asia Pacific
            region_name = region_group['name'].replace('All Devices in ', '')
            regional_group = {
                "name": f"{region_name} Regional Team",
                "description": f"ServiceNow group for {region_name} regional operations",
                "dynamic_groups": [region_group['id']]
            }
            
            group = api_post("plugins/service_now_groups/groups/", regional_group)
            if group:
                servicenow_groups.append(group)
                print(f"Created ServiceNow Group: {regional_group['name']}")
            else:
                print(f"Failed to create ServiceNow Group: {regional_group['name']}")
    
    # 5. Vendor-specific teams
    for vendor_slug, vendor_group in dynamic_groups['manufacturer_groups'].items():
        vendor_name = vendor_group['name'].replace('All ', '').replace(' Devices', '')
        vendor_team = {
            "name": f"{vendor_name} Support Team",
            "description": f"ServiceNow group for {vendor_name} device support and maintenance",
            "dynamic_groups": [vendor_group['id']]
        }
        
        group = api_post("plugins/service_now_groups/groups/", vendor_team)
        if group:
            servicenow_groups.append(group)
            print(f"Created ServiceNow Group: {vendor_team['name']}")
        else:
            print(f"Failed to create ServiceNow Group: {vendor_team['name']}")
    
    return servicenow_groups

def test_servicenow_groups_functionality():
    """Test the ServiceNow Groups app functionality."""
    
    print("\n=== Testing ServiceNow Groups Functionality ===")
    
    # 1. Test API endpoints
    print("\n1. Testing API endpoints...")
    
    # List all ServiceNow Groups
    groups = api_get("plugins/service_now_groups/groups/")
    if groups:
        print(f"✓ Found {groups.get('count', 0)} ServiceNow Groups")
        for group in groups.get('results', [])[:3]:  # Show first 3
            print(f"  - {group['name']}: {group.get('description', 'No description')}")
    else:
        print("✗ Failed to fetch ServiceNow Groups")
    
    # 2. Test device association
    print("\n2. Testing device association...")
    
    # Get a few devices to test with
    devices = api_get("dcim/devices/", {"limit": 5})
    if devices and devices.get('results'):
        test_device = devices['results'][0]
        print(f"✓ Testing with device: {test_device['name']}")
        
        # Get ServiceNow Groups for this device
        device_groups = api_get(f"plugins/service_now_groups/groups/", {"device": test_device['id']})
        if device_groups:
            print(f"✓ Device {test_device['name']} is associated with {device_groups.get('count', 0)} ServiceNow Groups")
            for group in device_groups.get('results', [])[:3]:
                print(f"  - {group['name']}")
        else:
            print(f"✗ Failed to get ServiceNow Groups for device {test_device['name']}")
    else:
        print("✗ No devices found for testing")
    
    # 3. Test Dynamic Group association
    print("\n3. Testing Dynamic Group association...")
    
    dynamic_groups = api_get("extras/dynamic-groups/")
    if dynamic_groups:
        print(f"✓ Found {dynamic_groups.get('count', 0)} Dynamic Groups")
        for group in dynamic_groups.get('results', [])[:3]:
            print(f"  - {group['name']}: {group.get('description', 'No description')}")
    else:
        print("✗ Failed to fetch Dynamic Groups")
    
    print("\n=== Testing Complete ===")

if __name__ == "__main__":
    print("=== ServiceNow Groups Synthetic Data Generation ===")
    
    # Step 1: Create infrastructure (manufacturers, device types, roles)
    print("\n1. Creating device infrastructure...")
    manufacturer_objs, role_objs, device_type_objs = ensure_device_infrastructure()
    
    # Step 2: Create hierarchical locations
    print("\n2. Creating hierarchical locations...")
    regions, countries, sites = create_hierarchical_locations()
    
    # Step 3: Create devices
    print("\n3. Creating devices...")
    devices = create_devices(sites, role_objs, device_type_objs)
    
    # Step 4: Create Dynamic Groups
    print("\n4. Creating Dynamic Groups...")
    dynamic_groups = create_dynamic_groups()
    
    # Step 5: Create ServiceNow Groups
    print("\n5. Creating ServiceNow Groups...")
    servicenow_groups = create_servicenow_groups(dynamic_groups)
    
    # Step 6: Test functionality
    print("\n6. Testing ServiceNow Groups functionality...")
    test_servicenow_groups_functionality()
    
    print("\n=== Synthetic Data Generation Complete ===")
    print(f"Created {len(regions)} regions, {len(countries)} countries, {len(sites)} sites")
    print(f"Created {devices} devices")
    print(f"Created {sum(len(groups) for groups in dynamic_groups.values())} Dynamic Groups")
    print(f"Created {len(servicenow_groups)} ServiceNow Groups") 