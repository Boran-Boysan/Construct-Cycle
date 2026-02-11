"""
Accounts URL Configuration
apps/accounts/urls.py
"""
from django.urls import path
from . import views
from .dashboard_views import (
    buyer_dashboard_stats,
    seller_dashboard_stats,
    recent_orders,
    recent_sales,
)

urlpatterns = [
    # 🔐 Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 📧 Email Doğrulama
    path('verify-email/', views.verify_email_view, name='verify-email'),
    path('resend-verification/', views.resend_verification_view, name='resend-verification'),

    # 👤 Profil
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change-password'),

    # 📊 Dashboard Stats
    path('buyer-dashboard-stats/', buyer_dashboard_stats, name='buyer-dashboard-stats'),
    path('seller-dashboard-stats/', seller_dashboard_stats, name='seller-dashboard-stats'),
    path('recent-orders/', recent_orders, name='recent-orders'),
    path('recent-sales/', recent_sales, name='recent-sales'),
]