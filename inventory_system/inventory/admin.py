from django.contrib import admin
from .models import Supplier, Product, Sale, SupplierOrder
# Register your models here.
admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(SupplierOrder)