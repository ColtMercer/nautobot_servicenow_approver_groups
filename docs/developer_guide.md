ServiceNow Groups Nautobot App Developer Guide

Table of Contents
	•	Introduction
	•	Prerequisites
	•	App Structure
	•	NautobotAppConfig
	•	Models
	•	API and Views
	•	UI Extensions
	•	Platform Features
	•	Testing
	•	Continuous Integration
	•	Contribution Guidelines
	•	Critical Lessons Learned

Introduction

This guide outlines the requirements and best practices for the ServiceNow Groups Nautobot app. It will provide a new ServiceNowGroup model to associate ServiceNow groups with Nautobot devices dynamically (by location, dynamic groups, or explicit device assignment). These groups will be added to any ServiceNow Change Record raised against affected CIs and displayed in a dedicated section on the device detail page.

Prerequisites
	•	Python 3.8+ (compatible with your Nautobot instance)
	•	Nautobot 1.x or later
	•	A development environment configured per the Nautobot Development Guide
	•	(Optional) cookiecutter-nautobot-app for scaffolding

App Structure  (docs.nautobot.com)

Follow the recommended Nautobot app layout:

service_now_groups/
├── pyproject.toml
├── README.md
└── service_now_groups/
    ├── __init__.py           # Contains NautobotAppConfig subclass
    ├── admin.py              # Django admin registrations
    ├── api/
    │   ├── serializers.py    # REST API serializers
    │   ├── urls.py           # REST API routes
    │   └── views.py          # REST API viewsets
    ├── migrations/
    │   └── 0001_initial.py   # Database migrations
    ├── models.py             # ServiceNowGroup model and logic
    ├── templates/
    │   └── service_now_groups/
    │       └── device_service_now_groups.html
    ├── tests/
    │   ├── test_models.py
    │   ├── test_api.py
    │   └── test_templates.py
    └── views.py              # UI view extensions if needed

NautobotAppConfig
	•	In service_now_groups/__init__.py, subclass NautobotAppConfig.
	•	Set attributes: name, verbose_name, default_settings.
	•	Optionally override ready() to connect signal handlers.

Models  (docs.nautobot.com)
	•	Define ServiceNowGroup in models.py:
	•	name = CharField(...)
	•	description = TextField(...)
	•	locations = ManyToManyField('dcim.Location')
	•	dynamic_groups = ManyToManyField('extras.DynamicGroup')
	•	devices = ManyToManyField('dcim.Device')
	•	Implement assignment logic (match on any attribute).
	•	Register model for global search, GraphQL, and Django admin.

API and Views
	•	Use Django REST Framework:
	•	Serializers in api/serializers.py.
	•	ViewSets in api/views.py (extend NautobotModelViewSet).
	•	Routes in api/urls.py.
	•	Expose CRUD endpoints for ServiceNowGroup.

UI Extensions  (docs.nautobot.com)
	•	Create template device_service_now_groups.html under templates/service_now_groups/.
	•	Use template_content.py to inject this into the device detail view.
	•	Enforce view permissions.

Platform Features
	•	(Optional) Add custom validators or filter extensions.
	•	Use change logging (change_logging.py) to audit assignment updates.

Testing  (docs.nautobot.com)
	•	Employ pytest with pytest-django and Nautobot's testing utilities.
	•	Write tests for:
	•	Model validation and dynamic assignment logic.
	•	API behavior (permissions, CRUD operations).
	•	Template rendering on device detail pages.
	•	Use factory classes (factory-boy) to simplify test data setup.

Continuous Integration
	•	Add a GitHub Actions workflow (.github/workflows/ci.yml):
	•	Run black --check, isort --check, flake8, and pytest.

Contribution Guidelines
	•	Follow Semantic Versioning.
	•	Maintain code style with black, isort, and flake8.
	•	Write clear commit messages and PR descriptions.
	•	Include or update CHANGELOG.md for each release.
	•	License under Apache 2.0.

Critical Lessons Learned

CRITICAL: Nautobot vs Django Development Patterns

1. **ALWAYS Use Nautobot Base Classes**
   - ❌ DO NOT use Django REST Framework classes directly (ModelViewSet, ModelSerializer)
   - ✅ ALWAYS use Nautobot base classes:
     - `NautobotModelViewSet` instead of `ModelViewSet`
     - `NautobotModelSerializer` instead of `ModelSerializer`
     - `NautobotFilterSet` instead of `FilterSet`
     - `NautobotModelForm` instead of `ModelForm`

2. **Circular Import Issues**
   - ❌ DO NOT import Nautobot components at module level in __init__.py, urls.py, or views.py
   - ❌ DO NOT use complex deferred loading patterns that still import at startup
   - ✅ Start with simple, empty URL patterns and add functionality gradually
   - ✅ Use basic Django views initially, then upgrade to NautobotUIViewSet later

3. **Plugin Loading Order**
   - Nautobot loads plugins before Django is fully configured
   - Any imports of Django components (auth, models, etc.) will cause AppRegistryNotReady errors
   - Keep plugin configuration minimal until Django is ready

4. **Development Strategy**
   - Start with template content injection (simplest)
   - Add basic Django views (no NautobotUIViewSet)
   - Add API functionality with proper Nautobot base classes
   - Finally add advanced UI features with NautobotUIViewSet

5. **Testing Approach**
   - Test plugin loading first (containers start without errors)
   - Test template content injection
   - Test API endpoints
   - Test UI functionality
   - Never assume something works - always verify

6. **Reference Implementation**
   - Study the Device Lifecycle Management app: https://github.com/nautobot/nautobot-app-device-lifecycle-mgmt
   - Follow their patterns exactly
   - Use their base classes and import patterns