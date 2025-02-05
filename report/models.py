from django.db import models
from inventory_management.models import Product

# Create your models here.

class LowStockAlert(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    threshold = models.PositiveIntegerField(default=5)
    is_alerted = models.BooleanField(default=False)

    def __str__(self):
        return f"Low stock alert for {self.product.name}"