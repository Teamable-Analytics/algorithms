from django.db import models

from app.models.base_models import BaseModel


class APIUseCase(models.TextChoices):
    """
    Choices for the usecase field in the APILog model
    """

    NORMAL = "Normal", "Normal"
    INTERNAL_DEMO = "Internal Demo", "Internal Demo"


class APILog(BaseModel):
    endpoint = models.TextField()
    http_method = models.CharField(max_length=50)
    use_case = models.CharField(max_length=50, choices=APIUseCase.choices)
    api_version = models.CharField(max_length=50)


class APILogGenerate(APILog):
    generation_configuration = models.JSONField()
