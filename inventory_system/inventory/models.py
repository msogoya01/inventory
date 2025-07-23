from django.db import models

# Create your models here.
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    low_stock_threshold = models.IntegerField(default=5)

    def __str__(self):
        return self.name

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sale_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} on {self.sale_date.strftime('%Y-%m-%d')}"

class SupplierOrder(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_date = models.DateField(auto_now_add=True)
    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def get_status(self):
        from django.utils import timezone
        today = timezone.now().date()
        if self.actual_delivery_date:
            return 'Delivered'
        elif today > self.expected_delivery_date:
            return 'Delayed'
        else:
            return 'Pending'

    def __str__(self):
        return f"Order of {self.quantity} {self.product.name} from {self.supplier.name} ({self.get_status()})"