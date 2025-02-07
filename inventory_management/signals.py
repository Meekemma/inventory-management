# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from inventory_management.models import Product
# from report.models import LowStockAlert



# @receiver(post_save, sender=Product)
# def check_low_stock(sender, instance, **kwargs):
#     low_stock_alert, created = LowStockAlert.objects.get_or_create(product=instance)

#     # Update the alert status based on product quantity
#     if instance.quantity <= low_stock_alert.threshold:
#         low_stock_alert.is_alerted = True
#     else:
#         low_stock_alert.is_alerted = False
#     low_stock_alert.save()
