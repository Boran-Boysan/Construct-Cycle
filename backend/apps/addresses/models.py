from django.db import models
from django.conf import settings


class City(models.Model):
    """İl"""
    name = models.CharField(max_length=100, verbose_name="İl Adı")
    plate_code = models.CharField(max_length=2, unique=True, verbose_name="Plaka Kodu")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        db_table = 'cities'
        verbose_name = "İl"
        verbose_name_plural = "İller"
        ordering = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    """İlçe"""
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='districts', verbose_name="İl")
    name = models.CharField(max_length=100, verbose_name="İlçe Adı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        db_table = 'districts'
        verbose_name = "İlçe"
        verbose_name_plural = "İlçeler"
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.city.name}"


class Address(models.Model):
    """Kullanıcı Adresi"""
    ADDRESS_TYPE_CHOICES = [
        ('shipping', 'Teslimat Adresi'),
        ('billing', 'Fatura Adresi'),
        ('both', 'Her İkisi'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name="Kullanıcı"
    )
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='both', verbose_name="Adres Tipi")
    title = models.CharField(max_length=100, verbose_name="Adres Başlığı")
    full_name = models.CharField(max_length=200, verbose_name="Ad Soyad")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name="İl")
    district = models.ForeignKey(District, on_delete=models.PROTECT, verbose_name="İlçe")
    neighborhood = models.CharField(max_length=100, blank=True, verbose_name="Mahalle")
    address_line = models.TextField(verbose_name="Adres")
    postal_code = models.CharField(max_length=10, blank=True, verbose_name="Posta Kodu")
    is_default = models.BooleanField(default=False, verbose_name="Varsayılan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'addresses'
        verbose_name = "Adres"
        verbose_name_plural = "Adresler"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.full_name}"

    @property
    def full_address(self):
        parts = [self.address_line]
        if self.neighborhood:
            parts.append(self.neighborhood)
        parts.append(f"{self.district.name}/{self.city.name}")
        if self.postal_code:
            parts.append(self.postal_code)
        return ", ".join(parts)

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
