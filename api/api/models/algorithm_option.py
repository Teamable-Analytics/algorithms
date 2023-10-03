from django.db import models
from django.utils.translation import gettext_lazy as _

ALGORITHM_OPTIONS = (
    ("priority", _("priority")),
    ("social", _("social")),
    ("weight", _("weight")),
    ("random", _("random")),
)


class AbstractAlgorithmOption(models.Model):
    algorithm_type = models.TextField(
        blank=False, null=False, choices=ALGORITHM_OPTIONS
    )
    max_project_preferences = models.IntegerField(blank=False, null=False)

    def validate(self):
        raise NotImplementedError("Subclasses should implement this!")

    class Meta:
        abstract = True


class RandomAlgorithmOption(AbstractAlgorithmOption):
    algorithm_type = "social"

    def validate(self):
        raise NotImplementedError("TODO: Implement this!")
    
    def __str__(self):
        return f"""RandomAlgorithmOption {{ max_project_preferences: {self.max_project_preferences} }}"""
