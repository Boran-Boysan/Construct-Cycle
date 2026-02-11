from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Address, City, District
from .serializers import (
    AddressSerializer, AddressCreateSerializer,
    CitySerializer, CityWithDistrictsSerializer, DistrictSerializer
)


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_active=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return AddressCreateSerializer
        return AddressSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        address = self.get_object()
        address.is_default = True
        address.save()
        return Response({'message': 'Varsayılan adres güncellendi.'})

    @action(detail=False, methods=['get'])
    def default(self, request):
        address = self.get_queryset().filter(is_default=True).first()
        if address:
            return Response(AddressSerializer(address).data)
        return Response({'detail': 'Varsayılan adres bulunamadı.'}, status=404)


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = City.objects.filter(is_active=True)
    serializer_class = CitySerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CityWithDistrictsSerializer(instance)
        return Response(serializer.data)


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = DistrictSerializer

    def get_queryset(self):
        queryset = District.objects.filter(is_active=True)
        city_id = self.request.query_params.get('city')
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        return queryset
