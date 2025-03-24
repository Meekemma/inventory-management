from rest_framework import serializers
from .models import Order, OrderItem,Supplier
from inventory_management.models import Product
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()



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
        """Create a new order with items, updating stock atomically."""
        user = self.context['request'].user
        order_items_data = validated_data.pop('orderitem_set', [])

        with transaction.atomic():
            # Create order (user is nullable, so allow None if intentional)
            order = Order.objects.create(
                user=user if user.is_authenticated else None,
                status='pending',
                is_paid=False,
                total_price=0.00  # Initial value, updated later
            )

            # Process order items
            for item_data in order_items_data:
                product = item_data['product']
                quantity = item_data['quantity']

                # Update stock
                if product.quantity < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {product.name}. Available: {product.quantity}"
                    )
                product.quantity -= quantity
                product.save()

                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity
                )

            # Update total price
            order.total_price = order.get_product_total
            order.save(update_fields=['total_price'])

        return order

    def update(self, instance, validated_data):
        """Update an existing order, handling status changes and item updates."""
        order_items_data = validated_data.pop('orderitem_set', None)

        with transaction.atomic():
            # Update status or is_paid if provided
            instance.status = validated_data.get('status', instance.status)
            instance.is_paid = validated_data.get('is_paid', instance.is_paid)

            if order_items_data:
                # Revert stock for existing items
                for item in instance.orderitem_set.all():
                    item.product.quantity += item.quantity
                    item.product.save()
                instance.orderitem_set.all().delete()  # Clear existing items

                # Add new items and update stock
                for item_data in order_items_data:
                    product = item_data['product']
                    quantity = item_data['quantity']
                    if product.quantity < quantity:
                        raise serializers.ValidationError(
                            f"Insufficient stock for {product.name}. Available: {product.quantity}"
                        )
                    product.quantity -= quantity
                    product.save()

                    OrderItem.objects.create(
                        order=instance,
                        product=product,
                        quantity=quantity
                    )

            # Update total price
            instance.total_price = instance.get_product_total
            instance.save(update_fields=['total_price'])

        return instance