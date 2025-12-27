
from django.db import models
from django.conf import settings


class Order(models.Model):
    """
    Sipariş modeli - Alıcı ve satıcı arasındaki işlemler
    """

    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('confirmed', 'Onaylandı'),
        ('shipped', 'Kargoya Verildi'),
        ('delivered', 'Teslim Edildi'),
        ('cancelled', 'İptal Edildi'),
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Nakit'),
        ('transfer', 'Havale/EFT'),
        ('credit_card', 'Kredi Kartı'),
    ]

    # Sipariş numarası (otomatik oluşturulacak)
    order_number = models.CharField(max_length=50, unique=True, verbose_name="Sipariş No")

    # İlişkiler
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name="Alıcı"
    )

    seller_company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='sales',
        verbose_name="Satıcı Firma"
    )

    # Durum
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Durum"
    )

    # Ödeme
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='cash',
        verbose_name="Ödeme Yöntemi"
    )

    # Fiyat bilgileri (kuruş cinsinden - cents)
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Toplam Tutar"
    )

    # Notlar
    buyer_note = models.TextField(blank=True, verbose_name="Alıcı Notu")
    seller_note = models.TextField(blank=True, verbose_name="Satıcı Notu")

    # Tarihler
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sipariş Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'orders'
        verbose_name = "Sipariş"
        verbose_name_plural = "Siparişler"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer']),
            models.Index(fields=['seller_company']),
            models.Index(fields=['status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Sipariş #{self.order_number}"

    def save(self, *args, **kwargs):
        # Sipariş numarası otomatik oluştur
        if not self.order_number:
            import uuid
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_id = str(uuid.uuid4())[:8].upper()
            self.order_number = f"CC-{timestamp}-{unique_id}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Sipariş kalemleri - Siparişteki her ürün
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Sipariş"
    )

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name="Ürün"
    )

    # Snapshot - Sipariş anındaki bilgiler (ürün silinse bile kalır)
    product_name = models.CharField(max_length=255, verbose_name="Ürün Adı")
    product_condition = models.IntegerField(verbose_name="Ürün Durumu")

    # Miktar ve fiyat
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Miktar"
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Birim Fiyat"
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Toplam Fiyat"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Eklenme Tarihi")

    class Meta:
        db_table = 'order_items'
        verbose_name = "Sipariş Kalemi"
        verbose_name_plural = "Sipariş Kalemleri"
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        # Toplam fiyatı hesapla
        self.total_price = self.unit_price * self.quantity

        # Snapshot bilgilerini al
        if not self.product_name:
            self.product_name = self.product.name
            self.product_condition = self.product.condition

        super().save(*args, **kwargs)