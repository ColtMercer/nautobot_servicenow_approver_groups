"""Template content injection for the ServiceNow Groups app."""

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.template.loader import render_to_string

from .models import ServiceNowGroup
from nautobot.extras.plugins import TemplateExtension


class DeviceServiceNowGroups(TemplateExtension):
    """Template extension to add ServiceNow groups to device detail view."""

    model = 'dcim.device'

    def left_page(self, request, instance):
        """Render content for the left page section."""

        # Collect all ServiceNow group IDs associated with this device
        group_ids = set()
        
        # Add groups from explicit device assignment
        explicit_groups = ServiceNowGroup.objects.filter(devices=instance).values_list('id', flat=True)
        group_ids.update(explicit_groups)
        
        # Add groups from device's location
        if instance.location:
            location_groups = ServiceNowGroup.objects.filter(locations=instance.location).values_list('id', flat=True)
            group_ids.update(location_groups)
        
        # Add groups from dynamic groups that include this device
        dynamic_groups = ServiceNowGroup.objects.filter(dynamic_groups__isnull=False).distinct()
        for group in dynamic_groups:
            if group.is_device_associated(instance):
                group_ids.add(group.id)
        
        # Get all the groups in a single query
        servicenow_groups = ServiceNowGroup.objects.filter(id__in=group_ids).prefetch_related(
            'locations',
            'dynamic_groups', 
            'devices'
        )
        
        # Render the template
        template_context = {
            'servicenow_groups': servicenow_groups,
            'object': instance,  # Pass device as object for template compatibility
        }
        
        return self.render(
            'service_now_groups/device_service_now_groups.html',
            extra_context=template_context
        ) 