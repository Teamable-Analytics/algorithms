from rest_framework import serializers

from api.api.models import APILog


class APILogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APILog
        fields = "__all__"
