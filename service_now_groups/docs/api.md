# ServiceNow Groups API Documentation

## Overview

The ServiceNow Groups API provides RESTful endpoints for managing ServiceNow group associations with Nautobot devices. All endpoints follow Nautobot's REST API conventions and support standard HTTP methods.

## Authentication

All API requests require authentication using Nautobot API tokens:

```bash
curl -H "Authorization: Token your-api-token" \
     http://your-nautobot/api/plugins/service-now-groups/groups/
```

## Base URL

```
http://your-nautobot/api/plugins/service-now-groups/
```

## Endpoints

### ServiceNow Groups

#### List ServiceNow Groups

Retrieve a list of all ServiceNow groups with optional filtering.

**Endpoint:** `GET /groups/`

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `name` | string | Filter by group name (exact match) | `?name=Network_Engineers` |
| `name__icontains` | string | Filter by group name (case-insensitive contains) | `?name__icontains=network` |
| `location` | integer | Filter by location ID | `?location=1` |
| `dynamic_group` | integer | Filter by dynamic group ID | `?dynamic_group=3` |
| `device` | integer | Filter by device ID | `?device=10` |
| `search` | string | Search across name and description | `?search=engineering` |
| `limit` | integer | Number of results to return (max 1000) | `?limit=50` |
| `offset` | integer | Number of results to skip | `?offset=100` |

**Example Request:**

```bash
curl -H "Authorization: Token your-token" \
     "http://your-nautobot/api/plugins/service-now-groups/groups/?name__icontains=network&limit=10"
```

**Example Response:**

```json
{
  "count": 25,
  "next": "http://your-nautobot/api/plugins/service-now-groups/groups/?limit=10&offset=10",
  "previous": null,
  "results": [
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
  ]
}
```

#### Create ServiceNow Group

Create a new ServiceNow group.

**Endpoint:** `POST /groups/`

**Request Body:**

```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "locations": [1, 2, 3],
  "dynamic_groups": [4, 5],
  "devices": [10, 15, 20]
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique name for the ServiceNow group |
| `description` | string | No | Optional description of the group's purpose |
| `locations` | array | No | Array of location IDs to assign all devices in those locations |
| `dynamic_groups` | array | No | Array of dynamic group IDs to assign all devices in those groups |
| `devices` | array | No | Array of device IDs for explicit device assignment |

**Example Request:**

```bash
curl -X POST \
     -H "Authorization: Token your-token" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Network_Engineers",
       "description": "Network engineering team for core infrastructure",
       "locations": [1, 2],
       "dynamic_groups": [3],
       "devices": [10, 15, 20]
     }' \
     http://your-nautobot/api/plugins/service-now-groups/groups/
```

**Example Response:**

```json
{
  "id": 1,
  "name": "Network_Engineers",
  "description": "Network engineering team for core infrastructure",
  "locations": [
    {
      "id": 1,
      "name": "HQ",
      "url": "/api/dcim/locations/1/"
    },
    {
      "id": 2,
      "name": "Branch Office",
      "url": "/api/dcim/locations/2/"
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
    },
    {
      "id": 15,
      "name": "switch-core-02",
      "url": "/api/dcim/devices/15/"
    },
    {
      "id": 20,
      "name": "router-core-01",
      "url": "/api/dcim/devices/20/"
    }
  ],
  "assigned_device_count": 45,
  "created": "2024-01-15T10:30:00Z",
  "last_updated": "2024-01-15T10:30:00Z"
}
```

#### Retrieve ServiceNow Group

Get details of a specific ServiceNow group.

**Endpoint:** `GET /groups/{id}/`

**Example Request:**

```bash
curl -H "Authorization: Token your-token" \
     http://your-nautobot/api/plugins/service-now-groups/groups/1/
```

**Example Response:**

```json
{
  "id": 1,
  "name": "Network_Engineers",
  "description": "Network engineering team for core infrastructure",
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

#### Update ServiceNow Group

Update an existing ServiceNow group.

**Endpoint:** `PUT /groups/{id}/` or `PATCH /groups/{id}/`

**Request Body:**

For `PUT` requests, include all fields. For `PATCH` requests, include only the fields to update.

```json
{
  "name": "Updated_Network_Engineers",
  "description": "Updated description",
  "locations": [1, 2, 3],
  "dynamic_groups": [4, 5],
  "devices": [10, 15, 20]
}
```

**Example Request:**

```bash
curl -X PATCH \
     -H "Authorization: Token your-token" \
     -H "Content-Type: application/json" \
     -d '{
       "description": "Updated network engineering team description"
     }' \
     http://your-nautobot/api/plugins/service-now-groups/groups/1/
```

#### Delete ServiceNow Group

Delete a ServiceNow group.

**Endpoint:** `DELETE /groups/{id}/`

**Example Request:**

```bash
curl -X DELETE \
     -H "Authorization: Token your-token" \
     http://your-nautobot/api/plugins/service-now-groups/groups/1/
```

**Response:** 204 No Content

### Custom Actions

#### Check Device Association

Check if a specific device is associated with a ServiceNow group.

**Endpoint:** `POST /groups/{id}/check-device-association/`

**Request Body:**

```json
{
  "device_id": 10
}
```

**Example Request:**

```bash
curl -X POST \
     -H "Authorization: Token your-token" \
     -H "Content-Type: application/json" \
     -d '{"device_id": 10}' \
     http://your-nautobot/api/plugins/service-now-groups/groups/1/check-device-association/
```

**Example Response:**

```json
{
  "is_associated": true,
  "assignment_methods": [
    {
      "method": "explicit_device",
      "description": "Device explicitly assigned to this group"
    },
    {
      "method": "location",
      "description": "Device located in HQ (ID: 1)"
    }
  ],
  "device": {
    "id": 10,
    "name": "switch-core-01",
    "url": "/api/dcim/devices/10/"
  }
}
```

#### Get Group Statistics

Get statistics about a ServiceNow group.

**Endpoint:** `GET /groups/{id}/statistics/`

**Example Request:**

```bash
curl -H "Authorization: Token your-token" \
     http://your-nautobot/api/plugins/service-now-groups/groups/1/statistics/
```

**Example Response:**

```json
{
  "total_devices": 25,
  "devices_by_assignment_method": {
    "explicit_device": 5,
    "dynamic_group": 15,
    "location": 10
  },
  "locations_count": 2,
  "dynamic_groups_count": 1,
  "explicit_devices_count": 5,
  "created_date": "2024-01-15T10:30:00Z",
  "last_updated": "2024-01-15T10:30:00Z"
}
```

## Error Handling

### Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Resource deleted successfully |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource conflict (e.g., duplicate name) |
| 500 | Internal Server Error - Server error |

### Example Error Responses

**400 Bad Request - Validation Error:**

```json
{
  "name": ["This field is required."],
  "locations": ["Invalid location ID: 999"]
}
```

**409 Conflict - Duplicate Name:**

```json
{
  "detail": "A ServiceNow group with this name already exists."
}
```

**404 Not Found:**

```json
{
  "detail": "Not found."
}
```

## Rate Limiting

API requests are subject to rate limiting:

- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

## Pagination

List endpoints support pagination with the following query parameters:

- `limit`: Number of results per page (max 1000)
- `offset`: Number of results to skip

**Example:**

```bash
curl "http://your-nautobot/api/plugins/service-now-groups/groups/?limit=10&offset=20"
```

**Response includes pagination metadata:**

```json
{
  "count": 100,
  "next": "http://your-nautobot/api/plugins/service-now-groups/groups/?limit=10&offset=30",
  "previous": "http://your-nautobot/api/plugins/service-now-groups/groups/?limit=10&offset=10",
  "results": [...]
}
```

## Bulk Operations

### Bulk Create

Create multiple ServiceNow groups in a single request.

**Endpoint:** `POST /groups/bulk-create/`

**Request Body:**

```json
{
  "groups": [
    {
      "name": "Network_Engineers",
      "description": "Network engineering team",
      "locations": [1, 2]
    },
    {
      "name": "Security_Team",
      "description": "Security operations team",
      "dynamic_groups": [3]
    }
  ]
}
```

### Bulk Update

Update multiple ServiceNow groups in a single request.

**Endpoint:** `POST /groups/bulk-update/`

**Request Body:**

```json
{
  "groups": [
    {
      "id": 1,
      "description": "Updated description"
    },
    {
      "id": 2,
      "locations": [1, 2, 3]
    }
  ]
}
```

### Bulk Delete

Delete multiple ServiceNow groups in a single request.

**Endpoint:** `POST /groups/bulk-delete/`

**Request Body:**

```json
{
  "ids": [1, 2, 3]
}
```

## Usage Examples

### Python Client Example

```python
import requests

# Configuration
NAUTOBOT_URL = "http://your-nautobot"
API_TOKEN = "your-api-token"
HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

# Create a new group
def create_group(name, description, locations=None, dynamic_groups=None, devices=None):
    data = {
        "name": name,
        "description": description
    }
    if locations:
        data["locations"] = locations
    if dynamic_groups:
        data["dynamic_groups"] = dynamic_groups
    if devices:
        data["devices"] = devices
    
    response = requests.post(
        f"{NAUTOBOT_URL}/api/plugins/service-now-groups/groups/",
        headers=HEADERS,
        json=data
    )
    return response.json()

# Get groups for a specific device
def get_device_groups(device_id):
    response = requests.get(
        f"{NAUTOBOT_URL}/api/plugins/service-now-groups/groups/",
        headers=HEADERS,
        params={"device": device_id}
    )
    return response.json()

# Check if device is associated with a group
def check_device_association(group_id, device_id):
    response = requests.post(
        f"{NAUTOBOT_URL}/api/plugins/service-now-groups/groups/{group_id}/check-device-association/",
        headers=HEADERS,
        json={"device_id": device_id}
    )
    return response.json()
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

// Configuration
const NAUTOBOT_URL = 'http://your-nautobot';
const API_TOKEN = 'your-api-token';

const api = axios.create({
    baseURL: `${NAUTOBOT_URL}/api/plugins/service-now-groups`,
    headers: {
        'Authorization': `Token ${API_TOKEN}`,
        'Content-Type': 'application/json'
    }
});

// Create a new group
async function createGroup(name, description, locations = [], dynamicGroups = [], devices = []) {
    try {
        const response = await api.post('/groups/', {
            name,
            description,
            locations,
            dynamic_groups: dynamicGroups,
            devices
        });
        return response.data;
    } catch (error) {
        console.error('Error creating group:', error.response.data);
        throw error;
    }
}

// Get all groups
async function getGroups(params = {}) {
    try {
        const response = await api.get('/groups/', { params });
        return response.data;
    } catch (error) {
        console.error('Error getting groups:', error.response.data);
        throw error;
    }
}

// Check device association
async function checkDeviceAssociation(groupId, deviceId) {
    try {
        const response = await api.post(`/groups/${groupId}/check-device-association/`, {
            device_id: deviceId
        });
        return response.data;
    } catch (error) {
        console.error('Error checking association:', error.response.data);
        throw error;
    }
}
```

## Best Practices

1. **Use PATCH for Updates**: Use PATCH requests when updating only specific fields to avoid overwriting unchanged data.

2. **Handle Pagination**: Always handle pagination for list endpoints to avoid memory issues with large datasets.

3. **Validate Responses**: Check HTTP status codes and handle error responses appropriately.

4. **Use Bulk Operations**: Use bulk operations when creating, updating, or deleting multiple groups to improve performance.

5. **Cache Results**: Cache frequently accessed data to reduce API calls and improve performance.

6. **Monitor Rate Limits**: Respect rate limits and implement exponential backoff for retries.

7. **Error Handling**: Implement proper error handling for network issues and API errors.

## Support

For API support and questions:

- **Documentation**: [docs.nautobot.com](https://docs.nautobot.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/nautobot-servicenow-groups/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/nautobot-servicenow-groups/discussions) 