from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex, BTreeIndex
from decimal import Decimal


class Category(models.Model):
    """
    Ürün kategorileri - Hiyerarşik yapı
    """

    name = models.CharField(max_length=255, verbose_name="Kategori Adı")
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name="Üst Kategori"
    )
    slug = models.SlugField(unique=True, max_length=255, verbose_name="URL")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Sıralama", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma Tarihi")

    class Meta:
        db_table = 'categories'
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ['display_order', 'name']

        # PostgreSQL'e özel index'ler
        indexes = [
            models.Index(fields=['parent']),
            models.Index(fields=['slug']),
            BTreeIndex(fields=['display_order', 'name']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Product(models.Model):
    """
    Ürün modeli - PostgreSQL optimizasyonlu
    """

    CONDITION_CHOICES = [
        (0, 'Sıfır / Hiç Kullanılmamış'),
        (1, 'Az Kullanılmış / İyi Durumda'),
        (2, 'Kullanılmış / Orta Durumda'),
    ]

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Satıcı Firma",
        db_index=True
    )

    name = models.CharField(max_length=255, verbose_name="Ürün Adı", db_index=True)
    description = models.TextField(verbose_name="Açıklama")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
        verbose_name="Kategori",
        db_index=True
    )

    condition = models.IntegerField(
        choices=CONDITION_CHOICES,
        default=0,
        verbose_name="Kullanım Durumu",
        db_index=True
    )

    stock_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Stok Miktarı"
    )

    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Satış Fiyatı",
        db_index=True
    )

    ai_suggested_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="AI Önerilen Fiyat"
    )

    city = models.CharField(max_length=100, verbose_name="Şehir", db_index=True)
    district = models.CharField(max_length=100, blank=True, verbose_name="İlçe")

    # PostgreSQL ArrayField - Etiketler için
    tags = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        null=True,
        verbose_name="Etiketler",
        help_text="Ör: ['demir', 'profil', '80x80']"
    )

    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?", db_index=True)
    is_sold = models.BooleanField(default=False, verbose_name="Satıldı mı?", db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="İlan Tarihi", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        db_table = 'products'
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        ordering = ['-created_at']

        # PostgreSQL'e özel index'ler
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['category']),
            models.Index(fields=['city']),
            models.Index(fields=['is_active', 'is_sold']),
            models.Index(fields=['-created_at']),

            # Composite indexes
            BTreeIndex(fields=['city', 'category', '-created_at']),
            BTreeIndex(fields=['is_active', 'is_sold', '-created_at']),
            BTreeIndex(fields=['sale_price', '-created_at']),

            # GIN Index - Array field için
            GinIndex(fields=['tags']),
        ]

        # Constraint'ler
        constraints = [
            models.CheckConstraint(
                condition=models.Q(stock_quantity__gte=0),
                name='stock_quantity_positive'
            ),
            models.CheckConstraint(
                condition=models.Q(sale_price__gt=0),
                name='sale_price_positive'
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.company.company_name}"

    @property
    def condition_display(self):
        return dict(self.CONDITION_CHOICES)[self.condition]

    @property
    def savings(self):
        if self.ai_suggested_price and self.ai_suggested_price > self.sale_price:
            return self.ai_suggested_price - self.sale_price
        return Decimal('0.00')

    @property
    def days_listed(self):
        from django.utils import timezone
        delta = timezone.now() - self.created_at
        return delta.days


class ProductImage(models.Model):
    """
    Ürün fotoğrafları - Çoklu fotoğraf desteği
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Ürün",
        db_index=True
    )

    image_url = models.ImageField(
        upload_to='products/%Y/%m/',
        verbose_name="Fotoğraf"
    )

    is_primary = models.BooleanField(default=False, verbose_name="Ana Fotoğraf", db_index=True)
    display_order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yüklenme Tarihi")

    class Meta:
        db_table = 'product_images'
        verbose_name = "Ürün Fotoğrafı"
        verbose_name_plural = "Ürün Fotoğrafları"
        ordering = ['display_order', '-is_primary']

        # PostgreSQL index
        indexes = [
            models.Index(fields=['product', 'is_primary']),
            BTreeIndex(fields=['product', 'display_order']),
        ]

        # Unique constraint - Her üründe sadece 1 ana fotoğraf
        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                condition=models.Q(is_primary=True),
                name='one_primary_image_per_product'
            ),
        ]

    def __str__(self):
        return f"{self.product.name} - Fotoğraf {self.display_order}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)