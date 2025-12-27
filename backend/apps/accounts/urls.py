from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Kimlik Doğrulama
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify-email/', views.EmailVerificationView.as_view(), name='verify-email'),

    # Kullanıcı Profili
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.PasswordChangeView.as_view(), name='change-password'),
]