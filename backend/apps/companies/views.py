
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .models import Company, CompanyUser
from .serializers import (
    CompanySerializer, CompanyCreateSerializer,
    CompanyUserSerializer, CompanyUserCreateSerializer
)


@extend_schema(tags=['🏢 Firmalar'])
class CompanyRegisterView(generics.CreateAPIView):
    """
    Firma Kaydı

    Yeni firma kaydı oluşturur. Sadece 'seller' kullanıcılar firma oluşturabilir.
    """
    serializer_class = CompanyCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        return Response(
            CompanySerializer(company).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['🏢 Firmalar'])
class MyCompanyView(generics.RetrieveUpdateAPIView):
    """
    Kendi Firmam

    Kullanıcının kendi firmasını görüntüler ve günceller.
    """
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Kullanıcının firmasını getir"""
        if not hasattr(self.request.user, 'owned_company'):
            from rest_framework.exceptions import NotFound
            raise NotFound("Henüz bir firmanız yok")
        return self.request.user.owned_company


@extend_schema(tags=['🏢 Firmalar'])
class CompanyDetailView(generics.RetrieveAPIView):
    """
    Firma Detayı

    Belirli bir firmanın bilgilerini görüntüler.
    """
    queryset = Company.objects.filter(is_verified=True)
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


@extend_schema(tags=['👥 Firma Çalışanları'])
class CompanyUserListView(generics.ListAPIView):
    """
    Firma Çalışanları Listesi

    Kendi firmasının çalışanlarını listeler.
    """
    serializer_class = CompanyUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Sadece kendi firmasının çalışanlarını getir"""
        if not hasattr(self.request.user, 'owned_company'):
            return CompanyUser.objects.none()
        return CompanyUser.objects.filter(company=self.request.user.owned_company)


@extend_schema(tags=['👥 Firma Çalışanları'])
class CompanyUserCreateView(generics.CreateAPIView):
    """
    Firma Çalışanı Ekle

    Firmaya yeni çalışan ekler. Sadece firma sahibi ekleyebilir.
    """
    serializer_class = CompanyUserCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Kullanıcının firması var mı kontrol et
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'error': 'Firma sahibi olmalısınız'},
                status=status.HTTP_403_FORBIDDEN
            )

        company = request.user.owned_company
        serializer = self.get_serializer(data=request.data, context={'company': company})
        serializer.is_valid(raise_exception=True)
        company_user = serializer.save()

        return Response(
            CompanyUserSerializer(company_user).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['👥 Firma Çalışanları'])
class CompanyUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Firma Çalışanı Detay

    Firma çalışanını görüntüler, günceller veya siler.
    """
    serializer_class = CompanyUserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        """Sadece kendi firmasının çalışanlarını getir"""
        if not hasattr(self.request.user, 'owned_company'):
            return CompanyUser.objects.none()
        return CompanyUser.objects.filter(company=self.request.user.owned_company)