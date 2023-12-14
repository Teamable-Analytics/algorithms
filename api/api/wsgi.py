"""
WSGI config for api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.environ.get("APP_ENV", "dev")

if APP_ENV == "prod":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.api.settings.prod")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.api.settings")

application = get_wsgi_application()
