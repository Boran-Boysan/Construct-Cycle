
"""
Frontend’den gelen kullanıcı verilerini (register, login, profil, şifre, email doğrulama) alır,
kontrol eder (validate eder) ve
Django User modeline uygun hale getirir.

Form → API → Serializer → User Model → Veritabanı
"""
from rest_framework import serializers # Django REST Framework serializer altyapısı (JSON ↔ Model dönüşümü)
from django.contrib.auth import authenticate # Kullanıcı giriş bilgilerini doğrulamak için Django’nun hazır login fonksiyonu
from .models import User # Projede kullanılan özel User modeli


class UserSerializer(serializers.ModelSerializer):
    """Kullanıcı bilgileri serializer"""

    full_name = serializers.ReadOnlyField()
    is_seller = serializers.ReadOnlyField()
    is_buyer = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'phone', 'user_type', 'is_seller', 'is_buyer',
            'is_email_verified', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_email_verified']


class RegisterSerializer(serializers.ModelSerializer):
    """Kullanıcı kayıt serializer"""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'user_type'
        ]

    def validate(self, data):
        """Şifre kontrolü"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Şifreler eşleşmiyor")
        return data

    def validate_user_type(self, value):
        """Admin olamaz"""
        if value == 'admin':
            raise serializers.ValidationError("Admin rolü için kayıt yapılamaz")
        return value

    def create(self, validated_data):
        """Kullanıcı oluştur"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Giriş serializer"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Giriş bilgilerini kontrol et"""
        user = authenticate(username=data['email'], password=data['password'])

        if not user:
            raise serializers.ValidationError('Geçersiz giriş bilgileri')

        if not user.is_active:
            raise serializers.ValidationError('Hesap deaktif')

        data['user'] = user
        return data


class PasswordChangeSerializer(serializers.Serializer):
    """Şifre değiştirme serializer"""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        """Şifre kontrolü"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Yeni şifreler eşleşmiyor")
        return data

    def validate_old_password(self, value):
        """Eski şifre kontrolü"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Eski şifre hatalı")
        return value


class EmailVerificationSerializer(serializers.Serializer):
    """Email doğrulama serializer"""

    token = serializers.CharField()