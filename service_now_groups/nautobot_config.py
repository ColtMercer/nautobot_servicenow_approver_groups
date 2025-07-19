"""
Nautobot configuration file for ServiceNow Groups app.
"""

from nautobot.core.settings import *  # noqa: F403

import os
ALLOWED_HOSTS = os.environ.get("NAUTOBOT_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Plugins
PLUGINS = ["service_now_groups"] 