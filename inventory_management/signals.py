from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, InventoryTransaction, LowStockAlert

@receiver(post_save, sender=Product)
def create_low_stock_alert(sender, instance, created, **kwargs):
    if created:
        LowStockAlert.objects.create(product=instance)  