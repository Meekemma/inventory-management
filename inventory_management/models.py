from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)  # Indexing for fast lookups
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)  # Frequently queried
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]  # Explicit indexing

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name="products", db_index=True)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True, db_index=True)  # Indexed for lookups
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products", db_index=True) 
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['name', 'category'])]  # Indexing for better filtering

    def __str__(self):
        return self.name


class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('ADD', 'Stock Added'),
        ('REMOVE', 'Stock Removed'),
        ('ADJUST', 'Stock Adjusted'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="transactions", db_index=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, db_index=True)  # Indexed for fast filtering
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['created_at'])]  # Optimize time-based queries

    def __str__(self):
        return f"{self.transaction_type} - {self.product.name} ({self.quantity})"
