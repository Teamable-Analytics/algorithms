"""
ASGI config for api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from dotenv import load_dotenv
load_dotenv()

APP_ENV = os.environ.get("APP_ENV", "dev")

if APP_ENV == "prod":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.api.settings.prod")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.api.settings")

application = get_asgi_application()
