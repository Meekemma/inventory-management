from rest_framework import serializers
from .models import Order, OrderItem,Supplier
from inventory_management.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()



class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_description = serializers.CharField(source='product.description', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)


    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_description', 'product_price', 'quantity', 'date_added')
        read_only_fields = ('id', 'date_added')






class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, source='orderitem_set')
    total_price = serializers.SerializerMethodField()
    product_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'user', 'total_price', 'ordered_date', 'status', 'is_paid','order_items', 'product_items')
        read_only_fields = ('id', 'user', 'total_price', 'ordered_date')

    def get_total_price(self, obj):
        return obj.get_product_total

    def get_product_items(self, obj):
        return obj.get_product_items

    def create(self, validated_data):
        user = self.context['request'].user
        order_items_data = validated_data.pop('orderitem_set', [])

        # Create a new order or retrieve an existing one
        order, created = Order.objects.get_or_create(
            user=user,
            status='pending',
            is_paid=False,
        )

        # Ensure the order is saved and has a primary key
        if created:
            order.save()

        # Handle order items
        for item_data in order_items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            # Create or update the OrderItem
            order_item, item_created = OrderItem.objects.get_or_create(
                order=order,
                product=product,
                defaults={'quantity': quantity}  # Set the quantity if the item is created
            )

            # Update quantity for existing items
            if not item_created:
                order_item.quantity += quantity
                order_item.save()

        # Update the total price of the order after adding all items
        order.total_price = order.get_product_total
        order.save(update_fields=['total_price'])

        return order