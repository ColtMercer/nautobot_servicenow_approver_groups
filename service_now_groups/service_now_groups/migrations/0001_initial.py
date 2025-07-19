"""Initial migration for ServiceNow Groups app."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Initial migration for ServiceNowGroup model."""

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceNowGroup",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True,
                        serialize=False,
                        editable=False,
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, null=True),
                ),
                (
                    "last_updated",
                    models.DateTimeField(auto_now=True, null=True),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the ServiceNow group",
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Description of the ServiceNow group's purpose",
                    ),
                ),
                (
                    "devices",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific devices associated with this ServiceNow group",
                        related_name="service_now_groups",
                        to="dcim.device",
                    ),
                ),
                (
                    "dynamic_groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Dynamic groups associated with this ServiceNow group",
                        related_name="service_now_groups",
                        to="extras.dynamicgroup",
                    ),
                ),
                (
                    "locations",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Locations associated with this ServiceNow group",
                        related_name="service_now_groups",
                        to="dcim.location",
                    ),
                ),
            ],
            options={
                "verbose_name": "ServiceNow Group",
                "verbose_name_plural": "ServiceNow Groups",
                "ordering": ["name"],
            },
        ),
    ] 