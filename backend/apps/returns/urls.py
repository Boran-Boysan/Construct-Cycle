from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReturnRequestViewSet, RefundViewSet

router = DefaultRouter()
router.register(r'', ReturnRequestViewSet, basename='return')
router.register(r'refunds', RefundViewSet, basename='refund')

urlpatterns = [path('', include(router.urls))]
