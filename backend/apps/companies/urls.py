
from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    # Firma İşlemleri
    path('register/', views.CompanyRegisterView.as_view(), name='company-register'),
    path('my-company/', views.MyCompanyView.as_view(), name='my-company'),
    path('<int:id>/', views.CompanyDetailView.as_view(), name='company-detail'),

    # Firma Çalışanları
    path('users/', views.CompanyUserListView.as_view(), name='company-users-list'),
    path('users/add/', views.CompanyUserCreateView.as_view(), name='company-user-create'),
    path('users/<int:id>/', views.CompanyUserDetailView.as_view(), name='company-user-detail'),
]