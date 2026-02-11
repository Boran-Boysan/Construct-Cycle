from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AddressViewSet, CityViewSet, DistrictViewSet

router = DefaultRouter()
router.register(r'', AddressViewSet, basename='address')
router.register(r'cities', CityViewSet, basename='city')
router.register(r'districts', DistrictViewSet, basename='district')

urlpatterns = [
    path('', include(router.urls)),
]
