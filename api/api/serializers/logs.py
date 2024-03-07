from rest_framework import serializers

from api.api.models import APILog, APILogGenerate


class APILogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APILog
        fields = "__all__"


class APILogGenerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = APILogGenerate
        fields = "__all__"
