from django.db import models
from django.conf import settings

class ShippingCompany(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    logo = models.ImageField(upload_to='shipping/logos/', blank=True, null=True)
    tracking_url_template = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shipping_companies'

    def __str__(self):
        return self.name

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('shipped', 'Kargoya Verildi'),
        ('delivered', 'Teslim Edildi'),
    ]
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='shipment')
    shipping_company = models.ForeignKey(ShippingCompany, on_delete=models.PROTECT, null=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shipments'

class ShipmentHistory(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shipment_history'
        ordering = ['-created_at']
