# ORM nin kullanıldığı kısım, burdaki amaç SQL yazmayı engellemek.

from django.contrib.auth.models import \
    AbstractUser  # Django'nun varsayılan kullanıcı (User) modelini genişletmemizi sağlar.
from django.db import \
    models  # Django ORM ile veritabanı tablolarını ve alanlarını (Model, CharField, ForeignKey vb.) tanımlamak için kullanılır.
from django.utils import timezone
from datetime import timedelta
import random
import string


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

    # ✅ DÜZELTİLDİ: username artık zorunlu değil
    username = models.CharField(max_length=150, blank=True, null=True, verbose_name="Kullanıcı Adı")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # ✅ DÜZELTİLDİ: Boş liste, username zorunlu değil

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

    def save(self, *args, **kwargs):
        """
        Kullanıcı kaydedilirken username otomatik oluştur
        """
        if not self.username:
            # Email'den username oluştur: ornek@mail.com → ornek
            self.username = self.email.split('@')[0]

            # Eğer aynı username varsa sonuna random sayı ekle
            counter = 1
            original_username = self.username
            while User.objects.filter(username=self.username).exists():
                self.username = f"{original_username}{counter}"
                counter += 1

        super().save(*args, **kwargs)

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


class EmailVerification(models.Model):
    """Email doğrulama kodları için model"""
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=6, verbose_name="Doğrulama Kodu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    expires_at = models.DateTimeField(verbose_name="Son Kullanma Tarihi")
    is_used = models.BooleanField(default=False, verbose_name="Kullanıldı mı?")

    class Meta:
        db_table = 'email_verifications'
        verbose_name = "Email Doğrulama"
        verbose_name_plural = "Email Doğrulamalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.code}"

    @staticmethod
    def generate_code():
        """6 haneli rastgele kod üret"""
        return ''.join(random.choices(string.digits, k=6))

    def is_expired(self):
        """Kodun süresi doldu mu?"""
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Kod geçerli mi? (kullanılmamış ve süresi dolmamış)"""
        return not self.is_used and not self.is_expired()

    @classmethod
    def create_for_user(cls, user):
        """Kullanıcı için yeni doğrulama kodu oluştur"""
        # Eski kodları pasif yap
        cls.objects.filter(user=user, is_used=False).update(is_used=True)

        # Yeni kod oluştur
        code = cls.generate_code()
        expires_at = timezone.now() + timedelta(minutes=15)  # 15 dakika geçerli

        return cls.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )