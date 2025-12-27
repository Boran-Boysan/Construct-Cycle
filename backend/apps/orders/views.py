
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer,
    OrderListSerializer
)


@extend_schema(tags=['📦 Siparişler'])
class OrderCreateView(generics.CreateAPIView):
    """
    Sipariş Oluştur

    Ürün satın alarak yeni sipariş oluşturur.
    """
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['📦 Siparişler'])
class MyOrdersView(generics.ListAPIView):
    """
    Siparişlerim (Alıcı Olarak)

    Kullanıcının verdiği siparişleri listeler.
    """
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            buyer=self.request.user
        ).select_related('buyer', 'seller_company').prefetch_related('items')


@extend_schema(tags=['📦 Siparişler'])
class MySalesView(generics.ListAPIView):
    """
    Satışlarım (Satıcı Olarak)

    Firmanıza yapılan siparişleri listeler.
    """
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Kullanıcının firması var mı kontrol et
        if not hasattr(self.request.user, 'owned_company'):
            return Order.objects.none()

        return Order.objects.filter(
            seller_company=self.request.user.owned_company
        ).select_related('buyer', 'seller_company').prefetch_related('items')


@extend_schema(tags=['📦 Siparişler'])
class OrderDetailView(generics.RetrieveAPIView):
    """
    Sipariş Detayı

    Belirli bir siparişin detay bilgilerini gösterir.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Kullanıcı ya alıcı ya da satıcı firma sahibi olmalı
        user = self.request.user

        queryset = Order.objects.filter(
            models.Q(buyer=user)
        )

        # Eğer firma sahibiyse, satışlarını da göster
        if hasattr(user, 'owned_company'):
            queryset = queryset | Order.objects.filter(
                seller_company=user.owned_company
            )

        return queryset.select_related('buyer', 'seller_company').prefetch_related('items')


@extend_schema(tags=['📦 Siparişler - Satıcı'])
class OrderStatusUpdateView(generics.UpdateAPIView):
    """
    Sipariş Durumu Güncelle (Sadece Satıcı)

    Satıcı siparişin durumunu güncelleyebilir.
    """
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Sadece kendi firmasının siparişlerini güncelleyebilir
        if hasattr(self.request.user, 'owned_company'):
            return Order.objects.filter(seller_company=self.request.user.owned_company)
        return Order.objects.none()

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Durumu güncelle
        order.status = serializer.validated_data['status']

        # Satıcı notu varsa ekle
        if 'seller_note' in serializer.validated_data:
            order.seller_note = serializer.validated_data['seller_note']

        order.save()

        return Response(OrderSerializer(order).data)


@extend_schema(tags=['📦 Siparişler'])
class OrderCancelView(APIView):
    """
    Sipariş İptal Et

    Alıcı beklemedeki siparişini iptal edebilir.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        # Siparişi al
        order = get_object_or_404(
            Order,
            id=id,
            buyer=request.user
        )

        # Sadece beklemedeki siparişler iptal edilebilir
        if order.status != 'pending':
            return Response(
                {'error': 'Sadece beklemedeki siparişler iptal edilebilir'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Durumu güncelle
        order.status = 'cancelled'
        order.save()

        # Stok geri ekle
        for item in order.items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.is_sold = False
            product.save()

        return Response({
            'message': 'Sipariş iptal edildi',
            'order': OrderSerializer(order).data
        })


# Import for Q queries
from django.db import models