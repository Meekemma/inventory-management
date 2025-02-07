from django.db.models.signals import post_save
from django.dispatch import receiver
from inventory_management.models import Product
from .models import LowStockAlert

@receiver(post_save, sender=Product)
def manage_low_stock_alert(sender, instance, **kwargs):
    """Create or remove low stock alerts based on product quantity."""
    alert_exists = LowStockAlert.objects.filter(product=instance).exists()

    if instance.quantity <= 5:  # Use instance.quantity instead of alert.threshold
        if not alert_exists:
            LowStockAlert.objects.create(product=instance, is_alerted=True)
    else:
        LowStockAlert.objects.filter(product=instance).delete() 
