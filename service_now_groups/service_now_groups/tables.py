"""Tables for the ServiceNow Groups app."""

import django_tables2 as tables

from nautobot.apps.tables import BaseTable, ButtonsColumn, ToggleColumn

from .models import ServiceNowGroup


class ServiceNowGroupTable(BaseTable):
    """Table for displaying ServiceNow Groups."""

    pk = ToggleColumn()
    name = tables.LinkColumn()
    description = tables.Column()
    locations = tables.TemplateColumn(
        template_code="{% for location in value.all %}<span class='badge bg-secondary'>{{ location.name }}</span>{% endfor %}",
        orderable=False,
    )
    dynamic_groups = tables.TemplateColumn(
        template_code="{% for dg in value.all %}<span class='badge bg-info'>{{ dg.name }}</span>{% endfor %}",
        orderable=False,
    )
    devices = tables.TemplateColumn(
        template_code="{% for device in value.all %}<span class='badge bg-warning'>{{ device.name }}</span>{% endfor %}",
        orderable=False,
    )
    device_count = tables.Column(accessor="device_count", verbose_name="Associated Devices")
    created = tables.DateColumn()
    last_updated = tables.DateTimeColumn()
    actions = ButtonsColumn(ServiceNowGroup, pk_field="pk")

    class Meta(BaseTable.Meta):
        model = ServiceNowGroup
        fields = [
            "pk",
            "name",
            "description",
            "locations",
            "dynamic_groups",
            "devices",
            "device_count",
            "created",
            "last_updated",
            "actions",
        ]
        default_columns = [
            "pk",
            "name",
            "description",
            "device_count",
            "created",
            "actions",
        ] 