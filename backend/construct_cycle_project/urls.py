from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

admin.site.site_header = "ConstructCycle Yönetim Paneli"
admin.site.site_title = "ConstructCycle Admin"
admin.site.index_title = "Yönetim Paneli"

urlpatterns = [
    # 🏠 Landing page
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),

    # 👨‍💼 Admin Panel
    path('admin/', admin.site.urls, name='admin-panel'),

    # 📚 API Documentation (Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='api-redoc'),

    # 🔐 Authentication & User Management
    path('api/v1/auth/', include(('apps.accounts.urls', 'accounts'), namespace='auth')),

    # 🏢 Companies
    path('api/v1/companies/', include(('apps.companies.urls', 'companies'), namespace='companies')),

    # 🛒 Products & Categories
    path('api/v1/products/', include(('apps.products.urls', 'products'), namespace='products')),

    # 📦 Orders
    path('api/v1/orders/', include(('apps.orders.urls', 'orders'), namespace='orders')),

    # 💬 Conversations
    path('api/v1/conversations/', include(('apps.conversations.urls', 'conversations'), namespace='conversations')),

    # 📊 Stock Management
    path('api/v1/stock/', include(('apps.stock.urls', 'stock'), namespace='stock')),
]

# Static ve Media dosyaları (Development için)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)