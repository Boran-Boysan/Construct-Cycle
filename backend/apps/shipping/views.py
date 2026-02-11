from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import ShippingCompany, Shipment
from .serializers import ShippingCompanySerializer, ShipmentSerializer

class ShippingCompanyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = ShippingCompany.objects.filter(is_active=True)
    serializer_class = ShippingCompanySerializer

class ShipmentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ShipmentSerializer
    def get_queryset(self):
        return Shipment.objects.filter(order__buyer=self.request.user)
