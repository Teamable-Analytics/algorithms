from rest_framework import serializers
from api.models import Requirement


class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = ["attribute_id", "operator", "value"]
