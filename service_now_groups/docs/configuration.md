# ServiceNow Groups Configuration Guide

## Overview

This guide provides detailed configuration options for the ServiceNow Groups Nautobot app, including plugin settings, environment variables, and deployment configurations.

## Plugin Configuration

### Basic Configuration

Add the plugin to your Nautobot configuration:

```python
# nautobot_config.py
PLUGINS = ["service_now_groups"]
```

### Advanced Plugin Settings

Configure plugin behavior using the `PLUGINS_CONFIG` setting:

```python
PLUGINS_CONFIG = {
    "service_now_groups": {
        # Enable/disable features
        "enable_change_logging": True,
        "enable_graphql": True,
        "enable_admin": True,
        
        # Group naming and validation
        "default_group_prefix": "SN_",
        "max_groups_per_device": 10,
        "require_description": False,
        
        # Assignment behavior
        "include_child_locations": True,
        "include_dynamic_group_children": True,
        
        # Performance settings
        "cache_timeout": 300,
        "max_assignment_depth": 5,
        
        # UI settings
        "show_assignment_methods": True,
        "show_device_count": True,
        "enable_bulk_operations": True,
    }
}
```

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enable_change_logging` | bool | `True` | Enable change logging for group assignments |
| `enable_graphql` | bool | `True` | Enable GraphQL queries for ServiceNow groups |
| `enable_admin` | bool | `True` | Enable Django admin interface |
| `default_group_prefix` | str | `""` | Default prefix for group names |
| `max_groups_per_device` | int | `None` | Maximum groups per device (None = unlimited) |
| `require_description` | bool | `False` | Require description when creating groups |
| `include_child_locations` | bool | `True` | Include devices in child locations |
| `include_dynamic_group_children` | bool | `True` | Include devices in dynamic group children |
| `cache_timeout` | int | `300` | Cache timeout in seconds |
| `max_assignment_depth` | int | `5` | Maximum depth for location hierarchy |
| `show_assignment_methods` | bool | `True` | Show assignment methods in UI |
| `show_device_count` | bool | `True` | Show device count in UI |
| `enable_bulk_operations` | bool | `True` | Enable bulk create/update/delete operations |

## Environment Variables

Configure the plugin using environment variables:

```bash
# Feature flags
export SERVICENOW_GROUPS_ENABLE_CHANGE_LOGGING=true
export SERVICENOW_GROUPS_ENABLE_GRAPHQL=true
export SERVICENOW_GROUPS_ENABLE_ADMIN=true

# Group settings
export SERVICENOW_GROUPS_DEFAULT_PREFIX="SN_"
export SERVICENOW_GROUPS_MAX_GROUPS_PER_DEVICE=10
export SERVICENOW_GROUPS_REQUIRE_DESCRIPTION=false

# Assignment behavior
export SERVICENOW_GROUPS_INCLUDE_CHILD_LOCATIONS=true
export SERVICENOW_GROUPS_INCLUDE_DYNAMIC_GROUP_CHILDREN=true

# Performance
export SERVICENOW_GROUPS_CACHE_TIMEOUT=300
export SERVICENOW_GROUPS_MAX_ASSIGNMENT_DEPTH=5

# UI settings
export SERVICENOW_GROUPS_SHOW_ASSIGNMENT_METHODS=true
export SERVICENOW_GROUPS_SHOW_DEVICE_COUNT=true
export SERVICENOW_GROUPS_ENABLE_BULK_OPERATIONS=true
```

### Environment Variable Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SERVICENOW_GROUPS_ENABLE_CHANGE_LOGGING` | bool | `True` | Enable change logging |
| `SERVICENOW_GROUPS_ENABLE_GRAPHQL` | bool | `True` | Enable GraphQL |
| `SERVICENOW_GROUPS_ENABLE_ADMIN` | bool | `True` | Enable admin interface |
| `SERVICENOW_GROUPS_DEFAULT_PREFIX` | str | `""` | Default group name prefix |
| `SERVICENOW_GROUPS_MAX_GROUPS_PER_DEVICE` | int | `None` | Max groups per device |
| `SERVICENOW_GROUPS_REQUIRE_DESCRIPTION` | bool | `False` | Require descriptions |
| `SERVICENOW_GROUPS_INCLUDE_CHILD_LOCATIONS` | bool | `True` | Include child locations |
| `SERVICENOW_GROUPS_INCLUDE_DYNAMIC_GROUP_CHILDREN` | bool | `True` | Include dynamic group children |
| `SERVICENOW_GROUPS_CACHE_TIMEOUT` | int | `300` | Cache timeout (seconds) |
| `SERVICENOW_GROUPS_MAX_ASSIGNMENT_DEPTH` | int | `5` | Max assignment depth |
| `SERVICENOW_GROUPS_SHOW_ASSIGNMENT_METHODS` | bool | `True` | Show assignment methods |
| `SERVICENOW_GROUPS_SHOW_DEVICE_COUNT` | bool | `True` | Show device count |
| `SERVICENOW_GROUPS_ENABLE_BULK_OPERATIONS` | bool | `True` | Enable bulk operations |

## Database Configuration

### PostgreSQL Settings

The plugin works with Nautobot's existing database configuration. For optimal performance, consider these PostgreSQL settings:

```sql
-- Increase work_mem for complex queries
SET work_mem = '256MB';

-- Enable query plan caching
SET plan_cache_mode = 'auto';

-- Optimize for read-heavy workloads
SET shared_preload_libraries = 'pg_stat_statements';
```

### Database Indexes

The plugin automatically creates necessary indexes, but you can add custom indexes for better performance:

```sql
-- Index for location-based queries
CREATE INDEX CONCURRENTLY idx_servicenow_groups_locations 
ON service_now_groups_servicenowgroup_locations (servicenowgroup_id, location_id);

-- Index for dynamic group queries
CREATE INDEX CONCURRENTLY idx_servicenow_groups_dynamic_groups 
ON service_now_groups_servicenowgroup_dynamic_groups (servicenowgroup_id, dynamicgroup_id);

-- Index for device queries
CREATE INDEX CONCURRENTLY idx_servicenow_groups_devices 
ON service_now_groups_servicenowgroup_devices (servicenowgroup_id, device_id);
```

## Redis Configuration

### Caching Settings

Configure Redis caching for improved performance:

```python
# nautobot_config.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "TIMEOUT": 300,
    },
    "servicenow_groups": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "TIMEOUT": 600,
    }
}
```

### Redis Environment Variables

```bash
# Redis connection
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=
export REDIS_DB=0

# Cache settings
export SERVICENOW_GROUPS_CACHE_TIMEOUT=300
export SERVICENOW_GROUPS_CACHE_PREFIX="sng:"
```

## Logging Configuration

### Plugin-Specific Logging

Configure logging for the ServiceNow Groups plugin:

```python
# nautobot_config.py
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "/var/log/nautobot/servicenow_groups.log",
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "service_now_groups": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
```

### Log Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `DEBUG` | Detailed information | Development and troubleshooting |
| `INFO` | General information | Normal operation monitoring |
| `WARNING` | Warning messages | Potential issues |
| `ERROR` | Error messages | Failed operations |
| `CRITICAL` | Critical errors | System failures |

## Security Configuration

### Permission Settings

Configure permissions for ServiceNow Groups:

```python
# nautobot_config.py
PLUGINS_CONFIG = {
    "service_now_groups": {
        # Permission settings
        "require_authentication": True,
        "allow_anonymous_read": False,
        "restrict_admin_access": True,
        
        # API settings
        "enable_api": True,
        "require_api_token": True,
        "api_rate_limit": 1000,
    }
}
```

### Security Environment Variables

```bash
# Security settings
export SERVICENOW_GROUPS_REQUIRE_AUTHENTICATION=true
export SERVICENOW_GROUPS_ALLOW_ANONYMOUS_READ=false
export SERVICENOW_GROUPS_RESTRICT_ADMIN_ACCESS=true
export SERVICENOW_GROUPS_ENABLE_API=true
export SERVICENOW_GROUPS_REQUIRE_API_TOKEN=true
export SERVICENOW_GROUPS_API_RATE_LIMIT=1000
```

## Performance Tuning

### Database Optimization

```python
# nautobot_config.py
DATABASES = {
    "default": {
        # ... existing settings ...
        "OPTIONS": {
            "MAX_CONNS": 20,
            "CONN_MAX_AGE": 300,
        },
    }
}
```

### Cache Optimization

```python
# nautobot_config.py
CACHES = {
    "servicenow_groups": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
        },
        "TIMEOUT": 600,
        "KEY_PREFIX": "sng:",
    }
}
```

### Worker Configuration

For background tasks and bulk operations:

```python
# nautobot_config.py
RQ_QUEUES = {
    "default": {
        "HOST": "localhost",
        "PORT": 6379,
        "DB": 0,
        "PASSWORD": "",
        "DEFAULT_TIMEOUT": 300,
    },
    "servicenow_groups": {
        "HOST": "localhost",
        "PORT": 6379,
        "DB": 1,
        "PASSWORD": "",
        "DEFAULT_TIMEOUT": 600,
    }
}
```

## Deployment Configurations

### Docker Deployment

```yaml
# docker-compose.yml
version: '3.8'
services:
  nautobot:
    image: nautobot/nautobot:latest
    environment:
      - PLUGINS=service_now_groups
      - SERVICENOW_GROUPS_ENABLE_CHANGE_LOGGING=true
      - SERVICENOW_GROUPS_CACHE_TIMEOUT=300
    volumes:
      - ./nautobot_config.py:/opt/nautobot/nautobot_config.py:ro
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=nautobot
      - POSTGRES_USER=nautobot
      - POSTGRES_PASSWORD=nautobot
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes Deployment

```yaml
# k8s-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: servicenow-groups-config
data:
  PLUGINS: "service_now_groups"
  SERVICENOW_GROUPS_ENABLE_CHANGE_LOGGING: "true"
  SERVICENOW_GROUPS_CACHE_TIMEOUT: "300"
  SERVICENOW_GROUPS_MAX_GROUPS_PER_DEVICE: "10"
```

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nautobot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nautobot
  template:
    metadata:
      labels:
        app: nautobot
    spec:
      containers:
      - name: nautobot
        image: nautobot/nautobot:latest
        envFrom:
        - configMapRef:
            name: servicenow-groups-config
        ports:
        - containerPort: 8080
```

## Monitoring and Health Checks

### Health Check Endpoint

The plugin provides a health check endpoint:

```bash
curl http://your-nautobot/api/plugins/service-now-groups/health/
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected",
  "groups_count": 25,
  "devices_with_groups": 150
}
```

### Metrics

Enable metrics collection:

```python
# nautobot_config.py
PLUGINS_CONFIG = {
    "service_now_groups": {
        "enable_metrics": True,
        "metrics_prefix": "servicenow_groups",
    }
}
```

Available metrics:
- `servicenow_groups_total`: Total number of groups
- `servicenow_groups_devices_total`: Total devices with group assignments
- `servicenow_groups_api_requests_total`: API request count
- `servicenow_groups_cache_hits_total`: Cache hit count
- `servicenow_groups_cache_misses_total`: Cache miss count

## Troubleshooting

### Common Issues

1. **Groups Not Appearing**:
   - Check plugin is enabled in `PLUGINS`
   - Verify database migrations are applied
   - Check user permissions

2. **Performance Issues**:
   - Monitor database query performance
   - Check Redis cache usage
   - Review assignment logic complexity

3. **API Errors**:
   - Verify API token permissions
   - Check rate limiting settings
   - Review request payload format

### Debug Mode

Enable debug mode for detailed logging:

```python
DEBUG = True

LOGGING = {
    "loggers": {
        "service_now_groups": {
            "level": "DEBUG",
        },
    },
}
```

### Database Queries

Monitor database performance:

```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
WHERE query LIKE '%service_now_groups%' 
ORDER BY mean_time DESC;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE tablename LIKE '%servicenow%';
```

## Support

For configuration support:

- **Documentation**: [docs.nautobot.com](https://docs.nautobot.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/nautobot-servicenow-groups/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/nautobot-servicenow-groups/discussions) 