from django.db import models
from django.conf import settings
import uuid

class ReturnRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('approved', 'Onaylandi'),
        ('rejected', 'Reddedildi'),
        ('completed', 'Tamamlandi'),
    ]
    REASON_CHOICES = [
        ('defective', 'Urun Kusurlu'),
        ('wrong_item', 'Yanlis Urun'),
        ('changed_mind', 'Fikir Degisikligi'),
        ('other', 'Diger'),
    ]
    return_number = models.CharField(max_length=50, unique=True)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='returns')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='returns')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'return_requests'

    def save(self, *args, **kwargs):
        if not self.return_number:
            self.return_number = f"RET-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class ReturnItem(models.Model):
    return_request = models.ForeignKey(ReturnRequest, on_delete=models.CASCADE, related_name='items')
    order_item = models.ForeignKey('orders.OrderItem', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'return_items'

class Refund(models.Model):
    STATUS_CHOICES = [('pending', 'Beklemede'), ('completed', 'Tamamlandi')]
    return_request = models.OneToOneField(ReturnRequest, on_delete=models.CASCADE, related_name='refund')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'refunds'
