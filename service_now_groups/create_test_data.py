#!/usr/bin/env python3
"""
Simple script to create test data for ServiceNow Groups plugin testing.
This script creates basic test devices and ServiceNow Groups.
"""

import os
import sys
import django

# Add /app to sys.path so Django can find nautobot_config.py
sys.path.insert(0, '/app')
# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nautobot_config')
django.setup()

from django.contrib.auth import get_user_model
from nautobot.dcim.models import Device, DeviceType, DeviceRole, Location, LocationType, Manufacturer
from nautobot.extras.models import DynamicGroup
from service_now_groups.models import ServiceNowGroup

User = get_user_model()

def create_test_data():
    """Create test data for ServiceNow Groups testing."""
    print("Creating test data for ServiceNow Groups plugin...")
    
    # Create or get admin user
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("Created admin user")
    
    # Create location types if they don't exist
    region_type, created = LocationType.objects.get_or_create(
        name="Region",
        defaults={'description': 'Geographic region'}
    )
    if created:
        print("Created Region location type")
    
    site_type, created = LocationType.objects.get_or_create(
        name="Site",
        defaults={'description': 'Physical site'}
    )
    if created:
        print("Created Site location type")
    
    # Create locations
    region1, created = Location.objects.get_or_create(
        name="North America",
        location_type=region_type,
        defaults={'description': 'North American region'}
    )
    if created:
        print("Created North America region")
    
    site1, created = Location.objects.get_or_create(
        name="New York DC",
        location_type=site_type,
        parent=region1,
        defaults={'description': 'New York Data Center'}
    )
    if created:
        print("Created New York DC site")
    
    site2, created = Location.objects.get_or_create(
        name="Los Angeles DC",
        location_type=site_type,
        parent=region1,
        defaults={'description': 'Los Angeles Data Center'}
    )
    if created:
        print("Created Los Angeles DC site")
    
    # Create manufacturer
    cisco, created = Manufacturer.objects.get_or_create(
        name="Cisco Systems",
        defaults={'description': 'Cisco Systems, Inc.'}
    )
    if created:
        print("Created Cisco manufacturer")
    
    # Create device type
    device_type, created = DeviceType.objects.get_or_create(
        model="C9300-48P",
        manufacturer=cisco,
        defaults={'part_number': 'C9300-48P'}
    )
    if created:
        print("Created C9300-48P device type")
    
    # Create device role
    switch_role, created = DeviceRole.objects.get_or_create(
        name="Access Switch",
        defaults={'color': 'ff0000', 'description': 'Access layer switch'}
    )
    if created:
        print("Created Access Switch role")
    
    # Create test devices
    devices = []
    for i in range(1, 6):
        device_name = f"test-switch-{i:02d}"
        location = site1 if i % 2 == 0 else site2
        
        device, created = Device.objects.get_or_create(
            name=device_name,
            defaults={
                'device_type': device_type,
                'device_role': switch_role,
                'location': location,
                'status': 'active'
            }
        )
        if created:
            print(f"Created device: {device_name}")
        devices.append(device)
    
    # Create dynamic group
    dynamic_group, created = DynamicGroup.objects.get_or_create(
        name="All Access Switches",
        defaults={
            'description': 'All access switches in the network',
            'content_type': Device._meta.get_content_type()
        }
    )
    if created:
        print("Created dynamic group: All Access Switches")
    
    # Create ServiceNow Groups
    groups = []
    
    # Group 1: Location-based
    group1, created = ServiceNowGroup.objects.get_or_create(
        name="NYC Network Team",
        defaults={
            'description': 'ServiceNow group for NYC network team'
        }
    )
    if created:
        group1.locations.add(site1)
        print("Created ServiceNow Group: NYC Network Team")
    groups.append(group1)
    
    # Group 2: Device-based
    group2, created = ServiceNowGroup.objects.get_or_create(
        name="Critical Infrastructure",
        defaults={
            'description': 'ServiceNow group for critical infrastructure devices'
        }
    )
    if created:
        group2.devices.add(devices[0], devices[1])
        print("Created ServiceNow Group: Critical Infrastructure")
    groups.append(group2)
    
    # Group 3: Dynamic group-based
    group3, created = ServiceNowGroup.objects.get_or_create(
        name="All Switches",
        defaults={
            'description': 'ServiceNow group for all switches via dynamic group'
        }
    )
    if created:
        group3.dynamic_groups.add(dynamic_group)
        print("Created ServiceNow Group: All Switches")
    groups.append(group3)
    
    print(f"\nTest data creation complete!")
    print(f"Created {len(devices)} devices")
    print(f"Created {len(groups)} ServiceNow Groups")
    print(f"Devices: {[d.name for d in devices]}")
    print(f"Groups: {[g.name for g in groups]}")
    
    return devices, groups

if __name__ == "__main__":
    create_test_data() 