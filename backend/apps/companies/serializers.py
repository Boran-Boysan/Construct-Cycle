
from rest_framework import serializers
from .models import Company, CompanyUser
from apps.accounts.serializers import UserSerializer


class CompanySerializer(serializers.ModelSerializer):
    """Firma serializer"""

    owner_email = serializers.CharField(source='owner_user.email', read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'company_name', 'tax_number', 'city', 'district',
            'phone', 'email', 'is_verified', 'owner_email', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_verified']


class CompanyCreateSerializer(serializers.ModelSerializer):
    """Firma oluşturma serializer"""

    class Meta:
        model = Company
        fields = [
            'company_name', 'tax_number', 'city', 'district',
            'phone', 'email'
        ]

    def validate_tax_number(self, value):
        """Vergi numarası kontrolü"""
        if Company.objects.filter(tax_number=value).exists():
            raise serializers.ValidationError("Bu vergi numarası zaten kayıtlı")
        return value

    def create(self, validated_data):
        """Firma oluştur - owner_user otomatik atanır"""
        user = self.context['request'].user

        # Kullanıcı zaten firma sahibi mi kontrol et
        if hasattr(user, 'owned_company'):
            raise serializers.ValidationError("Zaten bir firmanız var")

        # Kullanıcı seller olmalı
        if user.user_type != 'seller':
            raise serializers.ValidationError("Sadece satıcı hesapları firma oluşturabilir")

        company = Company.objects.create(owner_user=user, **validated_data)
        return company


class CompanyUserSerializer(serializers.ModelSerializer):
    """Firma çalışanı serializer"""

    user_details = UserSerializer(source='user', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CompanyUser
        fields = [
            'id', 'company', 'company_name', 'user', 'user_details',
            'role', 'role_display', 'joined_at'
        ]
        read_only_fields = ['id', 'joined_at']


class CompanyUserCreateSerializer(serializers.ModelSerializer):
    """Firma çalışanı ekleme serializer"""

    user_email = serializers.EmailField(write_only=True)

    class Meta:
        model = CompanyUser
        fields = ['user_email', 'role']

    def validate(self, data):
        """Validasyon"""
        from apps.accounts.models import User

        # Email'e göre kullanıcıyı bul
        try:
            user = User.objects.get(email=data['user_email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Bu email ile kayıtlı kullanıcı bulunamadı")

        data['user'] = user

        # Firma context'ten alınır
        company = self.context.get('company')
        if not company:
            raise serializers.ValidationError("Firma bilgisi bulunamadı")

        # Kullanıcı zaten bu firmada mı?
        if CompanyUser.objects.filter(company=company, user=user).exists():
            raise serializers.ValidationError("Bu kullanıcı zaten firmada kayıtlı")

        data['company'] = company

        return data

    def create(self, validated_data):
        """Firma çalışanı ekle"""
        validated_data.pop('user_email', None)
        return CompanyUser.objects.create(**validated_data)