"""Forms for the ServiceNow Groups app."""

from django import forms

from nautobot.apps.forms import NautobotModelForm
from .models import ServiceNowGroup


class ServiceNowGroupForm(NautobotModelForm):
    """Form for creating and editing ServiceNow Groups."""

    class Meta:
        """Meta attributes."""
        model = ServiceNowGroup
        fields = ["name", "description", "locations", "dynamic_groups", "devices"] 