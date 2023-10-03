from django.db import models
from django.utils.translation import gettext_lazy as _

REQUIREMENT_OPERATORS = (
    ("more than", _("more than")),
    ("less than", _("less than")),
    ("exactly", _("exactly"))
)

class Requirement(models.Model):
    attribute_id = models.CharField(unique=True, max_length=10, primary_key=True)
    operator = models.CharField(max_length=9, blank=False, null=False, choices=REQUIREMENT_OPERATORS)
    value = models.IntegerField(blank=False, null=False)

    def validate(self):
        raise NotImplementedError("TODO: Implement this!")
    
    def __str__(self):
        return f"Attribute {self.attribute_id} must be {self.operator} {self.value}"
