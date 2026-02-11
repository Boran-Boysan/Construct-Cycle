from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShippingCompanyViewSet, ShipmentViewSet

router = DefaultRouter()
router.register(r'companies', ShippingCompanyViewSet)
router.register(r'shipments', ShipmentViewSet, basename='shipment')

urlpatterns = [path('', include(router.urls))]
