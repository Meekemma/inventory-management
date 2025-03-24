
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import InventoryTransaction, Product
from django.db import transaction

# Store original values before update
@receiver(pre_save, sender=InventoryTransaction)
def capture_original_transaction(sender, instance, **kwargs):
    if instance.pk:  # Only for updates, not creates
        try:
            original = InventoryTransaction.objects.get(pk=instance.pk)
            instance._original_transaction_type = original.transaction_type
            instance._original_quantity = original.quantity
        except InventoryTransaction.DoesNotExist:
            instance._original_transaction_type = None
            instance._original_quantity = None
    else:
        instance._original_transaction_type = None
        instance._original_quantity = None


@receiver(post_save, sender=InventoryTransaction)
def update_product_quantity(sender, instance, created, **kwargs):
    """
    Update the associated product's quantity when an InventoryTransaction is created or updated.
    """
    product = instance.product
    transaction_type = instance.transaction_type
    quantity = instance.quantity

    with transaction.atomic():
        # Lock the product row to avoid concurrent updates
        product = Product.objects.select_for_update().get(id=product.id)

        if created:
            # New transaction: apply directly
            if transaction_type == "ADD":
                product.quantity += quantity
            elif transaction_type == "REMOVE":
                if product.quantity < quantity:
                    raise ValueError("Not enough stock to remove.")
                product.quantity -= quantity
            elif transaction_type == "ADJUST":
                product.quantity = quantity
        else:
            # Updated transaction: revert old effect, apply new effect
            original_type = getattr(instance, '_original_transaction_type', None)
            original_quantity = getattr(instance, '_original_quantity', None)

            if original_type and original_quantity is not None:
                # Revert the original effect
                if original_type == "ADD":
                    product.quantity -= original_quantity
                elif original_type == "REMOVE":
                    product.quantity += original_quantity
                elif original_type == "ADJUST":
                    # For ADJUST, the old quantity was the previous stock level,
                    # so we don't revert it directly; just apply the new one below
                    pass

            # Apply the new effect
            if transaction_type == "ADD":
                product.quantity += quantity
            elif transaction_type == "REMOVE":
                if product.quantity < quantity:
                    raise ValueError("Not enough stock to remove.")
                product.quantity -= quantity
            elif transaction_type == "ADJUST":
                product.quantity = quantity

        product.save()