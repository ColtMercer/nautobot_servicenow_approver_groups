"""Tests for the ServiceNow Groups models."""

import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase

from nautobot.dcim.models import Device, Location, DeviceRole, DeviceType, Manufacturer, Status
from nautobot.extras.models import DynamicGroup

from service_now_groups.models import ServiceNowGroup


class ServiceNowGroupModelTestCase(TestCase):
    """Test cases for ServiceNowGroup model."""

    def setUp(self):
        """Set up test data."""
        # Create test locations
        self.location1 = Location.objects.create(name="Test Location 1", slug="test-location-1")
        self.location2 = Location.objects.create(name="Test Location 2", slug="test-location-2")
        
        # Create test device role and type
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
            location=self.location1,
            status=self.status
        )
        self.device3 = Device.objects.create(
            name="Test Device 3",
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

    def test_service_now_group_creation(self):
        """Test basic ServiceNow group creation."""
        group = ServiceNowGroup.objects.create(
            name="Test Group",
            description="Test description"
        )
        self.assertEqual(group.name, "Test Group")
        self.assertEqual(group.description, "Test description")
        self.assertIsNotNone(group.id)

    def test_service_now_group_str_representation(self):
        """Test string representation of ServiceNow group."""
        group = ServiceNowGroup.objects.create(name="Test Group")
        self.assertEqual(str(group), "Test Group")

    def test_service_now_group_unique_name(self):
        """Test that ServiceNow group names must be unique."""
        ServiceNowGroup.objects.create(name="Test Group")
        with self.assertRaises(Exception):  # Should raise IntegrityError
            ServiceNowGroup.objects.create(name="Test Group")

    def test_service_now_group_validation_no_assignments(self):
        """Test validation when no assignment method is specified."""
        group = ServiceNowGroup(name="Test Group")
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_service_now_group_validation_with_locations(self):
        """Test validation with location assignment."""
        group = ServiceNowGroup(
            name="Test Group",
            description="Test description"
        )
        group.full_clean()  # Should not raise ValidationError
        group.save()
        group.locations.add(self.location1)
        self.assertEqual(group.locations.count(), 1)

    def test_service_now_group_validation_with_dynamic_groups(self):
        """Test validation with dynamic group assignment."""
        group = ServiceNowGroup(
            name="Test Group",
            description="Test description"
        )
        group.full_clean()  # Should not raise ValidationError
        group.save()
        group.dynamic_groups.add(self.dynamic_group)
        self.assertEqual(group.dynamic_groups.count(), 1)

    def test_service_now_group_validation_with_devices(self):
        """Test validation with explicit device assignment."""
        group = ServiceNowGroup(
            name="Test Group",
            description="Test description"
        )
        group.full_clean()  # Should not raise ValidationError
        group.save()
        group.devices.add(self.device1)
        self.assertEqual(group.devices.count(), 1)

    def test_get_associated_devices_location_based(self):
        """Test getting devices associated via location."""
        group = ServiceNowGroup.objects.create(name="Test Group")
        group.locations.add(self.location1)
        
        associated_devices = group.get_associated_devices()
        self.assertIn(self.device1, associated_devices)
        self.assertIn(self.device2, associated_devices)
        self.assertNotIn(self.device3, associated_devices)

    def test_get_associated_devices_dynamic_group_based(self):
        """Test getting devices associated via dynamic group."""
        group = ServiceNowGroup.objects.create(name="Test Group")
        group.dynamic_groups.add(self.dynamic_group)
        
        associated_devices = group.get_associated_devices()
        self.assertIn(self.device1, associated_devices)
        self.assertIn(self.device2, associated_devices)
        self.assertNotIn(self.device3, associated_devices)

    def test_get_associated_devices_explicit_assignment(self):
        """Test getting devices with explicit assignment."""
        group = ServiceNowGroup.objects.create(name="Test Group")
        group.devices.add(self.device1, self.device3)
        
        associated_devices = group.get_associated_devices()
        self.assertIn(self.device1, associated_devices)
        self.assertNotIn(self.device2, associated_devices)
        self.assertIn(self.device3, associated_devices)

    def test_get_associated_devices_multiple_methods(self):
        """Test getting devices with multiple assignment methods."""
        group = ServiceNowGroup.objects.create(name="Test Group")
        group.locations.add(self.location1)
        group.devices.add(self.device3)
        
        associated_devices = group.get_associated_devices()
        self.assertIn(self.device1, associated_devices)  # Via location
        self.assertIn(self.device2, associated_devices)  # Via location
        self.assertIn(self.device3, associated_devices)  # Via explicit assignment

    def test_is_device_associated_location_based(self):
        """Test device association check via location."""
        group = ServiceNowGroup.objects.create(name="Test Group")
        group.locations.add(self.location1)
        
        self.assertTrue(group.is_device_associated(self.device1))
        self.assertTrue(group.is_device_associated(self.device2))
        self.assertFalse(group.is_device_associated(self.device3))

    def test_is_device_associated_dynamic_group_based(self):
        """Test device association check via dynamic group."""
        group = ServiceNowGroup.objects.create(name="Test Group")
        group.dynamic_groups.add(self.dynamic_group)
        
        self.assertTrue(group.is_device_associated(self.device1))
        self.assertTrue(group.is_device_associated(self.device2))
        self.assertFalse(group.is_device_associated(self.device3))

    def test_is_device_associated_explicit_assignment(self):
        """Test device association check via explicit assignment."""
        group = ServiceNowGroup.objects.create(name="Test Group")
        group.devices.add(self.device1)
        
        self.assertTrue(group.is_device_associated(self.device1))
        self.assertFalse(group.is_device_associated(self.device2))
        self.assertFalse(group.is_device_associated(self.device3))

    def test_device_count_property(self):
        """Test device_count property."""
        group = ServiceNowGroup.objects.create(name="Test Group")
        group.locations.add(self.location1)
        group.devices.add(self.device3)
        
        # Should count devices from location (2) + explicit device (1) = 3
        self.assertEqual(group.device_count, 3)

    def test_assignment_summary_property(self):
        """Test assignment_summary property."""
        group = ServiceNowGroup.objects.create(name="Test Group")
        group.locations.add(self.location1)
        group.dynamic_groups.add(self.dynamic_group)
        group.devices.add(self.device3)
        
        summary = group.assignment_summary
        self.assertIn("1 location(s)", summary)
        self.assertIn("1 dynamic group(s)", summary)
        self.assertIn("1 explicit device(s)", summary)

    def test_assignment_summary_no_assignments(self):
        """Test assignment_summary when no assignments exist."""
        group = ServiceNowGroup.objects.create(name="Test Group")
        self.assertEqual(group.assignment_summary, "No assignments")

    def test_get_absolute_url(self):
        """Test get_absolute_url method."""
        group = ServiceNowGroup.objects.create(name="Test Group")
        url = group.get_absolute_url()
        self.assertIn(str(group.pk), url)
        self.assertIn("servicenowgroup", url)


class ServiceNowGroupModelIntegrationTestCase(TestCase):
    """Integration tests for ServiceNowGroup model with complex scenarios."""

    def setUp(self):
        """Set up complex test data."""
        # Create locations hierarchy
        self.parent_location = Location.objects.create(name="Parent Location", slug="parent-location")
        self.child_location = Location.objects.create(
            name="Child Location", 
            slug="child-location",
            parent=self.parent_location
        )
        
        # Create device components
        self.device_role = DeviceRole.objects.create(name="Test Role", slug="test-role")
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer", slug="test-manufacturer")
        self.device_type = DeviceType.objects.create(
            manufacturer=self.manufacturer,
            model="Test Model",
            slug="test-model"
        )
        self.status = Status.objects.get(slug="active")
        
        # Create devices in different locations
        self.parent_device = Device.objects.create(
            name="Parent Device",
            device_type=self.device_type,
            device_role=self.device_role,
            location=self.parent_location,
            status=self.status
        )
        self.child_device = Device.objects.create(
            name="Child Device",
            device_type=self.device_type,
            device_role=self.device_role,
            location=self.child_location,
            status=self.status
        )
        
        # Create dynamic groups
        self.parent_dynamic_group = DynamicGroup.objects.create(
            name="Parent Dynamic Group",
            slug="parent-dynamic-group",
            content_type_id=Device._meta.pk,
            filter={"location": [self.parent_location.pk]}
        )
        self.child_dynamic_group = DynamicGroup.objects.create(
            name="Child Dynamic Group",
            slug="child-dynamic-group",
            content_type_id=Device._meta.pk,
            filter={"location": [self.child_location.pk]}
        )

    def test_complex_assignment_scenario(self):
        """Test complex assignment scenario with multiple methods."""
        group = ServiceNowGroup.objects.create(
            name="Complex Group",
            description="Group with multiple assignment methods"
        )
        
        # Add assignments
        group.locations.add(self.parent_location)
        group.dynamic_groups.add(self.child_dynamic_group)
        group.devices.add(self.child_device)
        
        # Test device associations
        associated_devices = group.get_associated_devices()
        
        # Should include parent_device (via parent_location)
        self.assertIn(self.parent_device, associated_devices)
        # Should include child_device (via explicit assignment AND child_dynamic_group)
        self.assertIn(self.child_device, associated_devices)
        
        # Test individual device checks
        self.assertTrue(group.is_device_associated(self.parent_device))
        self.assertTrue(group.is_device_associated(self.child_device))
        
        # Test device count (should be 2 unique devices)
        self.assertEqual(group.device_count, 2)

    def test_dynamic_group_evaluation_error_handling(self):
        """Test handling of dynamic group evaluation errors."""
        # Create a dynamic group with invalid filter
        invalid_dynamic_group = DynamicGroup.objects.create(
            name="Invalid Dynamic Group",
            slug="invalid-dynamic-group",
            content_type_id=Device._meta.pk,
            filter={"invalid_field": "invalid_value"}
        )
        
        group = ServiceNowGroup.objects.create(name="Test Group")
        group.dynamic_groups.add(invalid_dynamic_group)
        group.locations.add(self.parent_location)  # Add valid assignment
        
        # Should not raise exception, should still work with valid assignments
        associated_devices = group.get_associated_devices()
        self.assertIn(self.parent_device, associated_devices)
        
        # Should handle device association check gracefully
        self.assertTrue(group.is_device_associated(self.parent_device)) 