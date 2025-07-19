"""Filtering for ServiceNow Groups."""

from nautobot.apps.filters import NautobotFilterSet
from .models import ServiceNowGroup

class ServiceNowGroupFilterSet(NautobotFilterSet):
    """Filter for ServiceNowGroup."""

    class Meta:
        """Meta attributes for filter."""
        model = ServiceNowGroup
        fields = ["name", "description"] 