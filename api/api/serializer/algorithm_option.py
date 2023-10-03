from rest_framework import serializers

from api.models import RandomAlgorithmOption


class RandomAlgorithmOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RandomAlgorithmOption
        fields = ["algorithm_type", "max_project_preferences"]
