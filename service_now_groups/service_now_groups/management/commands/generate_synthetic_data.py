from django.core.management.base import BaseCommand
from django.db import transaction

from nautobot.dcim.models import Location, Device, DeviceType, Manufacturer, Site
from nautobot.extras.models import DynamicGroup
from service_now_groups.models import ServiceNowGroup

# --- Begin helper functions copied from scripts/generate_synthetic_data.py ---

def create_locations():
    """Create hierarchical locations: Regions -> Countries -> Individual Locations."""
    # ... (copy full function from script)

def create_manufacturers():
    """Create manufacturers."""
    # ... (copy full function from script)

def create_device_types(manufacturers):
    """Create device types."""
    # ... (copy full function from script)

def create_sites(locations):
    """Create sites."""
    # ... (copy full function from script)

def create_devices(locations, device_types, sites):
    """Create devices."""
    # ... (copy full function from script)

def create_dynamic_groups():
    """Create dynamic groups."""
    # ... (copy full function from script)

def create_service_now_groups(locations, dynamic_groups):
    """Create ServiceNow groups."""
    # ... (copy full function from script)

# --- End helper functions ---

# For brevity, only the main() logic is shown here. The actual implementation will copy all helper functions as in the script.

class Command(BaseCommand):
    help = "Generate synthetic data for ServiceNow Groups app."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting synthetic data generation..."))
        with transaction.atomic():
            self.stdout.write("\n1. Creating locations...")
            locations = create_locations()
            self.stdout.write("\n2. Creating manufacturers...")
            manufacturers = create_manufacturers()
            self.stdout.write("\n3. Creating device types...")
            device_types = create_device_types(manufacturers)
            self.stdout.write("\n4. Creating sites...")
            sites = create_sites(locations)
            self.stdout.write("\n5. Creating devices...")
            devices = create_devices(locations, device_types, sites)
            self.stdout.write("\n6. Creating dynamic groups...")
            dynamic_groups = create_dynamic_groups()
            self.stdout.write("\n7. Creating ServiceNow groups...")
            service_now_groups = create_service_now_groups(locations, dynamic_groups)
        self.stdout.write(self.style.SUCCESS(f"\nSynthetic data generation complete!"))
        self.stdout.write(self.style.SUCCESS(f"- Created {len(locations)} locations"))
        self.stdout.write(self.style.SUCCESS(f"- Created {len(devices)} devices"))
        self.stdout.write(self.style.SUCCESS(f"- Created {len(dynamic_groups)} dynamic groups"))
        self.stdout.write(self.style.SUCCESS(f"- Created {len(service_now_groups)} ServiceNow groups")) 