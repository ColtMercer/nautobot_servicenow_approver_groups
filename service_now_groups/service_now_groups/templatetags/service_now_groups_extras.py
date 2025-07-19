"""Template tags for the ServiceNow Groups app."""

from django.template import Library
from django.template.loader import render_to_string

from ..models import ServiceNowGroup

register = Library()


@register.inclusion_tag('service_now_groups/device_service_now_groups.html', takes_context=True)
def device_service_now_groups_panel(context):
    """
    Template tag to render ServiceNow groups panel for device detail pages.
    
    Usage: {% device_service_now_groups_panel %}
    """
    device = context.get('object')
    if not device:
        return {'servicenow_groups': []}
    
    # Get all ServiceNow groups associated with this device
    servicenow_groups = ServiceNowGroup.objects.filter(
        devices=device
    ).distinct()
    
    # Add groups from device's location
    if hasattr(device, 'location') and device.location:
        location_groups = ServiceNowGroup.objects.filter(
            locations=device.location
        ).distinct()
        servicenow_groups = servicenow_groups.union(location_groups)
    
    # Add groups from dynamic groups that include this device
    dynamic_groups = ServiceNowGroup.objects.filter(
        dynamic_groups__isnull=False
    ).distinct()
    
    for group in dynamic_groups:
        if group.is_device_associated(device):
            servicenow_groups = servicenow_groups.union([group])
    
    # Prefetch related objects for performance
    servicenow_groups = servicenow_groups.prefetch_related(
        'locations',
        'dynamic_groups',
        'devices'
    )
    
    return {
        'servicenow_groups': servicenow_groups,
        'object': device,
    }


@register.simple_tag(takes_context=True)
def device_service_now_groups_count(context):
    """
    Template tag to get the count of ServiceNow groups associated with a device.
    
    Usage: {% device_service_now_groups_count as count %}
    """
    device = context.get('object')
    if not device:
        return 0
    
    # Count ServiceNow groups associated with this device
    count = ServiceNowGroup.objects.filter(devices=device).count()
    
    # Add location-based groups
    if hasattr(device, 'location') and device.location:
        count += ServiceNowGroup.objects.filter(locations=device.location).count()
    
    # Add dynamic group-based associations
    dynamic_groups = ServiceNowGroup.objects.filter(dynamic_groups__isnull=False)
    for group in dynamic_groups:
        if group.is_device_associated(device):
            count += 1
    
    return count


@register.filter
def has_servicenow_groups(device):
    """
    Template filter to check if a device has associated ServiceNow groups.
    
    Usage: {{ device|has_servicenow_groups }}
    """
    if not device:
        return False
    
    # Check explicit device assignment
    if ServiceNowGroup.objects.filter(devices=device).exists():
        return True
    
    # Check location assignment
    if hasattr(device, 'location') and device.location:
        if ServiceNowGroup.objects.filter(locations=device.location).exists():
            return True
    
    # Check dynamic group assignment
    dynamic_groups = ServiceNowGroup.objects.filter(dynamic_groups__isnull=False)
    for group in dynamic_groups:
        if group.is_device_associated(device):
            return True
    
    return False 