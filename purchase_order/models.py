from django.db import models
from django.core.validators import MinValueValidator
from inventory_management.models import Product, Supplier
from django.contrib.auth import get_user_model

User = get_user_model()

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name="purchase_orders")  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Updated via signal
    ordered_date = models.DateTimeField(auto_now_add=True)  
    expected_delivery_date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False) 
    received = models.BooleanField(default=False) 
    received_date = models.DateTimeField(null=True, blank=True)
    po_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['-ordered_date'] 

    def __str__(self):
        return f"PO #{self.po_number or self.id} - Supplier: {self.supplier} - User: {self.user}"  

    @property
    def get_product_total(self):
        order_items = self.purchaseorderitem_set.all() 
        return sum(item.get_item_total for item in order_items)

    @property
    def get_product_items(self):
        order_items = self.purchaseorderitem_set.all() 
        return sum(item.quantity for item in order_items)


class PurchaseOrderItem(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)]) 
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Set to product.cost_price on creation, adjustable for bulk
    date_added = models.DateTimeField(auto_now_add=True) 
    received_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.quantity} of {self.product.name if self.product else 'Unknown Product'} in Order for {self.order.user}"  

    @property
    def get_item_total(self):
        return self.unit_price * self.quantity