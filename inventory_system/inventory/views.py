import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import F, Count, Avg, Min, Max
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Product, Supplier, Sale, SupplierOrder
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.core.mail import mail_admins
from django import forms

#Create your views here

@login_required
def dashboard(request):
    products = Product.objects.all()
    low_stock = products.filter(quantity__lte=F('low_stock_threshold'))
    sales = Sale.objects.order_by('-sale_date')[:5]

    # In-app notifications
    notifications = []
    for product in low_stock:
        notifications.append(f"Low stock: {product.name} ({product.quantity} left)")

    # Inventory Forecasting
    forecasted_out_products = []
    thirty_days_ago = timezone.now() - timedelta(days=30)
    for product in products:
        sales_last_30 = Sale.objects.filter(product=product, sale_date__gte=thirty_days_ago)
        total_sold = sum(s.quantity for s in sales_last_30)
        avg_daily_sales = total_sold / 30 if total_sold > 0 else 0
        days_left = product.quantity / avg_daily_sales if avg_daily_sales > 0 else float('inf')
        if days_left < 7:
            forecasted_out_products.append({
                'product': product,
                'days_left': int(days_left) if days_left != float('inf') else '∞',
                'avg_daily_sales': round(avg_daily_sales, 2),
            })

    return render(request, 'inventory/dashboard.html', {
        'products': products,
        'low_stock': low_stock,
        'sales': sales,
        'forecasted_out_products': forecasted_out_products,
        'notifications': notifications,
    })

def intro_page(request):
    return render(request, 'inventory/intro.html')

# Product Views
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/product_list.html'

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = '__all__'
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = '__all__'
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

# Supplier Views
class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    fields = '__all__'
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('supplier_list')

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    fields = '__all__'
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('supplier_list')

class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier_list')

class SupplierAnalyticsView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'inventory/supplier_analytics.html'
    context_object_name = 'suppliers'

    def get_queryset(self):
        return Supplier.objects.annotate(
            total_products=Count('product'),
            total_sales=Count('product__sale'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Example: Add more analytics here, e.g., average sales per supplier
        context['supplier_stats'] = [
            {
                'supplier': supplier,
                'total_products': supplier.total_products,
                'total_sales': supplier.total_sales,
            }
            for supplier in context['suppliers']
        ]
        return context

# Sale Views
class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'inventory/sale_list.html'

class SaleCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    fields = '__all__'
    template_name = 'inventory/sale_form.html'
    success_url = reverse_lazy('sale_list')

    def form_valid(self, form):
        sale = form.save(commit=False)
        product = sale.product
        if sale.quantity > product.quantity:
            form.add_error('quantity', f'Not enough stock. Only {product.quantity} left.')
            return self.form_invalid(form)
        product.quantity -= sale.quantity
        product.save()
        # Email admin on new sale
        mail_admins(
            subject=f'New Sale: {product.name}',
            message=f'A sale of {sale.quantity} units for {product.name} was recorded. Remaining stock: {product.quantity}.',
        )
        # Email admin if product is now low on stock
        if product.quantity <= product.low_stock_threshold:
            mail_admins(
                subject=f'Low Stock Alert: {product.name}',
                message=f'{product.name} is low on stock: {product.quantity} left.',
            )
        return super().form_valid(form)

class SupplierOrderListView(LoginRequiredMixin, ListView):
    model = SupplierOrder
    template_name = 'inventory/supplierorder_list.html'
    context_object_name = 'orders'
    ordering = ['-order_date']

class SupplierOrderCreateView(LoginRequiredMixin, CreateView):
    model = SupplierOrder
    fields = ['supplier', 'product', 'quantity', 'expected_delivery_date', 'notes']
    template_name = 'inventory/supplierorder_form.html'
    success_url = reverse_lazy('supplierorder_list')

class SupplierOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = SupplierOrder
    fields = ['supplier', 'product', 'quantity', 'expected_delivery_date', 'actual_delivery_date', 'notes']
    template_name = 'inventory/supplierorder_form.html'
    success_url = reverse_lazy('supplierorder_list')

def export_products_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Category', 'Supplier', 'Price', 'Quantity', 'Low Stock Threshold'])
    for product in Product.objects.all():
        writer.writerow([
            product.name,
            product.category,
            product.supplier.name if product.supplier else '',
            product.price,
            product.quantity,
            product.low_stock_threshold
        ])
    return response

def export_sales_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales.csv"'
    writer = csv.writer(response)
    writer.writerow(['Product', 'Quantity', 'Sale Date'])
    for sale in Sale.objects.all():
        writer.writerow([
            sale.product.name,
            sale.quantity,
            sale.sale_date
        ])
    return response