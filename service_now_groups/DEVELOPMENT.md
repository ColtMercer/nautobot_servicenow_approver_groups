# ServiceNow Groups Development Guide

This document outlines the development standards and workflow for the ServiceNow Groups Nautobot app.

## Development Setup

### Prerequisites
- Python 3.8+
- pip
- git

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd service_now_groups

# Install development dependencies
make install
```

## Code Quality Standards

### Code Formatting
We use the following tools to maintain consistent code formatting:

- **Black**: Code formatter (line length: 120)
- **isort**: Import sorting (Black profile)
- **flake8**: Linting (max line length: 120)

### Type Hints
All new code should include type hints:
- Function parameters and return types
- Class attributes
- Variable annotations where helpful

### Documentation
- All public functions and classes must have docstrings
- Use Google-style docstrings
- Include type information in docstrings

### Testing
- Write tests for all new functionality
- Maintain test coverage above 90%
- Use descriptive test names
- Group related tests in classes

## Development Workflow

### Pre-commit Hooks
Pre-commit hooks are automatically installed and run on every commit:
- Code formatting (black, isort)
- Linting (flake8)
- Type checking (mypy)
- Security scanning (bandit)

### Running Quality Checks
```bash
# Format code
make format

# Run linting
make lint

# Run type checking
make type-check

# Run security checks
make security

# Run all quality checks
make quality
```

### Testing
```bash
# Run all tests with coverage
make test

# Run tests without coverage
make test-fast

# Run specific test file
pytest service_now_groups/tests/test_models.py

# Run tests with specific markers
pytest -m "unit"
pytest -m "integration"
```

### CI Pipeline
The CI pipeline runs the following checks:
1. Code formatting (black, isort)
2. Linting (flake8)
3. Type checking (mypy)
4. Security scanning (bandit)
5. Unit tests
6. Integration tests

## Code Style Guidelines

### Python
- Follow PEP 8 with modifications for 120-character line length
- Use type hints for all function signatures
- Use f-strings for string formatting
- Use list/dict comprehensions where appropriate
- Use context managers for resource management

### Django/Nautobot
- Follow Django best practices
- Use Nautobot's model patterns and conventions
- Use proper model validation
- Use select_related/prefetch_related for database optimization
- Use Django's built-in security features

### API Development
- Follow REST API conventions
- Use proper HTTP status codes
- Implement proper error handling
- Use serializers for data validation
- Document API endpoints

### Template Development
- Use Django template best practices
- Keep templates simple and readable
- Use template tags and filters appropriately
- Follow Nautobot's UI patterns

## Security Guidelines

### Input Validation
- Always validate user input
- Use Django forms and serializers
- Sanitize data before database operations
- Use parameterized queries

### Authentication & Authorization
- Use Django's authentication system
- Implement proper permission checks
- Use Nautobot's permission patterns
- Never trust client-side validation

### Data Protection
- Use HTTPS in production
- Implement proper CSRF protection
- Use secure session management
- Follow OWASP guidelines

## Performance Guidelines

### Database Optimization
- Use select_related and prefetch_related
- Minimize database queries
- Use database indexes appropriately
- Monitor query performance

### Caching
- Use Django's caching framework
- Cache expensive operations
- Use appropriate cache timeouts
- Monitor cache hit rates

### Code Optimization
- Profile code for bottlenecks
- Use efficient algorithms
- Avoid unnecessary object creation
- Use generators for large datasets

## Release Process

### Version Management
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version in pyproject.toml
- Update CHANGELOG.md
- Tag releases in git

### Testing Before Release
1. Run full test suite
2. Run quality checks
3. Test in clean environment
4. Verify documentation
5. Check security scan results

### Release Checklist
- [ ] All tests pass
- [ ] Code quality checks pass
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Version is updated
- [ ] Security scan is clean
- [ ] Performance is acceptable

## Troubleshooting

### Common Issues

#### Pre-commit Hooks Fail
```bash
# Update pre-commit hooks
pre-commit autoupdate

# Run hooks manually
pre-commit run --all-files
```

#### Type Checking Errors
```bash
# Run mypy with more details
mypy service_now_groups/ --show-error-codes

# Add type ignores where appropriate
# type: ignore[import]
```

#### Test Failures
```bash
# Run tests with verbose output
pytest -v

# Run specific test with debug output
pytest -v -s service_now_groups/tests/test_models.py::TestClass::test_method
```

## Contributing

### Pull Request Process
1. Create feature branch from main
2. Make changes following coding standards
3. Add tests for new functionality
4. Update documentation
5. Run quality checks
6. Submit pull request
7. Address review feedback
8. Merge after approval

### Commit Messages
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types: feat, fix, docs, style, refactor, test, chore

### Code Review Guidelines
- Review for functionality
- Check code quality
- Verify test coverage
- Ensure documentation is updated
- Check for security issues
- Verify performance impact 