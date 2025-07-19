"""URL patterns for the ServiceNow Groups app."""

from django.urls import path

from . import views
from nautobot.apps.urls import NautobotUIViewSetRouter
from .views import ServiceNowGroupUIViewSet

app_name = "service_now_groups"

router = NautobotUIViewSetRouter()
router.register("servicenowgroups", ServiceNowGroupUIViewSet)

urlpatterns = router.urls 