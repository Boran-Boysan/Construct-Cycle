from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# ✅ Bulk delete view import
from construct_cycle_project.views import bulk_delete_view

admin.site.site_header = "ConstructCycle Yönetim Paneli"
admin.site.site_title = "ConstructCycle Admin"
admin.site.index_title = "Yönetim Paneli"

urlpatterns = [
    # 🏠 Landing & Auth Pages
    path('', TemplateView.as_view(template_name='pages/landing.html'), name='landing'),
    path('index.html', TemplateView.as_view(template_name='pages/landing.html'), name='index'),
    path('login.html', TemplateView.as_view(template_name='pages/login.html'), name='login-page'),
    path('register.html', TemplateView.as_view(template_name='pages/register.html'), name='register-page'),
    path('verify-email.html', TemplateView.as_view(template_name='pages/verify-email.html'), name='verify-email-page'),

    # 📊 Dashboard Pages
    path('buyer-dashboard.html', TemplateView.as_view(template_name='pages/buyer-dashboard.html'),
         name='buyer-dashboard-page'),
    path('seller-dashboard.html', TemplateView.as_view(template_name='pages/seller-dashboard.html'),
         name='seller-dashboard-page'),

    # 👤 Profile & Settings
    path('profile.html', TemplateView.as_view(template_name='pages/profile.html'), name='profile-page'),
    path('settings.html', TemplateView.as_view(template_name='pages/settings.html'), name='settings-page'),

    # 🛒 Product Pages
    path('products.html', TemplateView.as_view(template_name='pages/products.html'), name='products-page'),
    path('product-detail.html', TemplateView.as_view(template_name='pages/product-detail.html'),
         name='product-detail-page'),
    path('add-product.html', TemplateView.as_view(template_name='pages/add-product.html'), name='add-product-page'),
    path('my-products.html', TemplateView.as_view(template_name='pages/my-products.html'), name='my-products-page'),

    # 📦 Order Pages
    path('my-orders.html', TemplateView.as_view(template_name='pages/my-orders.html'), name='my-orders-page'),
    path('my-sales.html', TemplateView.as_view(template_name='pages/my-sales.html'), name='my-sales-page'),
    path('order-detail.html', TemplateView.as_view(template_name='pages/order-detail.html'), name='order-detail-page'),

    # 💬 Communication Pages
    path('messages.html', TemplateView.as_view(template_name='pages/messages.html'), name='messages-page'),

    # ❤️ Favorites
    path('favorites.html', TemplateView.as_view(template_name='pages/favorites.html'), name='favorites-page'),

    # 🏢 Company Pages
    path('my-company.html', TemplateView.as_view(template_name='pages/my-company.html'), name='my-company-page'),
    path('company-detail.html', TemplateView.as_view(template_name='pages/company-detail.html'),
         name='company-detail-page'),

    # ✅ Bulk Delete - admin/'den ÖNCE tanımlanmalı
    path('admin/bulk-delete-all/', bulk_delete_view, name='admin_bulk_delete_all'),

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