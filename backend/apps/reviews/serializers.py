from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user_name', 'product', 'rating', 'title', 'comment', 'is_verified_purchase', 'helpful_count', 'created_at']

    def get_user_name(self, obj):
        name = obj.user.email.split('@')[0]
        return name[0] + '***'

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['product', 'rating', 'title', 'comment']
