from rest_framework import serializers
from .models import Report, UserWarning, UserBan

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'report_number', 'target_type', 'target_id', 'reason', 'description', 'status', 'created_at']

class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['target_type', 'target_id', 'reason', 'description']

class UserWarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWarning
        fields = ['id', 'reason', 'is_active', 'created_at']

class UserBanSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBan
        fields = ['id', 'reason', 'expires_at', 'is_active', 'created_at']
