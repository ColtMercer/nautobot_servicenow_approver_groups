"""REST API serializers for the ServiceNow Groups app."""

from rest_framework import serializers

from nautobot.apps.api import NautobotModelSerializer, WritableNestedSerializer
from nautobot.core.api.serializers import ValidatedModelSerializer


class ServiceNowGroupNestedSerializer(WritableNestedSerializer):
    """Nested serializer for ServiceNowGroup model."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:service_now_groups-api:servicenowgroup-detail")

    class Meta:
        model = None  # Will be set in __init__
        fields = ["id", "url", "name", "display"]


class ServiceNowGroupSerializer(NautobotModelSerializer):
    """Serializer for ServiceNowGroup model."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:service_now_groups-api:servicenowgroup-detail")
    locations = ServiceNowGroupNestedSerializer(many=True, read_only=True)
    dynamic_groups = ServiceNowGroupNestedSerializer(many=True, read_only=True)
    devices = ServiceNowGroupNestedSerializer(many=True, read_only=True)
    device_count = serializers.SerializerMethodField()

    class Meta:
        model = None  # Will be set in __init__
        fields = [
            "id",
            "url",
            "name",
            "description",
            "locations",
            "dynamic_groups",
            "devices",
            "device_count",
            "created",
            "last_updated",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the serializer with the correct model."""
        from ..models import ServiceNowGroup
        self.Meta.model = ServiceNowGroup
        super().__init__(*args, **kwargs)

    def get_device_count(self, obj):
        """Get the count of associated devices."""
        return obj.get_associated_devices().count()


class ServiceNowGroupCreateSerializer(ValidatedModelSerializer):
    """Serializer for creating ServiceNowGroup instances."""

    class Meta:
        model = None  # Will be set in __init__
        fields = [
            "name",
            "description",
            "locations",
            "dynamic_groups",
            "devices",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the serializer with the correct model."""
        from ..models import ServiceNowGroup
        self.Meta.model = ServiceNowGroup
        super().__init__(*args, **kwargs)

    def validate(self, data):
        """Validate the data."""
        # Ensure at least one assignment method is provided
        locations = data.get('locations', [])
        dynamic_groups = data.get('dynamic_groups', [])
        devices = data.get('devices', [])
        
        if not any([locations, dynamic_groups, devices]):
            raise serializers.ValidationError(
                "At least one of locations, dynamic groups, or devices must be selected."
            )
        
        return data


class ServiceNowGroupUpdateSerializer(ValidatedModelSerializer):
    """Serializer for updating ServiceNowGroup instances."""

    class Meta:
        model = None  # Will be set in __init__
        fields = [
            "name",
            "description",
            "locations",
            "dynamic_groups",
            "devices",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the serializer with the correct model."""
        from ..models import ServiceNowGroup
        self.Meta.model = ServiceNowGroup
        super().__init__(*args, **kwargs)

    def validate(self, data):
        """Validate the data."""
        # Ensure at least one assignment method is provided
        locations = data.get('locations', [])
        dynamic_groups = data.get('dynamic_groups', [])
        devices = data.get('devices', [])
        
        if not any([locations, dynamic_groups, devices]):
            raise serializers.ValidationError(
                "At least one of locations, dynamic groups, or devices must be selected."
            )
        
        return data 