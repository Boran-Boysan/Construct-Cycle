
#ORM nin kullanıldığı kısım, burdaki amaç SQL yazmayı engellemek.

from django.contrib.auth.models import AbstractUser # Django’nun varsayılan kullanıcı (User) modelini genişletmemizi sağlar.
from django.db import models  # Django ORM ile veritabanı tablolarını ve alanlarını (Model, CharField, ForeignKey vb.) tanımlamak için kullanılır.


class User(AbstractUser):
    """
    Kullanıcı modeli - Rol tabanlı yetkilendirme
    Roller: admin, seller (satıcı/müteahhit), buyer (alıcı)
    """

    USER_TYPE_CHOICES = [
        ('admin', 'Yönetici'),
        ('seller', 'Satıcı/Müteahhit'),
        ('buyer', 'Alıcı'),
    ]

    email = models.EmailField(unique=True, verbose_name="E-posta")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='buyer',
        verbose_name="Kullanıcı Tipi"
    )

    is_email_verified = models.BooleanField(default=False, verbose_name="E-posta Doğrulandı mı?")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")

    first_name = models.CharField(max_length=150, blank=True, verbose_name="Ad")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Soyad")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Tam ad"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def is_seller(self):
        """Satıcı mı?"""
        return self.user_type == 'seller'

    @property
    def is_buyer(self):
        """Alıcı mı?"""
        return self.user_type == 'buyer'

    def can_sell_products(self):
        """Ürün satış yetkisi var mı?"""
        return self.user_type == 'seller' and hasattr(self, 'owned_company')