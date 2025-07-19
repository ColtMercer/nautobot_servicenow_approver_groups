from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from nautobot.dcim.models import Device, DeviceType, DeviceRole, Location, LocationType, Manufacturer, Site
from nautobot.extras.models import DynamicGroup, Status
from service_now_groups.models import ServiceNowGroup

User = get_user_model()

class Command(BaseCommand):
    help = "Create test data for ServiceNow Groups plugin."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Creating test data for ServiceNow Groups plugin..."))

        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            username='admin', defaults={'email': 'admin@example.com'}
        )
        if created:
            admin_user.set_password('admin')
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user"))

        # Create location types
        region_type, _ = LocationType.objects.get_or_create(
            name="Region", defaults={'description': 'Geographic region'}
        )
        site_type, _ = LocationType.objects.get_or_create(
            name="Site", defaults={'description': 'Physical site'}
        )

        # Create locations
        region1, _ = Location.objects.get_or_create(
            name="North America", location_type=region_type, defaults={'description': 'North American region'}
        )
        site1, _ = Location.objects.get_or_create(
            name="New York DC", location_type=site_type, parent=region1, defaults={'description': 'New York Data Center'}
        )
        site2, _ = Location.objects.get_or_create(
            name="Los Angeles DC", location_type=site_type, parent=region1, defaults={'description': 'Los Angeles Data Center'}
        )

        # Create manufacturer
        cisco, _ = Manufacturer.objects.get_or_create(
            name="Cisco Systems", defaults={'description': 'Cisco Systems, Inc.'}
        )

        # Create device type
        device_type, _ = DeviceType.objects.get_or_create(
            model="C9300-48P", manufacturer=cisco, defaults={'part_number': 'C9300-48P'}
        )

        # Create device role
        switch_role, _ = DeviceRole.objects.get_or_create(
            name="Access Switch", defaults={'color': 'ff0000', 'description': 'Access layer switch'}
        )

        # Create or get "Active" status
        active_status, _ = Status.objects.get_or_create(
            name="Active",
            defaults={"slug": "active", "color": "#28a745", "description": "Active status"}
        )

        # Create a site (required for Device)
        site, _ = Site.objects.get_or_create(
            name="Test Site",
            defaults={"slug": "test-site", "status": active_status}
        )

        # Create test devices
        devices = []
        for i in range(1, 6):
            device_name = f"test-switch-{i:02d}"
            location = site1 if i % 2 == 0 else site2
            device, _ = Device.objects.get_or_create(
                name=device_name,
                defaults={
                    'device_type': device_type,
                    'device_role': switch_role,
                    'location': location,
                    'site': site,
                    'status': active_status
                }
            )
            devices.append(device)

        # Create dynamic group
        device_content_type = ContentType.objects.get_for_model(Device)
        dynamic_group, _ = DynamicGroup.objects.get_or_create(
            name="All Access Switches",
            defaults={
                'description': 'All access switches in the network',
                'content_type': device_content_type
            }
        )

        # Create ServiceNow Groups
        groups = []
        group1, created = ServiceNowGroup.objects.get_or_create(
            name="NYC Network Team",
            defaults={'description': 'ServiceNow group for NYC network team'}
        )
        if created:
            group1.locations.add(site1)
        groups.append(group1)

        group2, created = ServiceNowGroup.objects.get_or_create(
            name="Critical Infrastructure",
            defaults={'description': 'ServiceNow group for critical infrastructure devices'}
        )
        if created:
            group2.devices.add(devices[0], devices[1])
        groups.append(group2)

        group3, created = ServiceNowGroup.objects.get_or_create(
            name="All Switches",
            defaults={'description': 'ServiceNow group for all switches via dynamic group'}
        )
        if created:
            group3.dynamic_groups.add(dynamic_group)
        groups.append(group3)

        self.stdout.write(self.style.SUCCESS(f"Test data creation complete!"))
        self.stdout.write(self.style.SUCCESS(f"Created {len(devices)} devices"))
        self.stdout.write(self.style.SUCCESS(f"Created {len(groups)} ServiceNow Groups"))
        self.stdout.write(self.style.SUCCESS(f"Devices: {[d.name for d in devices]}"))
        self.stdout.write(self.style.SUCCESS(f"Groups: {[g.name for g in groups]}")) 