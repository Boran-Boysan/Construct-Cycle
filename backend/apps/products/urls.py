from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Kategoriler
    path('categories/', views.CategoryListView.as_view(), name='category-list'),

    # Ürünler (Public)
    path('', views.ProductListView.as_view(), name='product-list'),
    path('search/', views.ProductSearchView.as_view(), name='product-search'),
    path('<int:id>/', views.ProductDetailView.as_view(), name='product-detail'),

    # Ürünler (Satıcı)
    path('my-products/', views.MyProductsView.as_view(), name='my-products'),
    path('create/', views.ProductCreateView.as_view(), name='product-create'),
    path('<int:id>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('<int:id>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
]