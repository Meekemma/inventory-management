from django.db import models
from django.core.validators import MinValueValidator
from inventory_management.models import Product, Supplier
from django.contrib.auth import get_user_model

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    ordered_date = models.DateTimeField(auto_now_add=True)  
    is_paid = models.BooleanField(default=False) 
    received = models.BooleanField(default=False) 

    class Meta:
        ordering = ['-ordered_date'] 

    def __str__(self):
        return f"Order #{self.id} - {self.user}"  
    


    
    @property
    def get_product_total(self):
        """
        Calculate the total cost of all items in the order.
        """
        order_items = self.orderitem_set.all()  # Fetch all items related to this order
        Product_total = sum([item.get_item_total for item in order_items])  # Sum up the total cost of each item
        return Product_total

    @property
    def get_product_items(self):
        """
        Calculate the total quantity of all items in the order.
        """
        order_items = self.orderitem_set.all()
        total_quantity = sum([item.quantity for item in order_items])  # Sum up the quantities of each item
        return total_quantity




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE) 
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)]) 
    date_added = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.quantity} of {self.product.name if self.product else 'Unknown Product'} in Order for {self.order.user}"  

    @property
    def get_item_total(self):
        """
        Calculate the total cost of this specific item.
        """
        if self.product.price is not None and self.quantity is not None:
            return self.product.price * self.quantity
        return 0