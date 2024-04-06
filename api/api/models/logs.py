from typing import Union, Dict, List

from django.db import models

from api import api
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

    @staticmethod
    def log(
        endpoint: str, data: Union[Dict, List], source: APISource = APISource.NORMAL
    ):
        APILog.objects.create(
            endpoint=endpoint,
            source=source,
            api_version=api.VERSION,
            data=data,
        )
