"""
Dashboard API Views + Email Doğrulama
Alıcı ve Satıcı dashboard'ları ve email doğrulama işlemleri
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.db.models import Sum, Count, Q
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

from .serializers import (
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    UserSerializer,
)
from .models import EmailVerification
from .utils import send_verification_email, send_activation_success_email

User = get_user_model()


# ============================================
# EMAIL DOĞRULAMA ENDPOINT'LERİ
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
        send_activation_success_email(user)

        # ✅ Otomatik giriş için token oluştur
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'success': True,
            'message': 'Email adresiniz başarıyla doğrulandı! Hesabınız aktif edildi.',
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

    # Hata mesajlarını düzgün döndür
    errors = serializer.errors
    error_message = 'Doğrulama başarısız.'

    # Field-specific hataları çıkar
    if 'code' in errors:
        error_message = errors['code'][0] if isinstance(errors['code'], list) else errors['code']
    elif 'email' in errors:
        error_message = errors['email'][0] if isinstance(errors['email'], list) else errors['email']
    elif 'non_field_errors' in errors:
        error_message = errors['non_field_errors'][0]

    return Response({
        'success': False,
        'message': str(error_message),
        'errors': errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_view(request):
    """
    Doğrulama kodunu tekrar gönder
    POST /api/v1/auth/resend-verification/
    Body: { "email": "..." }
    """
    serializer = ResendVerificationSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Kullanıcı bulunamadı.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Yeni kod oluştur
        verification_code = EmailVerification.create_for_user(user)

        # Email gönder
        email_sent = send_verification_email(user, verification_code)

        if email_sent:
            return Response({
                'success': True,
                'message': 'Yeni doğrulama kodu email adresinize gönderildi.'
            })
        else:
            return Response({
                'success': False,
                'message': 'Email gönderilemedi. Lütfen tekrar deneyin.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'success': False,
        'message': 'Geçersiz istek.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# DASHBOARD ENDPOINT'LERİ
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buyer_dashboard_stats(request):
    """
    Alıcı dashboard istatistikleri
    GET /api/v1/auth/buyer-dashboard-stats/
    """
    user = request.user

    try:
        from apps.orders.models import Order
        total_orders = Order.objects.filter(buyer=user).count()
        pending_orders = Order.objects.filter(
            buyer=user,
            status__in=['pending', 'processing']
        ).count()
    except ImportError:
        total_orders = 0
        pending_orders = 0

    try:
        from apps.products.models import Product
        favorites = 0
    except ImportError:
        favorites = 0

    try:
        from apps.conversations.models import Conversation
        unread_messages = Conversation.objects.filter(
            participants=user,
            messages__is_read=False
        ).exclude(messages__sender=user).distinct().count()
    except ImportError:
        unread_messages = 0

    return Response({
        'success': True,
        'data': {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'favorites': favorites,
            'unread_messages': unread_messages,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_dashboard_stats(request):
    """
    Satıcı dashboard istatistikleri
    GET /api/v1/auth/seller-dashboard-stats/
    """
    user = request.user

    if user.user_type != 'seller':
        return Response({
            'success': False,
            'message': 'Bu endpoint sadece satıcılar için geçerlidir.'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        from apps.products.models import Product
        total_products = Product.objects.filter(
            company__owner=user,
            is_active=True
        ).count()
    except ImportError:
        total_products = 0

    try:
        from apps.orders.models import Order
        total_sales_data = Order.objects.filter(
            seller=user,
            status__in=['delivered', 'completed']
        ).aggregate(total=Sum('total_price'))
        total_sales = total_sales_data['total'] or 0

        pending_sales = Order.objects.filter(
            seller=user,
            status__in=['pending', 'processing']
        ).count()
    except ImportError:
        total_sales = 0
        pending_sales = 0

    rating = 4.5

    return Response({
        'success': True,
        'data': {
            'total_products': total_products,
            'total_sales': float(total_sales),
            'pending_sales': pending_sales,
            'rating': rating,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_orders(request):
    """
    Son siparişler (Alıcı için)
    GET /api/v1/auth/recent-orders/?limit=5
    """
    user = request.user
    limit = int(request.GET.get('limit', 5))

    try:
        from apps.orders.models import Order
        from apps.orders.serializers import OrderSerializer
        orders = Order.objects.filter(buyer=user).order_by('-created_at')[:limit]
        serializer = OrderSerializer(orders, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except ImportError:
        return Response({
            'success': True,
            'data': []
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_sales(request):
    """
    Son satışlar (Satıcı için)
    GET /api/v1/auth/recent-sales/?limit=5
    """
    user = request.user

    if user.user_type != 'seller':
        return Response({
            'success': False,
            'message': 'Bu endpoint sadece satıcılar için geçerlidir.'
        }, status=status.HTTP_403_FORBIDDEN)

    limit = int(request.GET.get('limit', 5))

    try:
        from apps.orders.models import Order
        from apps.orders.serializers import OrderSerializer
        sales = Order.objects.filter(seller=user).order_by('-created_at')[:limit]
        serializer = OrderSerializer(sales, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    except ImportError:
        return Response({
            'success': True,
            'data': []
        })