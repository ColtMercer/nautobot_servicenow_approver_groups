"""Tests for the ServiceNow Groups API."""

import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from nautobot.dcim.models import Device, Location, DeviceRole, DeviceType, Manufacturer, Status
from nautobot.extras.models import DynamicGroup

from service_now_groups.models import ServiceNowGroup

User = get_user_model()


class ServiceNowGroupAPITestCase(TestCase):
    """Test cases for ServiceNowGroup API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        # Create test locations
        self.location1 = Location.objects.create(name="Test Location 1", slug="test-location-1")
        self.location2 = Location.objects.create(name="Test Location 2", slug="test-location-2")
        
        # Create test device components
        self.device_role = DeviceRole.objects.create(name="Test Role", slug="test-role")
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer", slug="test-manufacturer")
        self.device_type = DeviceType.objects.create(
            manufacturer=self.manufacturer,
            model="Test Model",
            slug="test-model"
        )
        self.status = Status.objects.get(slug="active")
        
        # Create test devices
        self.device1 = Device.objects.create(
            name="Test Device 1",
            device_type=self.device_type,
            device_role=self.device_role,
            location=self.location1,
            status=self.status
        )
        self.device2 = Device.objects.create(
            name="Test Device 2",
            device_type=self.device_type,
            device_role=self.device_role,
            location=self.location2,
            status=self.status
        )
        
        # Create test dynamic group
        self.dynamic_group = DynamicGroup.objects.create(
            name="Test Dynamic Group",
            slug="test-dynamic-group",
            content_type_id=Device._meta.pk,
            filter={"location": [self.location1.pk]}
        )
        
        # Create test ServiceNow group
        self.service_now_group = ServiceNowGroup.objects.create(
            name="Test ServiceNow Group",
            description="Test description"
        )
        self.service_now_group.locations.add(self.location1)
        self.service_now_group.devices.add(self.device2)
        
        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_service_now_groups(self):
        """Test listing ServiceNow groups."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test ServiceNow Group")

    def test_retrieve_service_now_group(self):
        """Test retrieving a single ServiceNow group."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-detail", kwargs={"pk": self.service_now_group.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test ServiceNow Group")
        self.assertEqual(response.data["description"], "Test description")
        self.assertEqual(response.data["device_count"], 2)  # 1 from location + 1 explicit

    def test_create_service_now_group(self):
        """Test creating a new ServiceNow group."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-list")
        data = {
            "name": "New ServiceNow Group",
            "description": "New group description",
            "locations": [self.location1.pk],
            "devices": [self.device1.pk]
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ServiceNowGroup.objects.count(), 2)
        
        new_group = ServiceNowGroup.objects.get(name="New ServiceNow Group")
        self.assertEqual(new_group.description, "New group description")
        self.assertEqual(new_group.locations.count(), 1)
        self.assertEqual(new_group.devices.count(), 1)

    def test_create_service_now_group_validation_error(self):
        """Test creating a ServiceNow group without assignments."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-list")
        data = {
            "name": "Invalid Group",
            "description": "No assignments"
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assignment method", response.data["non_field_errors"][0])

    def test_update_service_now_group(self):
        """Test updating a ServiceNow group."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-detail", kwargs={"pk": self.service_now_group.pk})
        data = {
            "name": "Updated ServiceNow Group",
            "description": "Updated description",
            "locations": [self.location2.pk],
            "devices": [self.device1.pk]
        }
        
        response = self.client.put(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.service_now_group.refresh_from_db()
        self.assertEqual(self.service_now_group.name, "Updated ServiceNow Group")
        self.assertEqual(self.service_now_group.description, "Updated description")
        self.assertEqual(self.service_now_group.locations.count(), 1)
        self.assertEqual(self.service_now_group.locations.first(), self.location2)

    def test_partial_update_service_now_group(self):
        """Test partial update of a ServiceNow group."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-detail", kwargs={"pk": self.service_now_group.pk})
        data = {
            "description": "Partially updated description"
        }
        
        response = self.client.patch(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.service_now_group.refresh_from_db()
        self.assertEqual(self.service_now_group.description, "Partially updated description")
        # Other fields should remain unchanged
        self.assertEqual(self.service_now_group.name, "Test ServiceNow Group")

    def test_delete_service_now_group(self):
        """Test deleting a ServiceNow group."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-detail", kwargs={"pk": self.service_now_group.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ServiceNowGroup.objects.count(), 0)

    def test_filter_service_now_groups_by_name(self):
        """Test filtering ServiceNow groups by name."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-list")
        response = self.client.get(url, {"name": "Test"})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        
        response = self.client.get(url, {"name": "Nonexistent"})
        self.assertEqual(len(response.data["results"]), 0)

    def test_filter_service_now_groups_by_location(self):
        """Test filtering ServiceNow groups by location."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-list")
        response = self.client.get(url, {"locations": [self.location1.slug]})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        
        response = self.client.get(url, {"locations": [self.location2.slug]})
        self.assertEqual(len(response.data["results"]), 0)

    def test_filter_service_now_groups_by_device(self):
        """Test filtering ServiceNow groups by device."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-list")
        response = self.client.get(url, {"devices": [self.device2.name]})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        
        response = self.client.get(url, {"devices": [self.device1.name]})
        self.assertEqual(len(response.data["results"]), 0)

    def test_associated_devices_action(self):
        """Test the associated_devices custom action."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-associated-devices", kwargs={"pk": self.service_now_group.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        device_names = [device["name"] for device in response.data["results"]]
        self.assertIn("Test Device 1", device_names)  # From location
        self.assertIn("Test Device 2", device_names)  # Explicit assignment

    def test_check_device_association_action(self):
        """Test the check_device_association custom action."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-check-device-association", kwargs={"pk": self.service_now_group.pk})
        
        # Test with associated device
        data = {"device_id": self.device1.pk}
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_associated"])
        self.assertEqual(response.data["device_name"], "Test Device 1")
        
        # Test with non-associated device
        non_associated_device = Device.objects.create(
            name="Non Associated Device",
            device_type=self.device_type,
            device_role=self.device_role,
            location=self.location2,
            status=self.status
        )
        data = {"device_id": non_associated_device.pk}
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_associated"])

    def test_check_device_association_invalid_device(self):
        """Test check_device_association with invalid device ID."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-check-device-association", kwargs={"pk": self.service_now_group.pk})
        data = {"device_id": 99999}  # Non-existent device
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Device not found", response.data["error"])

    def test_check_device_association_missing_device_id(self):
        """Test check_device_association without device_id."""
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-check-device-association", kwargs={"pk": self.service_now_group.pk})
        data = {}
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("device_id is required", response.data["error"])

    def test_statistics_action(self):
        """Test the statistics custom action."""
        # Create additional groups for testing
        ServiceNowGroup.objects.create(name="Group 2", description="Second group")
        ServiceNowGroup.objects.create(name="Group 3", description="Third group")
        
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-statistics")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_groups"], 3)
        self.assertEqual(response.data["groups_with_locations"], 1)
        self.assertEqual(response.data["groups_with_devices"], 1)

    def test_unauthorized_access(self):
        """Test unauthorized access to API endpoints."""
        # Create unauthenticated client
        client = APIClient()
        
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-list")
        response = client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ServiceNowGroupAPIPermissionTestCase(TestCase):
    """Test cases for ServiceNowGroup API permissions."""

    def setUp(self):
        """Set up test data."""
        # Create users with different permissions
        self.user_no_perms = User.objects.create_user(
            username="noperms",
            password="testpass123"
        )
        
        self.user_view_perms = User.objects.create_user(
            username="viewperms",
            password="testpass123"
        )
        # Add view permissions
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(ServiceNowGroup)
        view_permission = Permission.objects.get(content_type=content_type, codename="view_servicenowgroup")
        self.user_view_perms.user_permissions.add(view_permission)
        
        # Create test data
        self.location = Location.objects.create(name="Test Location", slug="test-location")
        self.service_now_group = ServiceNowGroup.objects.create(
            name="Test Group",
            description="Test description"
        )
        self.service_now_group.locations.add(self.location)
        
        self.client = APIClient()

    def test_user_without_permissions(self):
        """Test API access for user without permissions."""
        self.client.force_authenticate(user=self.user_no_perms)
        
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_with_view_permissions(self):
        """Test API access for user with view permissions."""
        self.client.force_authenticate(user=self.user_view_perms)
        
        # Should be able to view
        url = reverse("plugins-api:service_now_groups-api:servicenowgroup-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should not be able to create
        data = {"name": "New Group", "description": "New description"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 