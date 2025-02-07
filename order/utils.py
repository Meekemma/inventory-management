from .models import Order, OrderItem

def update_order_totals(order):
    """
    Recalculates the total price and total quantity for the given order.
    Deletes the order if no items remain.
    """
    if not order.orderitem_set.exists():
        order.delete()
        return {'message': 'Order deleted successfully.', 'deleted': True}

    order.total_price = order.get_product_total
    order.save(update_fields=['total_price'])

    return {
        'message': 'Order updated successfully.',
        'total_price': order.total_price,
        'product_items': order.get_product_items
    }
