"""
Accounts Views - Kayıt, Giriş, Email Doğrulama, Profil
apps/accounts/views.py
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    PasswordChangeSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
)
from .models import EmailVerification
from .utils import send_verification_email, send_activation_success_email

User = get_user_model()


# ============================================
# KAYIT
# ============================================
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Kullanıcı kaydı - Email doğrulama kodu gönderir
    POST /api/v1/auth/register/
    """
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'success': True,
            'message': 'Kayıt başarılı! Email adresinize doğrulama kodu gönderildi.',
            'email': user.email,
        }, status=status.HTTP_201_CREATED)

    # Hata mesajlarını düzgün döndür
    errors = serializer.errors
    error_message = 'Kayıt sırasında bir hata oluştu.'

    if 'email' in errors:
        error_message = errors['email'][0] if isinstance(errors['email'], list) else str(errors['email'])
    elif 'password_confirm' in errors:
        error_message = errors['password_confirm'][0] if isinstance(errors['password_confirm'], list) else str(errors['password_confirm'])
    elif 'non_field_errors' in errors:
        error_message = errors['non_field_errors'][0]

    return Response({
        'success': False,
        'message': str(error_message),
        'errors': errors,
    }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# GİRİŞ
# ============================================
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Kullanıcı girişi
    POST /api/v1/auth/login/
    """
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'success': True,
            'message': 'Giriş başarılı!',
            'token': token.key,
            'user': UserSerializer(user).data,
        })

    errors = serializer.errors
    error_message = 'Giriş yapılırken bir hata oluştu.'

    if 'non_field_errors' in errors:
        error_message = errors['non_field_errors'][0]
    elif 'email' in errors:
        error_message = errors['email'][0] if isinstance(errors['email'], list) else str(errors['email'])

    return Response({
        'success': False,
        'message': str(error_message),
        'errors': errors,
    }, status=status.HTTP_401_UNAUTHORIZED)


# ============================================
# EMAIL DOĞRULAMA
# ============================================
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_view(request):
    """
    Email doğrulama kodu kontrol et, kullanıcıyı aktif et
    POST /api/v1/auth/verify-email/
    Body: { "email": "...", "code": "123456" }
    """
    serializer = EmailVerificationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data['user']
        verification = serializer.validated_data['verification']

        # ✅ Kodu kullanıldı olarak işaretle
        verification.is_used = True
        verification.save()

        # ✅ Kullanıcıyı aktif et ve email doğrulandı olarak işaretle
        user.is_email_verified = True
        user.is_active = True
        user.save(update_fields=['is_email_verified', 'is_active'])

        # ✅ "Hesabınız aktif" maili gönder
        try:
            send_activation_success_email(user)
        except Exception as e:
            print(f"Aktivasyon maili gönderilemedi: {e}")
            # Mail gönderilemese bile doğrulama başarılı sayılsın

        # ✅ Otomatik giriş için token oluştur
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'success': True,
            'message': 'Email adresiniz başarıyla doğrulandı! Hesabınız aktif edildi.',
            'token': token.key,
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)

    # Hata mesajlarını düzgün döndür
    errors = serializer.errors
    error_message = 'Doğrulama başarısız.'

    if 'code' in errors:
        error_message = errors['code'][0] if isinstance(errors['code'], list) else str(errors['code'])
    elif 'email' in errors:
        error_message = errors['email'][0] if isinstance(errors['email'], list) else str(errors['email'])
    elif 'non_field_errors' in errors:
        error_message = errors['non_field_errors'][0]

    return Response({
        'success': False,
        'message': str(error_message),
        'errors': errors,
    }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# YENİDEN KOD GÖNDER
# ============================================
@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_view(request):
    """
    Doğrulama kodunu tekrar gönder
    POST /api/v1/auth/resend-verification/
    """
    serializer = ResendVerificationSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Kullanıcı bulunamadı.',
            }, status=status.HTTP_404_NOT_FOUND)

        # Yeni kod oluştur
        verification_code = EmailVerification.create_for_user(user)

        # Email gönder
        email_sent = send_verification_email(user, verification_code)

        if email_sent:
            return Response({
                'success': True,
                'message': 'Yeni doğrulama kodu email adresinize gönderildi.',
            })
        else:
            return Response({
                'success': False,
                'message': 'Email gönderilemedi. Lütfen tekrar deneyin.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'success': False,
        'message': 'Geçersiz istek.',
        'errors': serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# ÇIKIŞ
# ============================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Kullanıcı çıkışı - Token sil
    POST /api/v1/auth/logout/
    """
    try:
        request.user.auth_token.delete()
    except Exception:
        pass

    return Response({
        'success': True,
        'message': 'Çıkış yapıldı.',
    })


# ============================================
# PROFİL
# ============================================
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Profil görüntüleme ve güncelleme
    GET/PATCH /api/v1/auth/profile/
    """
    user = request.user

    if request.method == 'GET':
        return Response(UserSerializer(user).data)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# ŞİFRE DEĞİŞTİRME
# ============================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Şifre değiştirme
    POST /api/v1/auth/change-password/
    """
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({
            'success': True,
            'message': 'Şifre başarıyla değiştirildi.',
        })

    return Response({
        'success': False,
        'errors': serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)