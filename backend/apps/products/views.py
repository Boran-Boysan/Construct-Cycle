
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Product, Category, ProductImage
from .serializers import (
    ProductSerializer, ProductCreateSerializer, ProductUpdateSerializer,
    ProductListSerializer, CategorySerializer, ProductImageSerializer
)


@extend_schema(tags=['📂 Kategoriler'])
class CategoryListView(generics.ListAPIView):
    """
    Kategori Listesi

    Tüm ürün kategorilerini listeler.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


@extend_schema(
    tags=['🛠️ Ürünler'],
    parameters=[
        OpenApiParameter(name='category', type=OpenApiTypes.INT, description='Kategori ID'),
        OpenApiParameter(name='city', type=OpenApiTypes.STR, description='Şehir'),
        OpenApiParameter(name='condition', type=OpenApiTypes.INT, description='Kullanım durumu (0, 1, 2)'),
        OpenApiParameter(name='min_price', type=OpenApiTypes.NUMBER, description='Minimum fiyat'),
        OpenApiParameter(name='max_price', type=OpenApiTypes.NUMBER, description='Maximum fiyat'),
        OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Ürün adında ara'),
        OpenApiParameter(name='ordering', type=OpenApiTypes.STR,
                         description='Sıralama (sale_price, -sale_price, -created_at)'),
    ]
)
class ProductListView(generics.ListAPIView):
    """
    Ürün Listesi

    Tüm aktif ürünleri listeler. Filtreleme, arama ve sıralama yapılabilir.
    """
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'city', 'condition']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['sale_price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True, is_sold=False)

        # Fiyat filtreleme
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price:
            queryset = queryset.filter(sale_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(sale_price__lte=max_price)

        return queryset.select_related('company', 'category').prefetch_related('images')


@extend_schema(tags=['🛠️ Ürünler'])
class ProductDetailView(generics.RetrieveAPIView):
    """
    Ürün Detayı

    Belirli bir ürünün detay bilgilerini gösterir.
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'

    def get_queryset(self):
        return super().get_queryset().select_related('company', 'category').prefetch_related('images')


@extend_schema(tags=['🛠️ Ürünler - Satıcı'])
class ProductCreateView(generics.CreateAPIView):
    """
    Ürün Ekle (Sadece Satıcılar)

    Yeni ürün ekler. Sadece firma sahibi satıcılar ekleyebilir.
    """
    serializer_class = ProductCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Kullanıcının firması var mı kontrol et
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'error': 'Ürün eklemek için firma sahibi olmalısınız'},
                status=status.HTTP_403_FORBIDDEN
            )

        company = request.user.owned_company
        serializer = self.get_serializer(data=request.data, context={'company': company})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        return Response(
            ProductSerializer(product).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['🛠️ Ürünler - Satıcı'])
class ProductUpdateView(generics.UpdateAPIView):
    """
    Ürün Güncelle (Sadece Satıcılar)

    Mevcut ürünü günceller. Sadece ürünün sahibi güncelleyebilir.
    """
    serializer_class = ProductUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Sadece kendi ürünlerini güncelleyebilir
        if hasattr(self.request.user, 'owned_company'):
            return Product.objects.filter(company=self.request.user.owned_company)
        return Product.objects.none()


@extend_schema(tags=['🛠️ Ürünler - Satıcı'])
class ProductDeleteView(generics.DestroyAPIView):
    """
    Ürün Sil (Sadece Satıcılar)

    Ürünü siler. Sadece ürünün sahibi silebilir.
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Sadece kendi ürünlerini silebilir
        if hasattr(self.request.user, 'owned_company'):
            return Product.objects.filter(company=self.request.user.owned_company)
        return Product.objects.none()


@extend_schema(tags=['🛠️ Ürünler - Satıcı'])
class MyProductsView(generics.ListAPIView):
    """
    Kendi Ürünlerim

    Satıcının kendi ürünlerini listeler.
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'owned_company'):
            return Product.objects.filter(
                company=self.request.user.owned_company
            ).select_related('company', 'category').prefetch_related('images')
        return Product.objects.none()


@extend_schema(tags=['🛠️ Ürünler'])
class ProductSearchView(generics.ListAPIView):
    """
    Ürün Arama

    Gelişmiş ürün arama. İsim, açıklama ve etiketlerde arar.
    """
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')

        if not query:
            return Product.objects.none()

        # PostgreSQL full-text search burada eklenebilir
        # Şimdilik basit arama
        queryset = Product.objects.filter(
            is_active=True,
            is_sold=False
        ).filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(tags__overlap=[query])
        ).select_related('company', 'category').prefetch_related('images')

        return queryset


# Import for search
from django.db import models