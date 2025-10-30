from rest_framework import serializers

class BasicReportSerializer(serializers.Serializer):
    report_name = serializers.CharField(max_length=100)
    generated_at = serializers.DateTimeField()
    data = serializers.ListField()