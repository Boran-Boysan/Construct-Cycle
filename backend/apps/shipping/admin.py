from django.contrib import admin
from .models import ShippingCompany, Shipment, ShipmentHistory

@admin.register(ShippingCompany)
class ShippingCompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'status', 'tracking_number']
