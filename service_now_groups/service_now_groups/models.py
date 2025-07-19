"""Models for the ServiceNow Groups app."""

from typing import List, Optional, Union
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from nautobot.core.models import BaseModel
from nautobot.extras.models import ChangeLoggedModel, CustomFieldModel
from nautobot.extras.utils import extras_features


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class ServiceNowGroup(BaseModel, ChangeLoggedModel, CustomFieldModel):
    """
    ServiceNow Group model for associating ServiceNow groups with Nautobot devices.

    This model allows dynamic assignment of ServiceNow groups to devices based on:
    - Location
    - Dynamic Groups
    - Explicit device assignment
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the ServiceNow group",
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the ServiceNow group's purpose",
    )
    locations = models.ManyToManyField(
        to="dcim.Location",
        blank=True,
        related_name="service_now_groups",
        help_text="Locations associated with this ServiceNow group",
    )
    dynamic_groups = models.ManyToManyField(
        to="extras.DynamicGroup",
        blank=True,
        related_name="service_now_groups",
        help_text="Dynamic groups associated with this ServiceNow group",
    )
    devices = models.ManyToManyField(
        to="dcim.Device",
        blank=True,
        related_name="service_now_groups",
        help_text="Specific devices associated with this ServiceNow group",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "ServiceNow Group"
        verbose_name_plural = "ServiceNow Groups"

    def __str__(self):
        """Return the name of the ServiceNow group."""
        return self.name

    def get_absolute_url(self):
        """Return the absolute URL for this ServiceNow group."""
        return reverse("plugins:service_now_groups:servicenowgroups_detail", kwargs={"pk": self.pk})

    def clean(self):
        """Validate the ServiceNow group."""
        super().clean()

        # Ensure at least one assignment method is specified
        if not self.locations.exists() and not self.dynamic_groups.exists() and not self.devices.exists():
            raise ValidationError(
                "At least one assignment method must be specified: locations, dynamic groups, or devices."
            )

    def get_associated_devices(self) -> models.QuerySet:
        """
        Get all devices associated with this ServiceNow group.

        Returns devices based on:
        1. Devices in associated locations
        2. Devices in associated dynamic groups
        3. Explicitly assigned devices

        Returns:
            QuerySet: All associated devices
        """
        from nautobot.dcim.models import Device

        device_ids = set()

        # Add devices from associated locations
        if self.locations.exists():
            location_device_ids = Device.objects.filter(
                location__in=self.locations.all()
            ).values_list('id', flat=True)
            device_ids.update(location_device_ids)

        # Add devices from associated dynamic groups
        if self.dynamic_groups.exists():
            for dynamic_group in self.dynamic_groups.all():
                try:
                    dynamic_group_device_ids = dynamic_group.members.values_list('id', flat=True)
                    device_ids.update(dynamic_group_device_ids)
                except Exception:
                    # Skip dynamic groups that can't be evaluated
                    continue

        # Add explicitly assigned devices
        if self.devices.exists():
            explicit_device_ids = self.devices.values_list('id', flat=True)
            device_ids.update(explicit_device_ids)

        return Device.objects.filter(id__in=device_ids)

    def is_device_associated(self, device) -> bool:
        """
        Check if a specific device is associated with this ServiceNow group.

        Args:
            device: Device instance to check

        Returns:
            bool: True if device is associated, False otherwise
        """
        # Check explicit device assignment
        if self.devices.filter(pk=device.pk).exists():
            return True

        # Check location assignment
        if self.locations.filter(pk=device.location.pk).exists():
            return True

        # Check dynamic group assignment
        for dynamic_group in self.dynamic_groups.all():
            try:
                if device in dynamic_group.members:
                    return True
            except Exception:
                # Skip dynamic groups that can't be evaluated
                continue

        return False

    @property
    def device_count(self) -> int:
        """Return the number of devices associated with this group."""
        return self.get_associated_devices().count()

    @property
    def assignment_summary(self) -> str:
        """Return a summary of how this group is assigned."""
        summary: List[str] = []
        
        if self.locations.exists():
            summary.append(f"{self.locations.count()} location(s)")
        
        if self.dynamic_groups.exists():
            summary.append(f"{self.dynamic_groups.count()} dynamic group(s)")
        
        if self.devices.exists():
            summary.append(f"{self.devices.count()} explicit device(s)")
        
        return ", ".join(summary) if summary else "No assignments" 