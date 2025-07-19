"""ServiceNow Groups Nautobot App."""

from django.urls import path, include
from nautobot.apps import NautobotAppConfig


class ServiceNowGroupsConfig(NautobotAppConfig):
    """Nautobot app configuration for the ServiceNow Groups plugin."""

    name = "service_now_groups"
    verbose_name = "ServiceNow Groups"
    description = "Associate ServiceNow groups with Nautobot devices dynamically"
    version = "0.1.0"
    author = "Nautobot Community"
    author_email = "community@nautobot.com"
    required_settings = []
    min_version = "1.0.0"
    max_version = "2.999"
    default_settings = {
        "enable_change_logging": True,
        "enable_graphql": True,
    }

    # Template content injection
    template_extensions = ['service_now_groups.template_content.DeviceServiceNowGroups']


# This is the config variable that Nautobot expects to find
config = ServiceNowGroupsConfig 