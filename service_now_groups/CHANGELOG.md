# Changelog

All notable changes to the ServiceNow Groups Nautobot app will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial development version
- ServiceNowGroup model with dynamic assignment logic
- REST API with full CRUD operations
- Django admin interface
- UI integration with device detail pages
- Comprehensive test suite
- Code quality tools and pre-commit hooks
- CI/CD pipeline with GitHub Actions
- Docker containerization support
- Documentation and configuration guides

## [1.0.0] - 2024-01-15

### Added
- **ServiceNowGroup Model**: Core model for managing ServiceNow group associations
  - Dynamic assignment based on location, dynamic groups, and explicit devices
  - Hierarchical location assignment with child location support
  - Validation and constraint checking
  - Change logging and audit trail

- **REST API**: Complete API implementation
  - Full CRUD operations for ServiceNow groups
  - Advanced filtering and search capabilities
  - Custom actions for device association checking
  - Bulk operations support
  - Comprehensive error handling and validation

- **Django Admin Interface**: Administrative interface
  - List view with device counts and assignment summaries
  - Advanced filtering and search
  - Custom admin actions for CSV export and validation
  - Organized fieldsets with collapsible sections

- **UI Extensions**: User interface integration
  - Device detail page integration with ServiceNow groups section
  - Template tags and filters for dynamic content
  - List and detail views for ServiceNow groups
  - Responsive design with Bootstrap styling

- **Testing Framework**: Comprehensive test suite
  - Model tests covering validation and assignment logic
  - API tests for CRUD operations and permissions
  - Template tests for UI rendering and integration
  - Integration tests for complex scenarios
  - Factory classes for test data setup

- **Code Quality Tools**: Development standards enforcement
  - Black for code formatting
  - isort for import sorting
  - flake8 for linting
  - mypy for type checking
  - bandit for security scanning
  - Pre-commit hooks for automated enforcement

- **CI/CD Pipeline**: Automated testing and deployment
  - GitHub Actions workflow with multi-stage testing
  - Code quality checks and security scanning
  - Multi-version compatibility testing (Python 3.8-3.11, Nautobot 1.5.0-2.0.0)
  - Automated package building and PyPI publishing
  - Docker containerization with health checks

- **Documentation**: Comprehensive documentation
  - Detailed README with installation and usage instructions
  - Complete API documentation with examples
  - Configuration guide with all settings and options
  - Development guide with standards and workflow
  - Troubleshooting guide with common issues

### Features
- **Dynamic Assignment Logic**: Intelligent device-to-group assignment
  - Location-based assignment with hierarchy support
  - Dynamic group membership assignment
  - Explicit device assignment for specific cases
  - Multiple assignment methods per device

- **Performance Optimizations**: Efficient data handling
  - Database query optimization with prefetch_related
  - Redis caching for frequently accessed data
  - Bulk operations for large-scale changes
  - Background task processing for heavy operations

- **Security Features**: Comprehensive security measures
  - Permission-based access control
  - API token authentication
  - Rate limiting and request validation
  - Input sanitization and validation

- **Monitoring and Observability**: Operational insights
  - Health check endpoints
  - Metrics collection and reporting
  - Comprehensive logging with configurable levels
  - Performance monitoring and alerting

### Technical Specifications
- **Python Compatibility**: 3.8, 3.9, 3.10, 3.11
- **Nautobot Compatibility**: 1.5.0, 1.6.0, 2.0.0
- **Database Support**: PostgreSQL (primary), MySQL (experimental)
- **Cache Support**: Redis (recommended), Memcached (supported)
- **Container Support**: Docker, Docker Compose, Kubernetes

### Installation
```bash
# Install from PyPI
pip install nautobot-servicenow-groups

# Or install from source
git clone https://github.com/your-org/nautobot-servicenow-groups.git
cd nautobot-servicenow-groups
pip install -e .
```

### Configuration
```python
# nautobot_config.py
PLUGINS = ["service_now_groups"]

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

### Migration Guide
This is the initial release, so no migration is required for existing installations.

### Breaking Changes
None - this is the initial release.

### Deprecations
None - this is the initial release.

## [0.1.0] - 2024-01-01

### Added
- Initial alpha release for testing and feedback
- Basic ServiceNowGroup model implementation
- Simple REST API endpoints
- Basic Django admin interface
- Initial documentation

### Known Issues
- Limited error handling in early alpha version
- Performance optimizations not yet implemented
- UI styling needs refinement
- Test coverage incomplete

## Version History

### Version Numbering
This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

### Release Schedule
- **Major releases**: As needed for breaking changes
- **Minor releases**: Monthly for new features
- **Patch releases**: Weekly for bug fixes and security updates

### Support Policy
- **Current version**: Full support
- **Previous major version**: Security fixes only
- **Older versions**: No support

## Contributing

### Reporting Issues
- Use [GitHub Issues](https://github.com/your-org/nautobot-servicenow-groups/issues)
- Include version information and detailed reproduction steps
- Provide logs and error messages when applicable

### Feature Requests
- Use [GitHub Discussions](https://github.com/your-org/nautobot-servicenow-groups/discussions)
- Describe the use case and expected behavior
- Consider implementation complexity and maintenance burden

### Pull Requests
- Follow the [Development Guide](DEVELOPMENT.md)
- Include tests for new functionality
- Update documentation as needed
- Ensure all CI checks pass

## Acknowledgments

### Contributors
- Initial development team
- Community contributors and testers
- Nautobot team for the excellent platform

### Dependencies
- [Nautobot](https://github.com/nautobot/nautobot) - The network automation platform
- [Django](https://www.djangoproject.com/) - The web framework
- [Django REST Framework](https://www.django-rest-framework.org/) - API framework
- [pytest](https://pytest.org/) - Testing framework
- [Black](https://black.readthedocs.io/) - Code formatter
- [isort](https://pycqa.github.io/isort/) - Import sorter
- [flake8](https://flake8.pycqa.org/) - Linter
- [mypy](https://mypy.readthedocs.io/) - Type checker
- [bandit](https://bandit.readthedocs.io/) - Security linter

### License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Links

- **Documentation**: [docs.nautobot.com](https://docs.nautobot.com)
- **Source Code**: [GitHub Repository](https://github.com/your-org/nautobot-servicenow-groups)
- **Issues**: [GitHub Issues](https://github.com/your-org/nautobot-servicenow-groups/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/nautobot-servicenow-groups/discussions)
- **PyPI**: [nautobot-servicenow-groups](https://pypi.org/project/nautobot-servicenow-groups/) 