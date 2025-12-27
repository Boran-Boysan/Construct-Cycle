
from rest_framework import serializers
from .models import Conversation, Message
from apps.products.serializers import ProductSerializer
from apps.accounts.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    """Mesaj serializer"""

    sender_email = serializers.CharField(source='sender.email', read_only=True)
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_email', 'sender_name',
            'message_text', 'is_read', 'read_at', 'is_mine', 'created_at'
        ]
        read_only_fields = ['id', 'sender', 'is_read', 'read_at', 'created_at']

    def get_is_mine(self, obj):
        """Mesaj bana ait mi?"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender == request.user
        return False


class MessageCreateSerializer(serializers.ModelSerializer):
    """Mesaj gönderme serializer"""

    class Meta:
        model = Message
        fields = ['conversation', 'message_text']

    def validate_message_text(self, value):
        """Mesaj boş olamaz"""
        if not value.strip():
            raise serializers.ValidationError("Mesaj boş olamaz")
        return value.strip()

    def create(self, validated_data):
        """Mesaj oluştur"""
        # Gönderen context'ten alınır
        sender = self.context['request'].user

        # Konuşma kontrolü
        conversation = validated_data['conversation']

        # Kullanıcı bu konuşmada var mı?
        if sender != conversation.buyer and sender != conversation.seller:
            raise serializers.ValidationError("Bu konuşmaya katılım yetkiniz yok")

        # Mesaj oluştur
        message = Message.objects.create(
            sender=sender,
            **validated_data
        )

        return message


class ConversationSerializer(serializers.ModelSerializer):
    """Konuşma serializer - Detay"""

    product_details = ProductSerializer(source='product', read_only=True)
    buyer_details = UserSerializer(source='buyer', read_only=True)
    seller_details = UserSerializer(source='seller', read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    last_message_text = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'product', 'product_details', 'buyer', 'buyer_details',
            'seller', 'seller_details', 'is_active', 'messages',
            'last_message_text', 'last_message_time', 'unread_count',
            'other_user', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_last_message_text(self, obj):
        """Son mesaj metni"""
        last = obj.last_message
        return last.message_text if last else None

    def get_last_message_time(self, obj):
        """Son mesaj zamanı"""
        last = obj.last_message
        return last.created_at if last else obj.updated_at

    def get_unread_count(self, obj):
        """Okunmamış mesaj sayısı"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.get_unread_count(request.user)
        return 0

    def get_other_user(self, obj):
        """Karşı tarafın bilgileri"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user == obj.buyer:
                other = obj.seller
            else:
                other = obj.buyer

            return {
                'id': other.id,
                'email': other.email,
                'name': other.full_name,
                'user_type': other.user_type
            }
        return None


class ConversationListSerializer(serializers.ModelSerializer):
    """Konuşma liste serializer - Hafif version"""

    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()
    last_message_text = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'product_name', 'product_image', 'other_user',
            'last_message_text', 'last_message_time', 'unread_count',
            'is_active', 'updated_at'
        ]

    def get_product_image(self, obj):
        """Ürün resmi"""
        primary_image = obj.product.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image_url.url)
        return None

    def get_other_user(self, obj):
        """Karşı tarafın bilgileri"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user == obj.buyer:
                other = obj.seller
            else:
                other = obj.buyer

            return {
                'id': other.id,
                'email': other.email,
                'name': other.full_name
            }
        return None

    def get_last_message_text(self, obj):
        """Son mesaj"""
        last = obj.last_message
        if last:
            # Uzunsa kısalt
            text = last.message_text
            return text[:50] + '...' if len(text) > 50 else text
        return "Henüz mesaj yok"

    def get_last_message_time(self, obj):
        """Son mesaj zamanı"""
        last = obj.last_message
        return last.created_at if last else obj.updated_at

    def get_unread_count(self, obj):
        """Okunmamış mesaj sayısı"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.get_unread_count(request.user)
        return 0


class ConversationStartSerializer(serializers.Serializer):
    """Konuşma başlatma serializer"""

    product_id = serializers.IntegerField()
    message_text = serializers.CharField()

    def validate_product_id(self, value):
        """Ürün var mı kontrol et"""
        from apps.products.models import Product

        try:
            product = Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Ürün bulunamadı veya aktif değil")

        return value

    def validate_message_text(self, value):
        """Mesaj boş olamaz"""
        if not value.strip():
            raise serializers.ValidationError("Mesaj boş olamaz")
        return value.strip()

    def create(self, validated_data):
        """Konuşma başlat ve ilk mesajı gönder"""
        from apps.products.models import Product

        product_id = validated_data['product_id']
        message_text = validated_data['message_text']

        # Kullanıcı context'ten alınır
        buyer = self.context['request'].user

        # Ürünü al
        product = Product.objects.get(id=product_id)
        seller = product.company.owner_user

        # Kendi ürününe mesaj atamaz
        if buyer == seller:
            raise serializers.ValidationError("Kendi ürününüze mesaj gönderemezsiniz")

        # Konuşma var mı kontrol et
        conversation, created = Conversation.objects.get_or_create(
            product=product,
            buyer=buyer,
            seller=seller
        )

        # İlk mesajı gönder
        message = Message.objects.create(
            conversation=conversation,
            sender=buyer,
            message_text=message_text
        )

        return conversation