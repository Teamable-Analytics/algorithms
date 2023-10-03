from django.db import models


class Student(models.Model):
    id = models.CharField(unique=True, max_length=10, primary_key=True)
    attributes = models.JSONField(
        default=dict, blank=True, null=False
    )  # TODO: Need validation
    relationships = models.JSONField(
        default=dict, blank=True, null=False
    )  # TODO: Need validation
    project_preferences = models.JSONField(
        default=list, blank=True, null=False
    )  # TODO: Need validation

    def validate(self):
        raise NotImplementedError("TODO: Implement this!")

    def __str__(self):
        return f"Student {self.id}"
