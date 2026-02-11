from rest_framework import serializers
from .models import ShippingCompany, Shipment

class ShippingCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCompany
        fields = ['id', 'name', 'code', 'is_active']

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['id', 'order', 'shipping_company', 'tracking_number', 'status', 'created_at']
