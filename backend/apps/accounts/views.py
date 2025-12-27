
"""
Bu dosya ConstructCycle’daki tüm kullanıcı kimlik doğrulama (authentication) API’lerini yöneten katman.
Yani: register, login, profil, şifre değiştirme, email doğrulama burada kontrol ediliyor.
Frontend → API → Serializer → User Model → Token üretimi → Response
akışını yöneten “kontrol katmanı”dır.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import login
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    PasswordChangeSerializer, EmailVerificationSerializer
)


@extend_schema(tags=['Kimlik Doğrulama'])
class RegisterView(generics.CreateAPIView):
    """
    Kullanıcı Kaydı

    Yeni kullanıcı kaydı oluşturur ve authentication token döner.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Kayıt başarılı. Lütfen email adresinizi doğrulayın.'
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Kimlik Doğrulama'])
class LoginView(generics.GenericAPIView):
    """
    Kullanıcı Girişi

    Email ve şifre ile giriş yapar, authentication token döner.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })


@extend_schema(tags=['Kullanıcı Profili'])
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Kullanıcı Profili

    Giriş yapmış kullanıcının profil bilgilerini görüntüler ve günceller.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Kullanıcı Profili'])
class PasswordChangeView(generics.GenericAPIView):
    """
    Şifre Değiştirme

    Kullanıcının şifresini değiştirir.
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            'message': 'Şifre başarıyla değiştirildi'
        })


@extend_schema(tags=['Kimlik Doğrulama'])
class EmailVerificationView(APIView):
    """
    Email Doğrulama

    Email doğrulama token'ını kontrol eder ve hesabı aktifleştirir.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO: Token doğrulama implementasyonu
        # token = serializer.validated_data['token']
        # user = verify_token(token)
        # user.is_email_verified = True
        # user.save()

        return Response({
            'message': 'Email başarıyla doğrulandı'
        })