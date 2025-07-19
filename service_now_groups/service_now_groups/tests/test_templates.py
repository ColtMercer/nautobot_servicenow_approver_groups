"""Tests for the ServiceNow Groups templates."""

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.template import Context, Template
from django.template.loader import render_to_string

from nautobot.dcim.models import Device, Location, DeviceRole, DeviceType, Manufacturer, Status
from nautobot.extras.models import DynamicGroup

from service_now_groups.models import ServiceNowGroup
from service_now_groups.templatetags.service_now_groups_extras import (
    device_service_now_groups_panel,
    device_service_now_groups_count,
    has_servicenow_groups
)

User = get_user_model()


class ServiceNowGroupTemplateTestCase(TestCase):
    """Test cases for ServiceNowGroup templates."""

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
        
        # Create test ServiceNow groups
        self.group1 = ServiceNowGroup.objects.create(
            name="Test Group 1",
            description="First test group"
        )
        self.group1.locations.add(self.location1)
        
        self.group2 = ServiceNowGroup.objects.create(
            name="Test Group 2",
            description="Second test group"
        )
        self.group2.devices.add(self.device2)
        
        # Set up request factory
        self.factory = RequestFactory()

    def test_device_service_now_groups_template_rendering(self):
        """Test rendering of device ServiceNow groups template."""
        request = self.factory.get('/')
        request.user = self.user
        
        context = {
            'object': self.device1,
            'servicenow_groups': [self.group1]
        }
        
        rendered = render_to_string(
            'service_now_groups/device_service_now_groups.html',
            context,
            request=request
        )
        
        # Check that the template renders without errors
        self.assertIn("ServiceNow Groups", rendered)
        self.assertIn("Test Group 1", rendered)
        self.assertIn("First test group", rendered)
        self.assertIn("1 location(s)", rendered)

    def test_device_service_now_groups_template_no_groups(self):
        """Test template rendering when no groups are associated."""
        request = self.factory.get('/')
        request.user = self.user
        
        context = {
            'object': self.device2,
            'servicenow_groups': []
        }
        
        rendered = render_to_string(
            'service_now_groups/device_service_now_groups.html',
            context,
            request=request
        )
        
        # Check that the template shows the no groups message
        self.assertIn("No ServiceNow groups are associated", rendered)
        self.assertIn("Create ServiceNow Group", rendered)

    def test_servicenowgroup_list_template_rendering(self):
        """Test rendering of ServiceNow group list template."""
        request = self.factory.get('/')
        request.user = self.user
        
        context = {
            'servicenow_groups': [self.group1, self.group2]
        }
        
        rendered = render_to_string(
            'service_now_groups/servicenowgroup_list.html',
            context,
            request=request
        )
        
        # Check that the template renders without errors
        self.assertIn("ServiceNow Groups", rendered)
        self.assertIn("Test Group 1", rendered)
        self.assertIn("Test Group 2", rendered)
        self.assertIn("Add ServiceNow Group", rendered)

    def test_servicenowgroup_detail_template_rendering(self):
        """Test rendering of ServiceNow group detail template."""
        request = self.factory.get('/')
        request.user = self.user
        
        context = {
            'servicenow_group': self.group1,
            'associated_devices': [self.device1]
        }
        
        rendered = render_to_string(
            'service_now_groups/servicenowgroup_detail.html',
            context,
            request=request
        )
        
        # Check that the template renders without errors
        self.assertIn("Test Group 1", rendered)
        self.assertIn("First test group", rendered)
        self.assertIn("Test Location 1", rendered)
        self.assertIn("Test Device 1", rendered)

    def test_template_tags_device_service_now_groups_panel(self):
        """Test the device_service_now_groups_panel template tag."""
        request = self.factory.get('/')
        request.user = self.user
        
        context = {'object': self.device1}
        result = device_service_now_groups_panel(context)
        
        # Check that the tag returns the expected context
        self.assertIn('servicenow_groups', result)
        self.assertIn('object', result)
        self.assertEqual(result['object'], self.device1)
        self.assertIn(self.group1, result['servicenow_groups'])

    def test_template_tags_device_service_now_groups_count(self):
        """Test the device_service_now_groups_count template tag."""
        request = self.factory.get('/')
        request.user = self.user
        
        context = {'object': self.device1}
        count = device_service_now_groups_count(context)
        
        # Device1 should be associated with group1 (via location)
        self.assertEqual(count, 1)
        
        context = {'object': self.device2}
        count = device_service_now_groups_count(context)
        
        # Device2 should be associated with group2 (via explicit assignment)
        self.assertEqual(count, 1)

    def test_template_filter_has_servicenow_groups(self):
        """Test the has_servicenow_groups template filter."""
        # Device1 should have groups (via location)
        self.assertTrue(has_servicenow_groups(self.device1))
        
        # Device2 should have groups (via explicit assignment)
        self.assertTrue(has_servicenow_groups(self.device2))
        
        # Create a device with no associations
        device3 = Device.objects.create(
            name="Test Device 3",
            device_type=self.device_type,
            device_role=self.device_role,
            status=self.status
        )
        self.assertFalse(has_servicenow_groups(device3))

    def test_template_with_multiple_assignment_methods(self):
        """Test template rendering with multiple assignment methods."""
        # Create a group with multiple assignment methods
        complex_group = ServiceNowGroup.objects.create(
            name="Complex Group",
            description="Group with multiple assignment methods"
        )
        complex_group.locations.add(self.location1)
        complex_group.dynamic_groups.add(self.dynamic_group)
        complex_group.devices.add(self.device2)
        
        request = self.factory.get('/')
        request.user = self.user
        
        context = {
            'servicenow_group': complex_group,
            'associated_devices': [self.device1, self.device2]
        }
        
        rendered = render_to_string(
            'service_now_groups/servicenowgroup_detail.html',
            context,
            request=request
        )
        
        # Check that all assignment methods are displayed
        self.assertIn("Test Location 1", rendered)
        self.assertIn("Test Dynamic Group", rendered)
        self.assertIn("Test Device 2", rendered)
        self.assertIn("1 location(s)", rendered)
        self.assertIn("1 dynamic group(s)", rendered)
        self.assertIn("1 explicit device(s)", rendered)


class ServiceNowGroupViewTestCase(TestCase):
    """Test cases for ServiceNowGroup views."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        # Create test location
        self.location = Location.objects.create(name="Test Location", slug="test-location")
        
        # Create test device components
        self.device_role = DeviceRole.objects.create(name="Test Role", slug="test-role")
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer", slug="test-manufacturer")
        self.device_type = DeviceType.objects.create(
            manufacturer=self.manufacturer,
            model="Test Model",
            slug="test-model"
        )
        self.status = Status.objects.get(slug="active")
        
        # Create test device
        self.device = Device.objects.create(
            name="Test Device",
            device_type=self.device_type,
            device_role=self.device_role,
            location=self.location,
            status=self.status
        )
        
        # Create test ServiceNow group
        self.service_now_group = ServiceNowGroup.objects.create(
            name="Test Group",
            description="Test description"
        )
        self.service_now_group.locations.add(self.location)

    def test_servicenowgroup_list_view(self):
        """Test ServiceNow group list view."""
        self.client.force_login(self.user)
        url = reverse("service_now_groups:servicenowgroup_list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Group", response.content.decode())
        self.assertIn("Test description", response.content.decode())

    def test_servicenowgroup_detail_view(self):
        """Test ServiceNow group detail view."""
        self.client.force_login(self.user)
        url = reverse("service_now_groups:servicenowgroup_detail", kwargs={"pk": self.service_now_group.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Group", response.content.decode())
        self.assertIn("Test description", response.content.decode())
        self.assertIn("Test Device", response.content.decode())

    def test_servicenowgroup_list_view_unauthorized(self):
        """Test ServiceNow group list view without authentication."""
        url = reverse("service_now_groups:servicenowgroup_list")
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_servicenowgroup_detail_view_unauthorized(self):
        """Test ServiceNow group detail view without authentication."""
        url = reverse("service_now_groups:servicenowgroup_detail", kwargs={"pk": self.service_now_group.pk})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_servicenowgroup_detail_view_nonexistent(self):
        """Test ServiceNow group detail view with nonexistent group."""
        self.client.force_login(self.user)
        url = reverse("service_now_groups:servicenowgroup_detail", kwargs={"pk": "00000000-0000-0000-0000-000000000000"})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


class ServiceNowGroupTemplateIntegrationTestCase(TestCase):
    """Integration tests for ServiceNowGroup template functionality."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        
        # Create test locations
        self.location1 = Location.objects.create(name="Location 1", slug="location-1")
        self.location2 = Location.objects.create(name="Location 2", slug="location-2")
        
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
            name="Device 1",
            device_type=self.device_type,
            device_role=self.device_role,
            location=self.location1,
            status=self.status
        )
        self.device2 = Device.objects.create(
            name="Device 2",
            device_type=self.device_type,
            device_role=self.device_role,
            location=self.location2,
            status=self.status
        )
        
        # Create test dynamic group
        self.dynamic_group = DynamicGroup.objects.create(
            name="Dynamic Group",
            slug="dynamic-group",
            content_type_id=Device._meta.pk,
            filter={"location": [self.location1.pk]}
        )
        
        # Create test ServiceNow groups
        self.location_group = ServiceNowGroup.objects.create(
            name="Location Group",
            description="Group assigned by location"
        )
        self.location_group.locations.add(self.location1)
        
        self.device_group = ServiceNowGroup.objects.create(
            name="Device Group",
            description="Group assigned by device"
        )
        self.device_group.devices.add(self.device2)
        
        self.dynamic_group_assigned = ServiceNowGroup.objects.create(
            name="Dynamic Group Assigned",
            description="Group assigned by dynamic group"
        )
        self.dynamic_group_assigned.dynamic_groups.add(self.dynamic_group)

    def test_complex_template_scenario(self):
        """Test complex template scenario with multiple groups and devices."""
        request = self.factory.get('/')
        request.user = self.user
        
        # Test device1 context (should have location_group and dynamic_group_assigned)
        context1 = {'object': self.device1}
        result1 = device_service_now_groups_panel(context1)
        
        self.assertIn(self.location_group, result1['servicenow_groups'])
        self.assertIn(self.dynamic_group_assigned, result1['servicenow_groups'])
        self.assertNotIn(self.device_group, result1['servicenow_groups'])
        
        # Test device2 context (should have device_group)
        context2 = {'object': self.device2}
        result2 = device_service_now_groups_panel(context2)
        
        self.assertIn(self.device_group, result2['servicenow_groups'])
        self.assertNotIn(self.location_group, result2['servicenow_groups'])
        self.assertNotIn(self.dynamic_group_assigned, result2['servicenow_groups'])
        
        # Test counts
        count1 = device_service_now_groups_count(context1)
        count2 = device_service_now_groups_count(context2)
        
        self.assertEqual(count1, 2)  # location_group + dynamic_group_assigned
        self.assertEqual(count2, 1)  # device_group only

    def test_template_performance(self):
        """Test template performance with multiple groups."""
        # Create many groups to test performance
        for i in range(10):
            group = ServiceNowGroup.objects.create(
                name=f"Performance Group {i}",
                description=f"Group {i} for performance testing"
            )
            if i % 2 == 0:
                group.locations.add(self.location1)
            else:
                group.devices.add(self.device2)
        
        request = self.factory.get('/')
        request.user = self.user
        
        context = {'object': self.device1}
        
        # This should not be slow even with many groups
        result = device_service_now_groups_panel(context)
        
        # Device1 should be associated with groups 0, 2, 4, 6, 8 (via location)
        self.assertEqual(len(result['servicenow_groups']), 5) 