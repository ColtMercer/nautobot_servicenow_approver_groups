"""Django admin configuration for the ServiceNow Groups app."""

from django.contrib import admin
from django.utils.html import format_html

from .models import ServiceNowGroup


@admin.register(ServiceNowGroup)
class ServiceNowGroupAdmin(admin.ModelAdmin):
    """Admin interface for ServiceNowGroup model."""

    list_display = [
        "name",
        "description",
        "device_count_display",
        "assignment_summary_display",
        "created",
        "last_updated",
    ]
    list_filter = [
        "created",
        "last_updated",
        "locations",
        "dynamic_groups",
    ]
    search_fields = [
        "name",
        "description",
    ]
    readonly_fields = [
        "created",
        "last_updated",
        "device_count",
        "assignment_summary",
    ]
    filter_horizontal = [
        "locations",
        "dynamic_groups",
        "devices",
    ]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "description",
                )
            },
        ),
        (
            "Assignments",
            {
                "fields": (
                    "locations",
                    "dynamic_groups",
                    "devices",
                ),
                "description": "Configure how this ServiceNow group is assigned to devices. "
                "At least one assignment method must be specified.",
            },
        ),
        (
            "Statistics",
            {
                "fields": (
                    "device_count",
                    "assignment_summary",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "created",
                    "last_updated",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def device_count_display(self, obj):
        """Display device count with formatting."""
        count = obj.device_count
        return format_html(
            '<span style="color: {};">{}</span>',
            "green" if count > 0 else "red",
            f"{count} device(s)",
        )

    device_count_display.short_description = "Associated Devices"

    def assignment_summary_display(self, obj):
        """Display assignment summary with formatting."""
        summary = obj.assignment_summary
        return format_html(
            '<span style="color: {};">{}</span>',
            "green" if summary != "No assignments" else "red",
            summary,
        )

    assignment_summary_display.short_description = "Assignment Summary"

    def get_queryset(self, request):
        """Optimize queryset with related fields."""
        return super().get_queryset(request).prefetch_related(
            "locations",
            "dynamic_groups",
            "devices",
        )

    def save_model(self, request, obj, form, change):
        """Validate model before saving."""
        obj.full_clean()
        super().save_model(request, obj, form, change)

    # Custom admin actions
    actions = ['export_assignment_summary', 'validate_assignments']

    def export_assignment_summary(self, request, queryset):
        """Export assignment summary for selected ServiceNow groups."""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="servicenow_groups_assignment_summary.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Description', 'Assignment Summary', 'Device Count', 'Created'])
        
        for group in queryset:
            writer.writerow([
                group.name,
                group.description or '',
                group.assignment_summary,
                group.device_count,
                group.created.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    export_assignment_summary.short_description = "Export assignment summary to CSV"

    def validate_assignments(self, request, queryset):
        """Validate assignments for selected ServiceNow groups."""
        from django.contrib import messages
        
        for group in queryset:
            try:
                group.full_clean()
                messages.success(request, f"✓ {group.name}: Valid")
            except Exception as e:
                messages.error(request, f"✗ {group.name}: {str(e)}")
    
    validate_assignments.short_description = "Validate assignments" 