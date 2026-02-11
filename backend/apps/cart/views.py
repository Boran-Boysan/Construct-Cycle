from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer
from apps.products.models import Product



class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_cart(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def list(self, request):
        cart = self.get_cart()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = self.get_cart()
        product = get_object_or_404(Product, pk=serializer.validated_data['product_id'])
        quantity = serializer.validated_data.get('quantity', 1)
        
        cart.add_product(product, quantity)
        return Response({'message': 'Ürün sepete eklendi.', 'cart': CartSerializer(cart).data})

    @action(detail=False, methods=['post'])
    def remove(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id gerekli.'}, status=400)
        
        cart = self.get_cart()
        product = get_object_or_404(Product, pk=product_id)
        cart.remove_product(product)
        return Response({'message': 'Ürün sepetten kaldırıldı.', 'cart': CartSerializer(cart).data})

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self.get_cart()
        cart.clear()
        return Response({'message': 'Sepet temizlendi.'})
