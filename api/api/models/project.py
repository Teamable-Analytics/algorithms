from django.db import models

from .requirement import Requirement


class Project(models.Model):
    id: models.CharField(unique=True, max_length=10, primary_key=True)
    number_of_teams = models.IntegerField(default=1, blank=True, null=False)
    requirements = models.ManyToManyField(Requirement, blank=True)

    def validate(self):
        raise NotImplementedError("TODO: Implement this!")

    def __str__(self):
        return f"Project {self.id}"
