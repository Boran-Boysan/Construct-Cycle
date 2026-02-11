from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, UserWarningViewSet, UserBanViewSet

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'warnings', UserWarningViewSet, basename='warning')
router.register(r'bans', UserBanViewSet, basename='ban')

urlpatterns = [path('', include(router.urls))]
