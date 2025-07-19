"""REST API URL configuration for the ServiceNow Groups app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceNowGroupViewSet

app_name = "service_now_groups-api"

router = DefaultRouter()
router.register('servicenowgroups', ServiceNowGroupViewSet)

urlpatterns = router.urls 