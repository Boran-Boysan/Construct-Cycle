from rest_framework import serializers
from .models import ReturnRequest, ReturnItem, Refund

class ReturnItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnItem
        fields = ['id', 'order_item', 'quantity']

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['id', 'amount', 'status', 'completed_at']

class ReturnRequestSerializer(serializers.ModelSerializer):
    items = ReturnItemSerializer(many=True, read_only=True)
    refund = RefundSerializer(read_only=True)

    class Meta:
        model = ReturnRequest
        fields = ['id', 'return_number', 'order', 'status', 'reason', 'description', 'items', 'refund', 'created_at']

class ReturnRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnRequest
        fields = ['order', 'reason', 'description']
