
from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    # Stok Hareketleri
    path('movements/', views.StockMovementListView.as_view(), name='movement-list'),
    path('movements/create/', views.StockMovementCreateView.as_view(), name='movement-create'),
    path('movements/product/<int:product_id>/', views.ProductStockHistoryView.as_view(), name='product-history'),

    # Stok Uyarıları
    path('alerts/', views.StockAlertListView.as_view(), name='alert-list'),
    path('alerts/create/', views.StockAlertCreateView.as_view(), name='alert-create'),
    path('alerts/<int:id>/update/', views.StockAlertUpdateView.as_view(), name='alert-update'),
    path('alerts/low-stock/', views.LowStockProductsView.as_view(), name='low-stock'),

    # Web Sitesi Satışları
    path('sales/', views.SaleToWebsiteListView.as_view(), name='sale-list'),
    path('sales/create/', views.SaleToWebsiteCreateView.as_view(), name='sale-create'),
    path('sales/<int:sale_id>/remove/', views.RemoveFromWebsiteView.as_view(), name='sale-remove'),

    # Raporlar
    path('summary/', views.StockSummaryView.as_view(), name='summary'),
]