"""
Frontend'den gelen kullanıcı verilerini (register, login, profil, şifre, email doğrulama) alır,
kontrol eder (validate eder) ve Django User modeline uygun hale getirir.

Form → API → Serializer → User Model → Veritabanı
"""
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import User, EmailVerification
from .utils import send_verification_email

User = get_user_model()


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
    """Kullanıcı kayıt serializer - Email aktivasyonlu"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'password_confirm', 'user_type']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        """Email benzersiz olmalı"""
        # Eğer aynı email ile kayıtlı AMA email doğrulanmamış kullanıcı varsa, onu sil (yeniden kayıt izni)
        existing_user = User.objects.filter(email=value.lower()).first()
        if existing_user:
            if not existing_user.is_email_verified:
                # Doğrulanmamış hesabı sil, yeniden kayıt yapabilsin
                existing_user.delete()
            else:
                raise serializers.ValidationError("Bu email adresi zaten kayıtlı.")
        return value.lower()

    def validate(self, attrs):
        """Şifre eşleşmesini kontrol et"""
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Şifreler eşleşmiyor."})
        return attrs

    def create(self, validated_data):
        """Kullanıcı oluştur ve aktivasyon kodu gönder"""
        # ✅ DÜZELTİLDİ: is_active=False - Email doğrulanana kadar giriş yapamaz
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', ''),
            user_type=validated_data.get('user_type', 'buyer'),
            password=validated_data['password'],
            is_active=False,           # ✅ Email doğrulanana kadar pasif
            is_email_verified=False     # Email doğrulanmadı
        )

        # Aktivasyon kodu oluştur
        verification_code = EmailVerification.create_for_user(user)

        # Email gönder
        email_sent = send_verification_email(user, verification_code)

        if not email_sent:
            # Email gönderilemezse kullanıcıyı sil ve hata ver
            user.delete()
            raise serializers.ValidationError({
                "email": "Email gönderilemedi. Lütfen email adresinizi kontrol edin ve tekrar deneyin."
            })

        return user


class LoginSerializer(serializers.Serializer):
    """Giriş serializer"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Giriş bilgilerini kontrol et"""
        email = data['email'].lower()

        # ✅ Önce kullanıcıyı email ile bul (authenticate is_active=False olanları reddeder)
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Geçersiz giriş bilgileri.')

        # ✅ Email doğrulama kontrolü - doğrulanmamışsa giriş yapamaz
        if not user_obj.is_email_verified:
            raise serializers.ValidationError(
                'Email adresiniz henüz doğrulanmamış. Lütfen email kutunuzu kontrol edin.'
            )

        # ✅ Hesap aktif değilse (email doğrulanmamış veya admin tarafından deaktif edilmiş)
        if not user_obj.is_active:
            raise serializers.ValidationError('Hesabınız aktif değil.')

        # Şifre kontrolü
        user = authenticate(username=email, password=data['password'])

        if not user:
            raise serializers.ValidationError('E-posta veya şifre hatalı.')

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
    """Email doğrulama kodu serializer"""
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, max_length=6, min_length=6)

    def validate(self, attrs):
        """Kodu doğrula"""
        email = attrs['email'].lower()
        code = attrs['code']

        # Kullanıcıyı bul
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Kullanıcı bulunamadı."})

        # Zaten doğrulanmış mı?
        if user.is_email_verified:
            raise serializers.ValidationError({"code": "Email zaten doğrulanmış."})

        # Doğrulama kodunu bul
        try:
            verification = EmailVerification.objects.get(
                user=user,
                code=code,
                is_used=False
            )
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError({"code": "Geçersiz doğrulama kodu."})

        # Kodun süresi dolmuş mu?
        if verification.is_expired():
            raise serializers.ValidationError({"code": "Doğrulama kodunun süresi dolmuş. Lütfen yeni kod isteyin."})

        attrs['user'] = user
        attrs['verification'] = verification
        return attrs


class ResendVerificationSerializer(serializers.Serializer):
    """Aktivasyon kodunu tekrar gönderme serializer"""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Email kontrolü"""
        try:
            user = User.objects.get(email=value.lower())
        except User.DoesNotExist:
            raise serializers.ValidationError("Kullanıcı bulunamadı.")

        if user.is_email_verified:
            raise serializers.ValidationError("Email zaten doğrulanmış.")

        return value.lower()