# Migration Guide

## Overview

This guide provides step-by-step instructions for upgrading the ServiceNow Groups Nautobot app between different versions. Follow these instructions carefully to ensure a smooth upgrade process.

## Pre-Upgrade Checklist

Before upgrading, ensure you have:

- [ ] **Backup your database** - Always create a backup before upgrading
- [ ] **Test in a staging environment** - Test the upgrade process in a non-production environment first
- [ ] **Review release notes** - Check the [CHANGELOG.md](../CHANGELOG.md) for breaking changes
- [ ] **Check compatibility** - Verify Nautobot version compatibility
- [ ] **Plan maintenance window** - Schedule downtime if needed

## Backup Procedures

### Database Backup

```bash
# PostgreSQL backup
pg_dump -h your-db-host -U your-db-user -d nautobot > nautobot_backup_$(date +%Y%m%d_%H%M%S).sql

# Or using Nautobot's backup command
nautobot-server backup --output-file nautobot_backup_$(date +%Y%m%d_%H%M%S).json
```

### Configuration Backup

```bash
# Backup your configuration files
cp nautobot_config.py nautobot_config.py.backup
cp .env .env.backup
```

### Docker Backup (if using containers)

```bash
# Backup Docker volumes
docker run --rm -v nautobot_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

## Version Compatibility Matrix

| ServiceNow Groups Version | Nautobot Version | Python Version | Django Version |
|---------------------------|------------------|----------------|----------------|
| 1.0.0                     | 1.5.0 - 2.0.0   | 3.8 - 3.11     | 3.2 - 4.2      |
| 0.1.0                     | 1.5.0 - 1.6.0   | 3.8 - 3.10     | 3.2 - 4.0      |

## Upgrade Paths

### From 0.1.0 to 1.0.0

This is a major version upgrade with significant changes.

#### Breaking Changes

1. **Database Schema Changes**: New fields and relationships added
2. **API Changes**: Some endpoint URLs and response formats changed
3. **Configuration Changes**: New plugin settings added
4. **Permission Changes**: New permissions required for some features

#### Upgrade Steps

1. **Stop Nautobot Services**
   ```bash
   # If using systemd
   sudo systemctl stop nautobot
   
   # If using Docker
   docker-compose down
   ```

2. **Update the Package**
   ```bash
   # Uninstall old version
   pip uninstall nautobot-servicenow-groups
   
   # Install new version
   pip install nautobot-servicenow-groups==1.0.0
   ```

3. **Update Configuration**
   
   Add new plugin settings to your `nautobot_config.py`:
   ```python
   PLUGINS_CONFIG = {
       "service_now_groups": {
           "enable_change_logging": True,
           "enable_graphql": True,
           "enable_admin": True,
           "default_group_prefix": "SN_",
           "max_groups_per_device": 10,
           "require_description": False,
           "include_child_locations": True,
           "include_dynamic_group_children": True,
           "cache_timeout": 300,
           "max_assignment_depth": 5,
           "show_assignment_methods": True,
           "show_device_count": True,
           "enable_bulk_operations": True,
       }
   }
   ```

4. **Run Database Migrations**
   ```bash
   nautobot-server migrate
   ```

5. **Collect Static Files**
   ```bash
   nautobot-server collectstatic --noinput
   ```

6. **Update Permissions**
   ```bash
   # Create new permissions for existing users
   nautobot-server shell -c "
   from django.contrib.auth.models import Group, Permission
   from django.contrib.contenttypes.models import ContentType
   from service_now_groups.models import ServiceNowGroup
   
   # Get content type for ServiceNowGroup
   ct = ContentType.objects.get_for_model(ServiceNowGroup)
   
   # Get all permissions for ServiceNowGroup
   permissions = Permission.objects.filter(content_type=ct)
   
   # Add permissions to admin group
   admin_group, created = Group.objects.get_or_create(name='Admin')
   admin_group.permissions.add(*permissions)
   print('Permissions updated successfully')
   "
   ```

7. **Verify Installation**
   ```bash
   # Check if plugin is loaded
   nautobot-server shell -c "
   from django.conf import settings
   print('service_now_groups' in settings.PLUGINS)
   "
   
   # Check database tables
   nautobot-server shell -c "
   from django.db import connection
   with connection.cursor() as cursor:
       cursor.execute(\"\"\"
           SELECT table_name 
           FROM information_schema.tables 
           WHERE table_schema = 'public' 
           AND table_name LIKE 'service_now_groups%'
       \"\"\")
       tables = cursor.fetchall()
       print('ServiceNow Groups tables:', [t[0] for t in tables])
   "
   ```

8. **Start Services**
   ```bash
   # If using systemd
   sudo systemctl start nautobot
   
   # If using Docker
   docker-compose up -d
   ```

9. **Test Functionality**
   - Access the admin interface and verify ServiceNow Groups are visible
   - Test API endpoints
   - Verify device detail pages show ServiceNow groups
   - Test creating and editing groups

#### Post-Upgrade Tasks

1. **Review and Update Customizations**
   - Check if any custom templates need updates
   - Verify custom API integrations still work
   - Update any custom scripts that use the API

2. **Monitor Logs**
   ```bash
   # Check for any errors
   tail -f /var/log/nautobot/nautobot.log | grep -i error
   
   # Check plugin-specific logs
   tail -f /var/log/nautobot/servicenow_groups.log
   ```

3. **Performance Monitoring**
   - Monitor database query performance
   - Check cache hit rates
   - Monitor API response times

### From Development/Alpha to 1.0.0

If you're upgrading from a development or alpha version:

1. **Export Data** (if needed)
   ```bash
   nautobot-server shell -c "
   from service_now_groups.models import ServiceNowGroup
   import json
   
   groups = ServiceNowGroup.objects.all()
   data = []
   for group in groups:
       data.append({
           'name': group.name,
           'description': group.description,
           'locations': [loc.name for loc in group.locations.all()],
           'dynamic_groups': [dg.name for dg in group.dynamic_groups.all()],
           'devices': [dev.name for dev in group.devices.all()],
       })
   
   with open('servicenow_groups_backup.json', 'w') as f:
       json.dump(data, f, indent=2)
   print(f'Exported {len(data)} groups')
   "
   ```

2. **Uninstall Old Version**
   ```bash
   pip uninstall nautobot-servicenow-groups
   ```

3. **Clean Database** (if needed)
   ```bash
   nautobot-server shell -c "
   from django.db import connection
   with connection.cursor() as cursor:
       cursor.execute('DROP TABLE IF EXISTS service_now_groups_servicenowgroup CASCADE')
       cursor.execute('DROP TABLE IF EXISTS service_now_groups_servicenowgroup_locations CASCADE')
       cursor.execute('DROP TABLE IF EXISTS service_now_groups_servicenowgroup_dynamic_groups CASCADE')
       cursor.execute('DROP TABLE IF EXISTS service_now_groups_servicenowgroup_devices CASCADE')
   print('Old tables dropped')
   "
   ```

4. **Follow the 1.0.0 installation steps above**

## Containerized Upgrades

### Docker Compose Upgrade

1. **Backup Current Setup**
   ```bash
   # Backup volumes
   docker run --rm -v nautobot_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
   
   # Backup configuration
   cp docker-compose.yml docker-compose.yml.backup
   cp .env .env.backup
   ```

2. **Update Docker Image**
   ```bash
   # Pull new image
   docker pull nautobot-servicenow-groups:1.0.0
   
   # Or rebuild locally
   docker-compose build --no-cache
   ```

3. **Update Configuration**
   ```bash
   # Update environment variables
   cp env.example .env
   # Edit .env with your specific values
   ```

4. **Run Upgrade**
   ```bash
   # Start services
   docker-compose up -d
   
   # Run migrations
   docker-compose exec nautobot nautobot-server migrate
   
   # Collect static files
   docker-compose exec nautobot nautobot-server collectstatic --noinput
   ```

### Kubernetes Upgrade

1. **Backup Current Deployment**
   ```bash
   # Backup current configuration
   kubectl get deployment nautobot -o yaml > nautobot-deployment-backup.yaml
   kubectl get configmap nautobot-config -o yaml > nautobot-config-backup.yaml
   ```

2. **Update Image**
   ```bash
   # Update deployment
   kubectl set image deployment/nautobot nautobot=nautobot-servicenow-groups:1.0.0
   
   # Or update the deployment YAML and apply
   kubectl apply -f k8s-deployment.yaml
   ```

3. **Run Migrations**
   ```bash
   # Create a job to run migrations
   kubectl create job --from=cronjob/migration-job migration-manual
   ```

## Troubleshooting Upgrades

### Common Issues

1. **Migration Errors**
   ```bash
   # Check migration status
   nautobot-server showmigrations service_now_groups
   
   # Reset migrations if needed (DANGEROUS - backup first!)
   nautobot-server shell -c "
   from django.db import connection
   with connection.cursor() as cursor:
       cursor.execute('DELETE FROM django_migrations WHERE app = \"service_now_groups\"')
   "
   nautobot-server migrate service_now_groups
   ```

2. **Permission Errors**
   ```bash
   # Recreate permissions
   nautobot-server shell -c "
   from django.contrib.auth.models import Group, Permission
   from django.contrib.contenttypes.models import ContentType
   from service_now_groups.models import ServiceNowGroup
   
   ct = ContentType.objects.get_for_model(ServiceNowGroup)
   permissions = Permission.objects.filter(content_type=ct)
   
   admin_group = Group.objects.get(name='Admin')
   admin_group.permissions.add(*permissions)
   "
   ```

3. **Import Errors**
   ```bash
   # Check if plugin is properly installed
   nautobot-server shell -c "
   import service_now_groups
   print('Plugin imported successfully')
   "
   ```

4. **Database Connection Issues**
   ```bash
   # Test database connection
   nautobot-server dbshell -c "SELECT version();"
   
   # Check database permissions
   nautobot-server shell -c "
   from django.db import connection
   with connection.cursor() as cursor:
       cursor.execute('SELECT current_user, current_database()')
       print(cursor.fetchone())
   "
   ```

### Rollback Procedures

If the upgrade fails, you can rollback:

1. **Stop Services**
   ```bash
   docker-compose down
   # or
   sudo systemctl stop nautobot
   ```

2. **Restore Database**
   ```bash
   # PostgreSQL restore
   psql -h your-db-host -U your-db-user -d nautobot < nautobot_backup_$(date).sql
   
   # Or Nautobot restore
   nautobot-server restore --input-file nautobot_backup_$(date).json
   ```

3. **Restore Configuration**
   ```bash
   cp nautobot_config.py.backup nautobot_config.py
   cp .env.backup .env
   ```

4. **Reinstall Old Version**
   ```bash
   pip uninstall nautobot-servicenow-groups
   pip install nautobot-servicenow-groups==0.1.0
   ```

5. **Start Services**
   ```bash
   docker-compose up -d
   # or
   sudo systemctl start nautobot
   ```

## Post-Upgrade Verification

After upgrading, verify the following:

1. **Plugin Loading**
   - Check that the plugin appears in the admin interface
   - Verify API endpoints are accessible

2. **Data Integrity**
   - Check that existing ServiceNow groups are still present
   - Verify device associations are correct
   - Test creating new groups

3. **Performance**
   - Monitor response times for API calls
   - Check database query performance
   - Verify caching is working

4. **Functionality**
   - Test all CRUD operations
   - Verify UI integration on device pages
   - Test bulk operations if enabled

## Support

If you encounter issues during the upgrade process:

1. **Check the logs** for error messages
2. **Review the troubleshooting section** above
3. **Search existing issues** on GitHub
4. **Create a new issue** with detailed information:
   - Current version and target version
   - Error messages and logs
   - Steps to reproduce
   - Environment details

## Migration Checklist

- [ ] Backup database and configuration
- [ ] Test upgrade in staging environment
- [ ] Update package to new version
- [ ] Update configuration files
- [ ] Run database migrations
- [ ] Collect static files
- [ ] Update permissions
- [ ] Verify plugin loading
- [ ] Test functionality
- [ ] Monitor performance
- [ ] Update documentation
- [ ] Notify users of changes 