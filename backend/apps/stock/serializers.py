
from rest_framework import serializers
from .models import StockMovement, StockAlert, SaleToWebsite
from apps.products.serializers import ProductSerializer


class StockMovementSerializer(serializers.ModelSerializer):
    """Stok hareketi serializer"""

    product_name = serializers.CharField(source='product.name', read_only=True)
    performed_by_email = serializers.CharField(source='performed_by.email', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'movement_type', 'movement_type_display',
            'quantity', 'reason', 'performed_by', 'performed_by_email', 'created_at'
        ]
        read_only_fields = ['id', 'performed_by', 'created_at']


class StockMovementCreateSerializer(serializers.ModelSerializer):
    """Stok hareketi oluşturma serializer"""

    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'quantity', 'reason']

    def validate_quantity(self, value):
        """Miktar pozitif olmalı"""
        if value <= 0:
            raise serializers.ValidationError("Miktar sıfırdan büyük olmalı")
        return value

    def validate(self, data):
        """Stok çıkışı için yeterli stok var mı kontrol et"""
        if data['movement_type'] == 'out':
            product = data['product']
            if data['quantity'] > product.stock_quantity:
                raise serializers.ValidationError({
                    'quantity': f"Yetersiz stok. Mevcut: {product.stock_quantity}"
                })
        return data

    def create(self, validated_data):
        """Stok hareketi oluştur"""
        # İşlemi yapan kullanıcı context'ten alınır
        user = self.context['request'].user

        # Kullanıcı firma sahibi olmalı
        if not hasattr(user, 'owned_company'):
            raise serializers.ValidationError("Stok işlemi için firma sahibi olmalısınız")

        # Ürün kullanıcının firmasına ait mi kontrol et
        product = validated_data['product']
        if product.company != user.owned_company:
            raise serializers.ValidationError("Bu ürün sizin firmanıza ait değil")

        # Stok hareketi oluştur
        stock_movement = StockMovement.objects.create(
            performed_by=user,
            **validated_data
        )

        return stock_movement


class StockAlertSerializer(serializers.ModelSerializer):
    """Stok uyarısı serializer"""

    product_name = serializers.CharField(source='product.name', read_only=True)
    current_quantity = serializers.DecimalField(
        source='product.stock_quantity',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    is_below_minimum = serializers.ReadOnlyField()

    class Meta:
        model = StockAlert
        fields = [
            'id', 'product', 'product_name', 'minimum_quantity',
            'current_quantity', 'is_below_minimum', 'is_active',
            'alert_sent', 'alert_sent_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'alert_sent', 'alert_sent_at', 'created_at', 'updated_at']


class StockAlertCreateSerializer(serializers.ModelSerializer):
    """Stok uyarısı oluşturma serializer"""

    class Meta:
        model = StockAlert
        fields = ['product', 'minimum_quantity', 'is_active']

    def validate_minimum_quantity(self, value):
        """Minimum miktar pozitif olmalı"""
        if value <= 0:
            raise serializers.ValidationError("Minimum miktar sıfırdan büyük olmalı")
        return value

    def validate_product(self, value):
        """Ürün için zaten uyarı var mı kontrol et"""
        if StockAlert.objects.filter(product=value).exists():
            raise serializers.ValidationError("Bu ürün için zaten stok uyarısı mevcut")
        return value


class SaleToWebsiteSerializer(serializers.ModelSerializer):
    """Web sitesi satış ilanı serializer"""

    product_details = ProductSerializer(source='product', read_only=True)
    listed_by_email = serializers.CharField(source='listed_by.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SaleToWebsite
        fields = [
            'id', 'product', 'product_details', 'stock_movement',
            'listed_quantity', 'listed_price', 'status', 'status_display',
            'notes', 'listed_by', 'listed_by_email',
            'created_at', 'listed_at', 'sold_at'
        ]
        read_only_fields = [
            'id', 'listed_by', 'created_at', 'listed_at', 'sold_at'
        ]


class SaleToWebsiteCreateSerializer(serializers.Serializer):
    """Ürünü web sitesine satışa çıkar"""

    product_id = serializers.IntegerField()
    listed_quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    listed_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_listed_quantity(self, value):
        """Miktar pozitif olmalı"""
        if value <= 0:
            raise serializers.ValidationError("Miktar sıfırdan büyük olmalı")
        return value

    def validate_listed_price(self, value):
        """Fiyat pozitif olmalı"""
        if value <= 0:
            raise serializers.ValidationError("Fiyat sıfırdan büyük olmalı")
        return value

    def validate(self, data):
        """Ürün ve stok kontrolü"""
        from apps.products.models import Product

        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product_id': "Ürün bulunamadı"})

        # Yeterli stok var mı?
        if data['listed_quantity'] > product.stock_quantity:
            raise serializers.ValidationError({
                'listed_quantity': f"Yetersiz stok. Mevcut: {product.stock_quantity}"
            })

        data['product'] = product
        return data

    def create(self, validated_data):
        """Web sitesine satışa çıkar"""
        from apps.products.models import Product

        product_id = validated_data['product_id']
        listed_quantity = validated_data['listed_quantity']
        listed_price = validated_data['listed_price']
        notes = validated_data.get('notes', '')

        # Kullanıcı context'ten alınır
        user = self.context['request'].user

        # Ürünü al
        product = Product.objects.get(id=product_id)

        # Kullanıcı firma sahibi olmalı ve ürün ona ait olmalı
        if not hasattr(user, 'owned_company') or product.company != user.owned_company:
            raise serializers.ValidationError("Bu ürün sizin firmanıza ait değil")

        # Stok hareketi oluştur (çıkış)
        stock_movement = StockMovement.objects.create(
            product=product,
            movement_type='out',
            quantity=listed_quantity,
            reason=f"Web sitesine satışa çıkarıldı - {notes}",
            performed_by=user
        )

        # Satış ilanı oluştur
        sale_listing = SaleToWebsite.objects.create(
            product=product,
            stock_movement=stock_movement,
            listed_quantity=listed_quantity,
            listed_price=listed_price,
            notes=notes,
            listed_by=user,
            status='pending'
        )

        # Ürün bilgilerini güncelle
        product.sale_price = listed_price
        product.save()

        # İlanı aktif yap
        sale_listing.mark_as_listed()

        return sale_listing


class StockSummarySerializer(serializers.Serializer):
    """Stok özeti serializer"""

    total_products = serializers.IntegerField()
    total_stock_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    low_stock_count = serializers.IntegerField()
    out_of_stock_count = serializers.IntegerField()
    active_listings = serializers.IntegerField()