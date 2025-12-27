from django.db import models
from django.conf import settings


class StockMovement(models.Model):
    """
    Stok Hareketi modeli - Giriş, çıkış ve düzeltmeler
    """

    MOVEMENT_TYPE_CHOICES = [
        ('in', 'Stok Girişi'),
        ('out', 'Stok Çıkışı'),
        ('adjustment', 'Düzeltme'),
    ]

    # Ürün
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='stock_movements',
        verbose_name="Ürün"
    )

    # Hareket tipi
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES,
        verbose_name="Hareket Tipi"
    )

    # Miktar
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Miktar"
    )

    # Açıklama
    reason = models.TextField(verbose_name="Sebep/Açıklama")

    # İşlemi yapan
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_movements',
        verbose_name="İşlemi Yapan"
    )

    # Tarih
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="İşlem Tarihi")

    class Meta:
        db_table = 'stock_movements'
        verbose_name = "Stok Hareketi"
        verbose_name_plural = "Stok Hareketleri"
        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['movement_type']),
            models.Index(fields=['performed_by']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        # İlk kayıt mı kontrol et
        is_new = self.pk is None

        super().save(*args, **kwargs)

        # Yeni kayıtsa ürün stokunu güncelle
        if is_new:
            product = self.product

            if self.movement_type == 'in':
                # Stok girişi
                product.stock_quantity += self.quantity
            elif self.movement_type == 'out':
                # Stok çıkışı
                product.stock_quantity -= self.quantity
            elif self.movement_type == 'adjustment':
                # Düzeltme - pozitif veya negatif olabilir
                product.stock_quantity += self.quantity

            # Negatif stok olmasın
            if product.stock_quantity < 0:
                product.stock_quantity = 0

            product.save()


class StockAlert(models.Model):
    """
    Stok Uyarısı modeli - Minimum stok seviyesi uyarıları
    """

    # Ürün
    product = models.OneToOneField(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='stock_alert',
        verbose_name="Ürün"
    )

    # Minimum stok seviyesi
    minimum_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Minimum Stok Miktarı"
    )

    # Uyarı aktif mi?
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    # Email gönderildi mi?
    alert_sent = models.BooleanField(default=False, verbose_name="Uyarı Gönderildi mi?")
    alert_sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Uyarı Gönderim Zamanı")

    # Tarih
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'stock_alerts'
        verbose_name = "Stok Uyarısı"
        verbose_name_plural = "Stok Uyarıları"

        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.product.name} - Min: {self.minimum_quantity}"

    @property
    def is_below_minimum(self):
        """Stok minimum seviyenin altında mı?"""
        return self.product.stock_quantity < self.minimum_quantity

    def check_and_send_alert(self):
        """Stok kontrolü yap ve gerekirse uyarı gönder"""
        if not self.is_active:
            return False

        if self.is_below_minimum and not self.alert_sent:
            # TODO: Email gönderme implementasyonu
            # send_stock_alert_email(self.product, self.product.company.owner_user)

            from django.utils import timezone
            self.alert_sent = True
            self.alert_sent_at = timezone.now()
            self.save()

            return True

        # Stok tekrar yükselirse uyarıyı sıfırla
        if not self.is_below_minimum and self.alert_sent:
            self.alert_sent = False
            self.alert_sent_at = None
            self.save()

        return False


class SaleToWebsite(models.Model):
    """
    Stoktan Web Sitesine Satış modeli
    Hangi ürünlerin stoktan web sitesine aktarıldığını takip eder
    """

    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('listed', 'İlanda'),
        ('sold', 'Satıldı'),
        ('removed', 'İlandan Kaldırıldı'),
    ]

    # Ürün
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='sale_listings',
        verbose_name="Ürün"
    )

    # Stok hareketi referansı
    stock_movement = models.ForeignKey(
        StockMovement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sale_listings',
        verbose_name="İlişkili Stok Hareketi"
    )

    # İlan bilgileri
    listed_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="İlan Edilen Miktar"
    )

    listed_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="İlan Fiyatı"
    )

    # Durum
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Durum"
    )

    # Not
    notes = models.TextField(blank=True, verbose_name="Notlar")

    # İşlemi yapan
    listed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='product_listings',
        verbose_name="İlanı Oluşturan"
    )

    # Tarihler
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")
    listed_at = models.DateTimeField(null=True, blank=True, verbose_name="İlan Tarihi")
    sold_at = models.DateTimeField(null=True, blank=True, verbose_name="Satış Tarihi")

    class Meta:
        db_table = 'sale_to_website'
        verbose_name = "Web Sitesi Satış İlanı"
        verbose_name_plural = "Web Sitesi Satış İlanları"
        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['status']),
            models.Index(fields=['listed_by']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_status_display()}"

    def mark_as_listed(self):
        """İlanı aktif yap"""
        from django.utils import timezone

        if self.status == 'pending':
            self.status = 'listed'
            self.listed_at = timezone.now()
            self.product.is_active = True
            self.product.save()
            self.save()

    def mark_as_sold(self):
        """Satıldı olarak işaretle"""
        from django.utils import timezone

        if self.status == 'listed':
            self.status = 'sold'
            self.sold_at = timezone.now()
            self.product.is_sold = True
            self.product.is_active = False
            self.product.save()
            self.save()

    def remove_listing(self):
        """İlandan kaldır"""
        if self.status == 'listed':
            self.status = 'removed'
            self.product.is_active = False
            self.product.save()
            self.save()