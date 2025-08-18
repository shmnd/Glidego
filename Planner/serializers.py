from rest_framework import serializers

class SuggestedPlanRequestSerializer(serializers.Serializer):
    start = serializers.CharField()
    end = serializers.CharField()
    dates = serializers.ListField(child=serializers.DateField())
    budget = serializers.CharField()
    people = serializers.DictField()
