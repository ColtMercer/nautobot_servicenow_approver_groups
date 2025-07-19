"""
Nautobot configuration file for ServiceNow Groups app.

This file contains the configuration settings for running Nautobot with the
ServiceNow Groups app in a containerized environment.
"""

import os
from nautobot.core.settings import *  # noqa: F403

# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("NAUTOBOT_DB_NAME", "nautobot"),
        "USER": os.getenv("NAUTOBOT_DB_USER", "nautobot"),
        "PASSWORD": os.getenv("NAUTOBOT_DB_PASSWORD", "nautobot"),
        "HOST": os.getenv("NAUTOBOT_DB_HOST", "localhost"),
        "PORT": os.getenv("NAUTOBOT_DB_PORT", "5432"),
        "CONN_MAX_AGE": 300,
    }
}

# Redis configuration
REDIS = {
    "tasks": {
        "HOST": os.getenv("NAUTOBOT_REDIS_HOST", "localhost"),
        "PORT": int(os.getenv("NAUTOBOT_REDIS_PORT", "6379")),
        "PASSWORD": os.getenv("NAUTOBOT_REDIS_PASSWORD", ""),
        "DATABASE": 0,
        "SSL": os.getenv("NAUTOBOT_REDIS_SSL", "false").lower() == "true",
    },
    "caching": {
        "HOST": os.getenv("NAUTOBOT_REDIS_HOST", "localhost"),
        "PORT": int(os.getenv("NAUTOBOT_REDIS_PORT", "6379")),
        "PASSWORD": os.getenv("NAUTOBOT_REDIS_PASSWORD", ""),
        "DATABASE": 1,
        "SSL": os.getenv("NAUTOBOT_REDIS_SSL", "false").lower() == "true",
    },
}

# Secret key
SECRET_KEY = os.getenv("NAUTOBOT_SECRET_KEY", "your-secret-key-here")

# Allowed hosts
ALLOWED_HOSTS = os.getenv("NAUTOBOT_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Debug mode
DEBUG = os.getenv("NAUTOBOT_DEBUG", "false").lower() == "true"

# Plugins
PLUGINS = ["service_now_groups"]

# Plugin settings
PLUGINS_CONFIG = {
    "service_now_groups": {
        "enable_change_logging": True,
        "enable_graphql": True,
        "enable_admin": True,
    }
}

# Set all paths to writable locations within the container
GIT_ROOT = "/app/git"
STATIC_ROOT = "/app/static"
MEDIA_ROOT = "/app/media"

# Disable Git integration to avoid permission issues
GIT_SYNC_ENABLED = False 