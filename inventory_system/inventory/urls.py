from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.intro_page, name='intro_page'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # Supplier URLs
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', views.SupplierCreateView.as_view(), name='supplier_add'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),

    # Sale URLs
    path('sales/', views.SaleListView.as_view(), name='sale_list'),
    path('sales/add/', views.SaleCreateView.as_view(), name='sale_add'),
    
    #Export URLs
    path('products/export/', views.export_products_csv, name='export_products_csv'),
    path('sales/export/', views.export_sales_csv, name='export_sales_csv'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('orders/', views.SupplierOrderListView.as_view(), name='supplierorder_list'),
    path('orders/add/', views.SupplierOrderCreateView.as_view(), name='supplierorder_add'),
    path('orders/<int:pk>/edit/', views.SupplierOrderUpdateView.as_view(), name='supplierorder_edit'),
    path('analytics/sales/', views.SalesAnalyticsView.as_view(), name='sales_analytics'),
    path('analytics/inventory/', views.InventoryAnalyticsView.as_view(), name='inventory_analytics'),
]