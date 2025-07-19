"""UI views for the ServiceNow Groups app."""

from nautobot.apps.views import NautobotUIViewSet
from .models import ServiceNowGroup
from .forms import ServiceNowGroupForm
from .tables import ServiceNowGroupTable
from .filters import ServiceNowGroupFilterSet

class ServiceNowGroupUIViewSet(NautobotUIViewSet):
    """UI ViewSet for ServiceNowGroup model."""

    queryset = ServiceNowGroup.objects.all()
    form_class = ServiceNowGroupForm
    table_class = ServiceNowGroupTable
    filterset_class = ServiceNowGroupFilterSet
    
    def get_object_view_extra_context(self, request, instance):
        """
        Return any additional context data for the object detail view.
        """
        return {"associated_devices": instance.get_associated_devices()} 