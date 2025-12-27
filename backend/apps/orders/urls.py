
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Sipariş Oluşturma
    path('create/', views.OrderCreateView.as_view(), name='order-create'),

    # Siparişlerim (Alıcı)
    path('my-orders/', views.MyOrdersView.as_view(), name='my-orders'),

    # Satışlarım (Satıcı)
    path('my-sales/', views.MySalesView.as_view(), name='my-sales'),

    # Sipariş Detayı
    path('<int:id>/', views.OrderDetailView.as_view(), name='order-detail'),

    # Sipariş Durumu Güncelle (Satıcı)
    path('<int:id>/update-status/', views.OrderStatusUpdateView.as_view(), name='order-update-status'),

    # Sipariş İptal (Alıcı)
    path('<int:id>/cancel/', views.OrderCancelView.as_view(), name='order-cancel'),
]