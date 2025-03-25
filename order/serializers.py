import logging
from rest_framework import serializers
from .models import Order, OrderItem,Supplier
from inventory_management.models import Product
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()
logger = logging.getLogger(__name__)



from rest_framework import serializers
from .models import OrderItem
from inventory_management.models import Product



class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_description = serializers.CharField(source='product.description', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True, default=0.00)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_description', 'product_price', 'quantity', 'date_added')
        read_only_fields = ('id', 'date_added')

    def validate(self, data):
        """Validate quantity against product stock."""
        product = data.get('product')
        quantity = data.get('quantity')
        if product and quantity:
            if product.quantity < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. Available: {product.quantity}"
                )
        return data




class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, source='orderitem_set')
    total_price = serializers.SerializerMethodField()
    product_items = serializers.SerializerMethodField()


    class Meta:
        model = Order
        fields = ('id', 'user', 'total_price', 'ordered_date', 'status', 'is_paid', 'order_items', 'product_items')
        read_only_fields = ('id', 'user', 'total_price', 'ordered_date')

    def get_total_price(self, obj):
        return obj.get_product_total

    def get_product_items(self, obj):
        return obj.get_product_items

    def create(self, validated_data):
        """Create or update the user's single unsettled order."""
        user = self.context['request'].user
        order_items_data = validated_data.pop('orderitem_set', [])

        with transaction.atomic():
            # Get or create the user's single pending, unpaid order
            order, created = Order.objects.get_or_create(
                user=user, 
                status='pending',
                is_paid=False,
                defaults={'total_price': 0.00}
            )

            # Process order items
            for item_data in order_items_data:
                product = item_data['product']
                quantity = item_data['quantity']

                # Create or update order item (add quantity if it exists)
                order_item, item_created = OrderItem.objects.get_or_create(
                    order=order,
                    product=product,
                    defaults={'quantity': quantity}
                )
                if not item_created:
                    order_item.quantity += quantity  # Increment quantity
                    order_item.save()

            # Update total price
            order.total_price = order.get_product_total
            order.save(update_fields=['total_price'])

        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('orderitem_set', None)

        try:
            with transaction.atomic():
                # Update status or is_paid if provided
                instance.status = validated_data.get('status', instance.status)
                instance.is_paid = validated_data.get('is_paid', instance.is_paid)

                if order_items_data and instance.status == 'pending' and not instance.is_paid:
                    for item_data in order_items_data:
                        product = item_data['product']
                        quantity = item_data['quantity']
                        order_item, created = OrderItem.objects.get_or_create(
                            order=instance,
                            product=product,
                            defaults={'quantity': quantity}
                        )
                        if not created:
                            order_item.quantity += quantity
                            order_item.save()

                # Save the instance explicitly
                instance.total_price = instance.get_product_total
                instance.save(update_fields=['total_price', 'status', 'is_paid'])
                logger.info(f"Order {instance.id} updated: status={instance.status}, is_paid={instance.is_paid}")

        except ValueError as e:
            # Catch stock-related errors from the signal
            logger.error(f"Failed to update order {instance.id}: {str(e)}")
            raise serializers.ValidationError(str(e))

        return instance