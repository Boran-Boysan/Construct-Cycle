
from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Sipariş kalemi serializer"""

    product_details = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_details', 'product_name',
            'product_condition', 'quantity', 'unit_price', 'total_price',
            'created_at'
        ]
        read_only_fields = ['id', 'product_name', 'product_condition', 'total_price', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    """Sipariş serializer - Liste ve detay için"""

    items = OrderItemSerializer(many=True, read_only=True)
    buyer_email = serializers.CharField(source='buyer.email', read_only=True)
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)
    seller_company_name = serializers.CharField(source='seller_company.company_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'buyer', 'buyer_email', 'buyer_name',
            'seller_company', 'seller_company_name', 'status', 'status_display',
            'payment_method', 'payment_method_display', 'total_amount',
            'buyer_note', 'seller_note', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    """Sipariş oluşturma serializer"""

    product_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES, default='cash')
    buyer_note = serializers.CharField(required=False, allow_blank=True)

    def validate_quantity(self, value):
        """Miktar pozitif olmalı"""
        if value <= 0:
            raise serializers.ValidationError("Miktar sıfırdan büyük olmalı")
        return value

    def validate_product_id(self, value):
        """Ürün var mı ve satışta mı kontrol et"""
        from apps.products.models import Product

        try:
            product = Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Ürün bulunamadı")

        if not product.is_active or product.is_sold:
            raise serializers.ValidationError("Bu ürün satışta değil")

        return value

    def create(self, validated_data):
        """Sipariş oluştur"""
        from apps.products.models import Product

        product_id = validated_data['product_id']
        quantity = validated_data['quantity']
        payment_method = validated_data.get('payment_method', 'cash')
        buyer_note = validated_data.get('buyer_note', '')

        # Kullanıcı context'ten alınır
        buyer = self.context['request'].user

        # Ürünü al
        product = Product.objects.get(id=product_id)

        # Stok kontrolü
        if quantity > product.stock_quantity:
            raise serializers.ValidationError({
                'quantity': f'Stokta sadece {product.stock_quantity} adet var'
            })

        # Toplam tutarı hesapla
        unit_price = product.sale_price
        total_amount = unit_price * quantity

        # Sipariş oluştur
        order = Order.objects.create(
            buyer=buyer,
            seller_company=product.company,
            payment_method=payment_method,
            total_amount=total_amount,
            buyer_note=buyer_note
        )

        # Sipariş kalemi oluştur
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=unit_price
        )

        # Stok düş
        product.stock_quantity -= quantity
        if product.stock_quantity == 0:
            product.is_sold = True
        product.save()

        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Sipariş durumu güncelleme serializer"""

    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    seller_note = serializers.CharField(required=False, allow_blank=True)


class OrderListSerializer(serializers.ModelSerializer):
    """Sipariş liste serializer - Hafif version"""

    buyer_email = serializers.CharField(source='buyer.email', read_only=True)
    seller_company_name = serializers.CharField(source='seller_company.company_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'buyer_email', 'seller_company_name',
            'status', 'status_display', 'total_amount', 'item_count',
            'created_at'
        ]

    def get_item_count(self, obj):
        """Siparişteki ürün sayısı"""
        return obj.items.count()