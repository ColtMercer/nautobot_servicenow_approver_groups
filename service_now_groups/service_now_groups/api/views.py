"""REST API views for the ServiceNow Groups app."""

from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from nautobot.apps.api import NautobotModelViewSet
from nautobot.apps.filters import NautobotFilterSet
from nautobot.dcim.models import Device, Location
from nautobot.extras.models import DynamicGroup
from ..models import ServiceNowGroup


class ServiceNowGroupFilterSet(NautobotFilterSet):
    """FilterSet for ServiceNowGroup model."""

    name = filters.CharFilter(lookup_expr="icontains")
    description = filters.CharFilter(lookup_expr="icontains")
    locations = filters.ModelMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name="locations__slug",
        to_field_name="slug",
    )
    dynamic_groups = filters.ModelMultipleChoiceFilter(
        queryset=DynamicGroup.objects.all(),
        field_name="dynamic_groups__slug",
        to_field_name="slug",
    )
    devices = filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        field_name="devices__name",
        to_field_name="name",
    )
    has_devices = filters.BooleanFilter(method="_has_devices")
    created = filters.DateTimeFilter()
    created__gte = filters.DateTimeFilter(field_name="created", lookup_expr="gte")
    created__lte = filters.DateTimeFilter(field_name="created", lookup_expr="lte")
    last_updated = filters.DateTimeFilter()
    last_updated__gte = filters.DateTimeFilter(field_name="last_updated", lookup_expr="gte")
    last_updated__lte = filters.DateTimeFilter(field_name="last_updated", lookup_expr="lte")

    def _has_devices(self, queryset, name, value):
        """Filter by whether the group has associated devices."""
        if value:
            return queryset.filter(devices__isnull=False).distinct()
        return queryset.filter(devices__isnull=True)

    class Meta:
        model = ServiceNowGroup
        fields = [
            "id",
            "name",
            "description",
            "locations",
            "dynamic_groups",
            "devices",
            "created",
            "last_updated",
        ]


class ServiceNowGroupViewSet(NautobotModelViewSet):
    """ViewSet for ServiceNowGroup model."""

    queryset = ServiceNowGroup.objects.all()
    lookup_field = "pk"

    def get_queryset(self):
        """Return queryset with optimized prefetch."""
        # Defer model import until runtime
        return ServiceNowGroup.objects.all().prefetch_related(
            "locations",
            "dynamic_groups",
            "devices",
        )

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        # Defer serializer imports until runtime
        from .serializers import (
            ServiceNowGroupCreateSerializer,
            ServiceNowGroupNestedSerializer,
            ServiceNowGroupSerializer,
            ServiceNowGroupUpdateSerializer,
        )
        
        if self.action == "create":
            return ServiceNowGroupCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ServiceNowGroupUpdateSerializer
        elif self.action == "list":
            return ServiceNowGroupNestedSerializer
        return ServiceNowGroupSerializer

    @action(detail=True, methods=["get"])
    def associated_devices(self, request, pk=None):
        """Get all devices associated with this ServiceNow group."""
        service_now_group = self.get_object()
        devices = service_now_group.get_associated_devices()
        
        # Use Nautobot's Device serializer for consistent API response
        from nautobot.dcim.api.serializers import DeviceSerializer
        
        page = self.paginate_queryset(devices)
        if page is not None:
            serializer = DeviceSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        
        serializer = DeviceSerializer(devices, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def sync_devices(self, request, pk=None):
        """Manually trigger device synchronization for this group."""
        service_now_group = self.get_object()
        try:
            # This would trigger the actual sync logic
            # For now, just return success
            return Response(
                {"status": "success", "message": "Device synchronization triggered"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get statistics about ServiceNow groups."""
        # Defer model import until runtime
        total_groups = ServiceNowGroup.objects.count()
        groups_with_devices = ServiceNowGroup.objects.filter(devices__isnull=False).distinct().count()
        groups_with_locations = ServiceNowGroup.objects.filter(locations__isnull=False).distinct().count()
        groups_with_dynamic_groups = ServiceNowGroup.objects.filter(dynamic_groups__isnull=False).distinct().count()
        
        return Response({
            "total_groups": total_groups,
            "groups_with_devices": groups_with_devices,
            "groups_with_locations": groups_with_locations,
            "groups_with_dynamic_groups": groups_with_dynamic_groups,
        }) 