from django.core.management.base import BaseCommand
from inventory.models import Supplier, Product

class Command(BaseCommand):
    help = 'Populate the database with 5 suppliers and 5 products.'

    def handle(self, *args, **kwargs):
        suppliers_data = [
            {'name': 'Acme Corp', 'contact': 'acme@example.com'},
            {'name': 'Global Supplies', 'contact': 'global@example.com'},
            {'name': 'TechSource', 'contact': 'techsource@example.com'},
            {'name': 'OfficeMart', 'contact': 'officemart@example.com'},
            {'name': 'EcoGoods', 'contact': 'ecogoods@example.com'},
        ]
        products_data = [
            {'name': 'Printer Paper', 'category': 'Office Supplies', 'price': 5.99, 'quantity': 100, 'low_stock_threshold': 10},
            {'name': 'Laptop', 'category': 'Electronics', 'price': 899.99, 'quantity': 20, 'low_stock_threshold': 2},
            {'name': 'Desk Chair', 'category': 'Furniture', 'price': 129.99, 'quantity': 15, 'low_stock_threshold': 3},
            {'name': 'Whiteboard', 'category': 'Office Supplies', 'price': 49.99, 'quantity': 25, 'low_stock_threshold': 5},
            {'name': 'LED Monitor', 'category': 'Electronics', 'price': 199.99, 'quantity': 30, 'low_stock_threshold': 4},
        ]

        # Create suppliers
        suppliers = []
        for data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(name=data['name'], defaults={'contact': data['contact']})
            suppliers.append(supplier)
        self.stdout.write(self.style.SUCCESS('Suppliers added.'))

        # Create products, each linked to a supplier
        for i, data in enumerate(products_data):
            supplier = suppliers[i % len(suppliers)]
            product, created = Product.objects.get_or_create(
                name=data['name'],
                defaults={
                    'category': data['category'],
                    'supplier': supplier,
                    'price': data['price'],
                    'quantity': data['quantity'],
                    'low_stock_threshold': data['low_stock_threshold'],
                }
            )
        self.stdout.write(self.style.SUCCESS('Products added.')) 