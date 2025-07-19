"""Shared test fixtures for ServiceNow Groups app."""

import pytest
from django.contrib.auth import get_user_model
from nautobot.dcim.models import Device, Location, DeviceRole, DeviceType, Manufacturer, Status
from nautobot.extras.models import DynamicGroup

from service_now_groups.models import ServiceNowGroup

User = get_user_model()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username="testuser",
        password="testpass123"
    )


@pytest.fixture
def location():
    """Create a test location."""
    return Location.objects.create(
        name="Test Location",
        slug="test-location"
    )


@pytest.fixture
def device_role():
    """Create a test device role."""
    return DeviceRole.objects.create(
        name="Test Role",
        slug="test-role"
    )


@pytest.fixture
def manufacturer():
    """Create a test manufacturer."""
    return Manufacturer.objects.create(
        name="Test Manufacturer",
        slug="test-manufacturer"
    )


@pytest.fixture
def device_type(manufacturer):
    """Create a test device type."""
    return DeviceType.objects.create(
        manufacturer=manufacturer,
        model="Test Model",
        slug="test-model"
    )


@pytest.fixture
def status():
    """Get the active status."""
    return Status.objects.get(slug="active")


@pytest.fixture
def device(location, device_type, device_role, status):
    """Create a test device."""
    return Device.objects.create(
        name="Test Device",
        device_type=device_type,
        device_role=device_role,
        location=location,
        status=status
    )


@pytest.fixture
def dynamic_group(location):
    """Create a test dynamic group."""
    return DynamicGroup.objects.create(
        name="Test Dynamic Group",
        slug="test-dynamic-group",
        content_type_id=Device._meta.pk,
        filter={"location": [location.pk]}
    )


@pytest.fixture
def service_now_group():
    """Create a test ServiceNow group."""
    return ServiceNowGroup.objects.create(
        name="Test ServiceNow Group",
        description="Test description"
    )


@pytest.fixture
def service_now_group_with_location(service_now_group, location):
    """Create a test ServiceNow group with location assignment."""
    service_now_group.locations.add(location)
    return service_now_group


@pytest.fixture
def service_now_group_with_device(service_now_group, device):
    """Create a test ServiceNow group with device assignment."""
    service_now_group.devices.add(device)
    return service_now_group


@pytest.fixture
def service_now_group_with_dynamic_group(service_now_group, dynamic_group):
    """Create a test ServiceNow group with dynamic group assignment."""
    service_now_group.dynamic_groups.add(dynamic_group)
    return service_now_group


@pytest.fixture
def complex_service_now_group(service_now_group, location, device, dynamic_group):
    """Create a test ServiceNow group with multiple assignment methods."""
    service_now_group.locations.add(location)
    service_now_group.devices.add(device)
    service_now_group.dynamic_groups.add(dynamic_group)
    return service_now_group 