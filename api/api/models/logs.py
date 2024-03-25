from django.db import models

from api.api.models.base_models import BaseModel


class APISource(models.TextChoices):
    """
    Choices for the source field in the APILog model
    """

    NORMAL = "Normal", "Normal"
    INTERNAL_DEMO = "Internal Demo", "Internal Demo"


class APILog(BaseModel):
    endpoint = models.CharField(max_length=100)
    source = models.CharField(max_length=50, choices=APISource.choices)
    api_version = models.CharField(max_length=50)
    data = models.JSONField()
