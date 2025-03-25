import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order, OrderItem
from django.db import transaction

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def deduct_stock_on_completion(sender, instance, created, **kwargs):
    """Deduct stock when an order's status changes to 'completed'."""
    if not created and instance.status == 'completed' and kwargs.get('update_fields') != {'total_price'}:
        with transaction.atomic():
            for item in instance.orderitem_set.all():
                product = item.product
                if product.quantity < item.quantity:
                    logger.error(f"Insufficient stock for {product.name}. Available: {product.quantity}, Required: {item.quantity}")
                    raise ValueError(f"Insufficient stock for {product.name}. Available: {product.quantity}")
                product.quantity -= item.quantity
                product.save()
                logger.info(f"Deducted {item.quantity} from {product.name}. New stock: {product.quantity}")



@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total_price(sender, instance, **kwargs):
    order = instance.order
    order.total_price = order.get_product_total
    order.save(update_fields=['total_price'])

