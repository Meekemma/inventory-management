from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PurchaseOrderItem

@receiver(post_save, sender=PurchaseOrderItem)
def update_total_price_on_save(sender, instance, **kwargs):
    order = instance.order
    order.total_price = sum(item.get_item_total for item in order.purchaseorderitem_set.all())
    order.save()

@receiver(post_delete, sender=PurchaseOrderItem)
def update_total_price_on_delete(sender, instance, **kwargs):
    order = instance.order
    order.total_price = sum(item.get_item_total for item in order.purchaseorderitem_set.all())
    order.save()