# ServiceNow Groups for Nautobot

A Nautobot app that associates ServiceNow groups with Nautobot devices dynamically based on location, dynamic groups, or explicit device assignment. These groups are displayed on device detail pages and can be used for ServiceNow Change Record automation.

## Features

- **Dynamic Group Assignment**: Associate ServiceNow groups with devices based on:
  - Location hierarchy
  - Dynamic group membership
  - Explicit device assignment
- **Device Detail Integration**: Display associated ServiceNow groups on device detail pages
- **REST API**: Full CRUD operations for managing ServiceNow groups
- **Django Admin**: Comprehensive admin interface for group management
- **Search & Filtering**: Advanced search and filtering capabilities
- **Change Logging**: Audit trail for all group assignments and changes

## Screenshots

### Device Detail Page Integration
![Device Detail Integration](docs/images/device-detail-integration.png)

### ServiceNow Groups List View
![Groups List View](docs/images/groups-list-view.png)

### Django Admin Interface
![Django Admin](docs/images/django-admin.png)

## Installation

### Prerequisites

- Python 3.8+
- Nautobot 1.5.0 or later
- PostgreSQL database
- Redis (for caching and background tasks)

### Option 1: Install from PyPI

```bash
pip install nautobot-servicenow-groups
```

### Option 2: Install from Source

```bash
git clone https://github.com/your-org/nautobot-servicenow-groups.git
cd nautobot-servicenow-groups
pip install -e .
```

### Configuration

1. **Add to Nautobot Configuration**

   Add `service_now_groups` to your `PLUGINS` setting in `nautobot_config.py`:

   ```python
   PLUGINS = ["service_now_groups"]
   ```

2. **Configure Plugin Settings** (Optional)

   ```python
   PLUGINS_CONFIG = {
       "service_now_groups": {
           "enable_change_logging": True,
           "enable_graphql": True,
           "enable_admin": True,
           "default_group_prefix": "SN_",
           "max_groups_per_device": 10,
       }
   }
   ```

3. **Run Database Migrations**

   ```bash
   nautobot-server migrate
   ```

4. **Collect Static Files**

   ```bash
   nautobot-server collectstatic --noinput
   ```

5. **Restart Nautobot**

   ```bash
   nautobot-server runserver
   ```

## Usage

### Creating ServiceNow Groups

1. **Via Django Admin**:
   - Navigate to Admin → ServiceNow Groups → ServiceNow Groups
   - Click "Add ServiceNow Group"
   - Fill in the required fields:
     - **Name**: ServiceNow group name (e.g., "Network_Engineers")
     - **Description**: Group description
     - **Locations**: Select locations to assign all devices in those locations
     - **Dynamic Groups**: Select dynamic groups to assign all devices in those groups
     - **Devices**: Select specific devices for explicit assignment

2. **Via REST API**:
   ```bash
   curl -X POST http://your-nautobot/api/plugins/service-now-groups/groups/ \
     -H "Authorization: Token your-token" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Network_Engineers",
       "description": "Network engineering team",
       "locations": [1, 2],
       "dynamic_groups": [3],
       "devices": [10, 15, 20]
     }'
   ```

### Viewing Associated Groups

1. **On Device Detail Page**:
   - Navigate to any device detail page
   - Scroll down to the "ServiceNow Groups" section
   - View all associated groups with assignment method indicators

2. **Via REST API**:
   ```bash
   # Get groups for a specific device
   curl http://your-nautobot/api/plugins/service-now-groups/groups/?device_id=10 \
     -H "Authorization: Token your-token"
   
   # Get all groups
   curl http://your-nautobot/api/plugins/service-now-groups/groups/ \
     -H "Authorization: Token your-token"
   ```

### Assignment Logic

The app uses a hierarchical assignment system:

1. **Explicit Device Assignment**: Devices explicitly assigned to a group
2. **Dynamic Group Membership**: Devices that are members of assigned dynamic groups
3. **Location Assignment**: Devices located in assigned locations (including child locations)

A device can be associated with multiple groups through different assignment methods.

## API Reference

### Endpoints

#### List ServiceNow Groups
```
GET /api/plugins/service-now-groups/groups/
```

**Query Parameters**:
- `name`: Filter by group name
- `location`: Filter by location ID
- `dynamic_group`: Filter by dynamic group ID
- `device`: Filter by device ID
- `search`: Search across name and description

#### Create ServiceNow Group
```
POST /api/plugins/service-now-groups/groups/
```

**Request Body**:
```json
{
  "name": "string",
  "description": "string",
  "locations": [1, 2, 3],
  "dynamic_groups": [4, 5],
  "devices": [10, 15, 20]
}
```

#### Retrieve ServiceNow Group
```
GET /api/plugins/service-now-groups/groups/{id}/
```

#### Update ServiceNow Group
```
PUT /api/plugins/service-now-groups/groups/{id}/
PATCH /api/plugins/service-now-groups/groups/{id}/
```

#### Delete ServiceNow Group
```
DELETE /api/plugins/service-now-groups/groups/{id}/
```

#### Custom Actions

##### Check Device Association
```
POST /api/plugins/service-now-groups/groups/{id}/check-device-association/
```

**Request Body**:
```json
{
  "device_id": 10
}
```

##### Get Group Statistics
```
GET /api/plugins/service-now-groups/groups/{id}/statistics/
```

### Response Format

All API responses follow the Nautobot REST API format:

```json
{
  "id": 1,
  "name": "Network_Engineers",
  "description": "Network engineering team",
  "locations": [
    {
      "id": 1,
      "name": "HQ",
      "url": "/api/dcim/locations/1/"
    }
  ],
  "dynamic_groups": [
    {
      "id": 3,
      "name": "Core Switches",
      "url": "/api/extras/dynamic-groups/3/"
    }
  ],
  "devices": [
    {
      "id": 10,
      "name": "switch-core-01",
      "url": "/api/dcim/devices/10/"
    }
  ],
  "assigned_device_count": 25,
  "created": "2024-01-15T10:30:00Z",
  "last_updated": "2024-01-15T10:30:00Z"
}
```

## Configuration Options

### Plugin Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `enable_change_logging` | `True` | Enable change logging for group assignments |
| `enable_graphql` | `True` | Enable GraphQL queries for ServiceNow groups |
| `enable_admin` | `True` | Enable Django admin interface |
| `default_group_prefix` | `""` | Default prefix for group names |
| `max_groups_per_device` | `None` | Maximum number of groups per device (None = unlimited) |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICENOW_GROUPS_ENABLE_CHANGE_LOGGING` | `True` | Enable change logging |
| `SERVICENOW_GROUPS_ENABLE_GRAPHQL` | `True` | Enable GraphQL |
| `SERVICENOW_GROUPS_ENABLE_ADMIN` | `True` | Enable admin interface |

## Development

### Local Development Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-org/nautobot-servicenow-groups.git
   cd nautobot-servicenow-groups
   ```

2. **Install Development Dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Run Tests**:
   ```bash
   pytest
   ```

4. **Code Quality Checks**:
   ```bash
   make lint
   make format
   make type-check
   ```

5. **Docker Development**:
   ```bash
   docker-compose up -d
   ```

### Project Structure

```
service_now_groups/
├── service_now_groups/
│   ├── __init__.py              # App configuration
│   ├── admin.py                 # Django admin
│   ├── api/                     # REST API
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── migrations/              # Database migrations
│   ├── models.py                # Data models
│   ├── templates/               # UI templates
│   ├── tests/                   # Test suite
│   └── views.py                 # UI views
├── docs/                        # Documentation
├── .github/workflows/           # CI/CD
├── Dockerfile                   # Container build
├── docker-compose.yml           # Local development
└── pyproject.toml              # Project configuration
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_models.py
pytest tests/test_api.py
pytest tests/test_templates.py

# Run with coverage
pytest --cov=service_now_groups --cov-report=html

# Run integration tests
pytest -m integration
```

### Test Data

The test suite includes factory classes for creating test data:

```python
from service_now_groups.tests.factories import ServiceNowGroupFactory

# Create a test group
group = ServiceNowGroupFactory(name="Test Group")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Development Standards

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain test coverage above 90%
- Follow Nautobot development patterns

## Troubleshooting

### Common Issues

1. **Groups Not Appearing on Device Pages**:
   - Check that the plugin is properly installed and configured
   - Verify device permissions
   - Check browser console for JavaScript errors

2. **API Authentication Errors**:
   - Ensure proper API token configuration
   - Check user permissions for the ServiceNow groups

3. **Database Migration Issues**:
   - Run `nautobot-server migrate --plan` to check migration status
   - Ensure database user has proper permissions

4. **Performance Issues**:
   - Check database query performance
   - Consider adding database indexes for large datasets
   - Monitor Redis cache usage

### Debug Mode

Enable debug mode for detailed error information:

```python
DEBUG = True
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs.nautobot.com](https://docs.nautobot.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/nautobot-servicenow-groups/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/nautobot-servicenow-groups/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## Acknowledgments

- Nautobot team for the excellent platform
- Django community for the robust framework
- ServiceNow community for integration patterns 