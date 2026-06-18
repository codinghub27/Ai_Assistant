from rest_framework import serializers

class ResearchSerializer(serializers.Serializer):
    question=serializers.CharField()