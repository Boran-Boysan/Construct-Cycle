from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Q
from drf_spectacular.utils import extend_schema
from .models import StockMovement, StockAlert, SaleToWebsite
from .serializers import (
    StockMovementSerializer, StockMovementCreateSerializer,
    StockAlertSerializer, StockAlertCreateSerializer,
    SaleToWebsiteSerializer, SaleToWebsiteCreateSerializer,
    StockSummarySerializer
)


@extend_schema(tags=['📊 Stok Hareketleri'])
class StockMovementListView(generics.ListAPIView):
    """
    Stok Hareketleri Listesi

    Firmanın tüm stok hareketlerini listeler.
    """
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Kullanıcının firması var mı kontrol et
        if not hasattr(self.request.user, 'owned_company'):
            return StockMovement.objects.none()

        # Firma ürünlerinin stok hareketleri
        return StockMovement.objects.filter(
            product__company=self.request.user.owned_company
        ).select_related('product', 'performed_by')


@extend_schema(tags=['📊 Stok Hareketleri'])
class StockMovementCreateView(generics.CreateAPIView):
    """
    Stok Hareketi Oluştur

    Yeni stok hareketi (giriş, çıkış, düzeltme) kaydeder.
    """
    serializer_class = StockMovementCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        stock_movement = serializer.save()

        return Response(
            StockMovementSerializer(stock_movement).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['📊 Stok Hareketleri'])
class ProductStockHistoryView(generics.ListAPIView):
    """
    Ürün Stok Geçmişi

    Belirli bir ürünün tüm stok hareketlerini listeler.
    """
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')

        # Kullanıcının firması var mı kontrol et
        if not hasattr(self.request.user, 'owned_company'):
            return StockMovement.objects.none()

        return StockMovement.objects.filter(
            product_id=product_id,
            product__company=self.request.user.owned_company
        ).select_related('product', 'performed_by')


@extend_schema(tags=['🔔 Stok Uyarıları'])
class StockAlertListView(generics.ListAPIView):
    """
    Stok Uyarıları Listesi

    Firmanın tüm stok uyarılarını listeler.
    """
    serializer_class = StockAlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Kullanıcının firması var mı kontrol et
        if not hasattr(self.request.user, 'owned_company'):
            return StockAlert.objects.none()

        return StockAlert.objects.filter(
            product__company=self.request.user.owned_company
        ).select_related('product')


@extend_schema(tags=['🔔 Stok Uyarıları'])
class StockAlertCreateView(generics.CreateAPIView):
    """
    Stok Uyarısı Oluştur

    Ürün için minimum stok uyarısı ayarlar.
    """
    serializer_class = StockAlertCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Ürün kontrolü
        product = serializer.validated_data['product']

        if not hasattr(request.user, 'owned_company') or product.company != request.user.owned_company:
            return Response(
                {'error': 'Bu ürün sizin firmanıza ait değil'},
                status=status.HTTP_403_FORBIDDEN
            )

        stock_alert = serializer.save()

        return Response(
            StockAlertSerializer(stock_alert).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['🔔 Stok Uyarıları'])
class StockAlertUpdateView(generics.UpdateAPIView):
    """
    Stok Uyarısı Güncelle

    Mevcut stok uyarısını günceller.
    """
    serializer_class = StockAlertCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Sadece kendi firmasının uyarılarını güncelleyebilir
        if hasattr(self.request.user, 'owned_company'):
            return StockAlert.objects.filter(product__company=self.request.user.owned_company)
        return StockAlert.objects.none()


@extend_schema(tags=['🔔 Stok Uyarıları'])
class LowStockProductsView(APIView):
    """
    Düşük Stoklu Ürünler

    Minimum seviyenin altındaki ürünleri listeler.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Kullanıcının firması var mı kontrol et
        if not hasattr(request.user, 'owned_company'):
            return Response([])

        # Düşük stoklu ürünler
        low_stock_alerts = StockAlert.objects.filter(
            product__company=request.user.owned_company,
            is_active=True
        ).select_related('product')

        low_stock_products = []
        for alert in low_stock_alerts:
            if alert.is_below_minimum:
                low_stock_products.append({
                    'product_id': alert.product.id,
                    'product_name': alert.product.name,
                    'current_quantity': alert.product.stock_quantity,
                    'minimum_quantity': alert.minimum_quantity,
                    'shortage': alert.minimum_quantity - alert.product.stock_quantity
                })

        return Response(low_stock_products)


@extend_schema(tags=['🌐 Web Sitesi Satışları'])
class SaleToWebsiteListView(generics.ListAPIView):
    """
    Web Sitesi Satış İlanları

    Web sitesine çıkarılan ürünleri listeler.
    """
    serializer_class = SaleToWebsiteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Kullanıcının firması var mı kontrol et
        if not hasattr(self.request.user, 'owned_company'):
            return SaleToWebsite.objects.none()

        return SaleToWebsite.objects.filter(
            product__company=self.request.user.owned_company
        ).select_related('product', 'listed_by', 'stock_movement')


@extend_schema(tags=['🌐 Web Sitesi Satışları'])
class SaleToWebsiteCreateView(generics.CreateAPIView):
    """
    Web Sitesine Satışa Çıkar

    Stoktan ürünü web sitesine satışa çıkarır.
    """
    serializer_class = SaleToWebsiteCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        sale_listing = serializer.save()

        return Response(
            SaleToWebsiteSerializer(sale_listing).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['🌐 Web Sitesi Satışları'])
class RemoveFromWebsiteView(APIView):
    """
    İlandan Kaldır

    Ürünü web sitesi satışından kaldırır.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, sale_id):
        # Satış ilanını al
        sale_listing = get_object_or_404(
            SaleToWebsite,
            id=sale_id
        )

        # Yetki kontrolü
        if not hasattr(request.user, 'owned_company') or \
                sale_listing.product.company != request.user.owned_company:
            return Response(
                {'error': 'Bu işlem için yetkiniz yok'},
                status=status.HTTP_403_FORBIDDEN
            )

        # İlandan kaldır
        sale_listing.remove_listing()

        # Stok geri ekle
        StockMovement.objects.create(
            product=sale_listing.product,
            movement_type='in',
            quantity=sale_listing.listed_quantity,
            reason=f"İlandan kaldırıldı - İlan #{sale_listing.id}",
            performed_by=request.user
        )

        return Response({
            'message': 'Ürün ilandan kaldırıldı ve stok geri eklendi',
            'sale_listing': SaleToWebsiteSerializer(sale_listing).data
        })


@extend_schema(tags=['📊 Stok Raporları'])
class StockSummaryView(APIView):
    """
    Stok Özeti

    Firmanın genel stok durumunu özetler.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Kullanıcının firması var mı kontrol et
        if not hasattr(request.user, 'owned_company'):
            return Response({
                'error': 'Firma sahibi olmalısınız'
            }, status=status.HTTP_403_FORBIDDEN)

        from apps.products.models import Product
        company = request.user.owned_company

        # Toplam ürün sayısı
        total_products = Product.objects.filter(company=company).count()

        # Toplam stok değeri
        products = Product.objects.filter(company=company)
        total_stock_value = sum(
            p.stock_quantity * p.sale_price for p in products
        )

        # Düşük stoklu ürünler
        low_stock_alerts = StockAlert.objects.filter(
            product__company=company,
            is_active=True
        )
        low_stock_count = sum(1 for alert in low_stock_alerts if alert.is_below_minimum)

        # Stokta olmayan ürünler
        out_of_stock_count = Product.objects.filter(
            company=company,
            stock_quantity=0
        ).count()

        # Aktif ilanlar
        active_listings = SaleToWebsite.objects.filter(
            product__company=company,
            status='listed'
        ).count()

        summary = {
            'total_products': total_products,
            'total_stock_value': total_stock_value,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'active_listings': active_listings
        }

        serializer = StockSummarySerializer(summary)
        return Response(serializer.data)