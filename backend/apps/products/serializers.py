from rest_framework import serializers
from .models import Product, Category, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    """Kategori serializer"""

    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'parent_name', 'display_order', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class ProductImageSerializer(serializers.ModelSerializer):
    """Ürün fotoğrafı serializer"""

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_primary', 'display_order', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    """Ürün serializer - Liste ve detay için"""

    # İlişkili veriler
    images = ProductImageSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    # Hesaplanan alanlar
    condition_display = serializers.CharField(read_only=True)
    savings = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    days_listed = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'company', 'company_name', 'name', 'description',
            'category', 'category_name', 'condition', 'condition_display',
            'stock_quantity', 'sale_price', 'ai_suggested_price', 'savings',
            'city', 'district', 'tags', 'is_active', 'is_sold',
            'images', 'days_listed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'company']


class ProductCreateSerializer(serializers.ModelSerializer):
    """Ürün oluşturma serializer"""

    # Fotoğraf upload için
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="Birden fazla fotoğraf yükleyebilirsiniz"
    )

    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'condition',
            'stock_quantity', 'sale_price', 'ai_suggested_price',
            'city', 'district', 'tags', 'uploaded_images'
        ]

    def validate_tags(self, value):
        """Etiket validasyonu"""
        if value and len(value) > 10:
            raise serializers.ValidationError("En fazla 10 etiket ekleyebilirsiniz")
        return value

    def create(self, validated_data):
        """Ürün oluştur ve fotoğrafları ekle"""
        uploaded_images = validated_data.pop('uploaded_images', [])

        # Firma context'ten alınır
        company = self.context.get('company')
        if not company:
            raise serializers.ValidationError("Firma bilgisi bulunamadı")

        # Ürün oluştur
        product = Product.objects.create(company=company, **validated_data)

        # Fotoğrafları ekle
        for index, image in enumerate(uploaded_images):
            ProductImage.objects.create(
                product=product,
                image_url=image,
                is_primary=(index == 0),  # İlk fotoğraf ana fotoğraf
                display_order=index
            )

        return product


class ProductUpdateSerializer(serializers.ModelSerializer):
    """Ürün güncelleme serializer"""

    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'condition',
            'stock_quantity', 'sale_price', 'ai_suggested_price',
            'city', 'district', 'tags', 'is_active'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Ürün liste serializer - Hafif version"""

    company_name = serializers.CharField(source='company.company_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    condition_display = serializers.CharField(read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'company_name', 'category_name',
            'condition', 'condition_display', 'sale_price',
            'city', 'district', 'primary_image', 'is_sold', 'created_at'
        ]

    def get_primary_image(self, obj):
        """Ana fotoğrafı getir"""
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary.image_url.url)
        return None