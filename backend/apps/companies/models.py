
from django.db import models
from django.conf import settings


class Company(models.Model):
    """
    Firma modeli - Müteahhit/Üretici firmaları
    """

    owner_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_company',
        verbose_name="Firma Sahibi"
    )

    company_name = models.CharField(max_length=255, verbose_name="Firma Adı")
    tax_number = models.CharField(max_length=50, unique=True, verbose_name="Vergi Numarası")

    # İletişim bilgileri
    city = models.CharField(max_length=100, verbose_name="Şehir")
    district = models.CharField(max_length=100, blank=True, verbose_name="İlçe")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    email = models.EmailField(verbose_name="E-posta")

    # Doğrulama
    is_verified = models.BooleanField(default=False, verbose_name="Doğrulanmış mı?")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")

    class Meta:
        db_table = 'companies'
        verbose_name = "Firma"
        verbose_name_plural = "Firmalar"
        indexes = [
            models.Index(fields=['owner_user']),
            models.Index(fields=['city']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['tax_number']),
        ]

    def __str__(self):
        return self.company_name


class CompanyUser(models.Model):
    """
    Firma çalışanları - Bir firmada birden fazla kullanıcı olabilir
    """

    ROLE_CHOICES = [
        ('admin', 'Yönetici'),
        ('warehouse_manager', 'Depo Sorumlusu'),
        ('sales_staff', 'Satış Yetkilisi'),
        ('viewer', 'Görüntüleyici'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='company_users',
        verbose_name="Firma"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_memberships',
        verbose_name="Kullanıcı"
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default='viewer',
        verbose_name="Rol"
    )

    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Katılma Tarihi")

    class Meta:
        db_table = 'company_users'
        verbose_name = "Firma Çalışanı"
        verbose_name_plural = "Firma Çalışanları"
        unique_together = [['company', 'user']]
        indexes = [
            models.Index(fields=['company', 'user']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.company.company_name} ({self.get_role_display()})"

    def can_manage_stock(self):
        """Stok yönetimi yetkisi"""
        return self.role in ['admin', 'warehouse_manager']

    def can_sell(self):
        """Satış yetkisi"""
        return self.role in ['admin', 'sales_staff']