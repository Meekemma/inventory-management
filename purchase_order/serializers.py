from rest_framework import serializers
from .models import PurchaseOrder, PurchaseOrderItem
from inventory_management.models import Product, Supplier
from django.contrib.auth import get_user_model

User = get_user_model()



class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_description = serializers.CharField(source='product.description', read_only=True)
    product_cost_price = serializers.DecimalField(source='product.cost_price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = ('id', 'product', 'product_name', 'product_description', 'product_cost_price', 'quantity', 'date_added')
        read_only_fields = ('id', 'date_added')





class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier = serializers.SlugRelatedField(queryset=Supplier.objects.all(), slug_field='name')  
    purchase_order_items = PurchaseOrderItemSerializer(many=True, source='purchaseorderitem_set')
    total_price = serializers.SerializerMethodField()
    product_items = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = ('id', 'user', 'supplier', 'total_price', 'ordered_date', 'status', 'is_paid', 'received', 'purchase_order_items', 'product_items')
        read_only_fields = ('id', 'user', 'total_price', 'ordered_date')

    def get_total_price(self, obj):
        return obj.get_product_total

    def get_product_items(self, obj):
        return obj.get_product_items

    def create(self, validated_data):
        user = self.context['request'].user
        supplier = validated_data.pop('supplier')  # Get supplier from request
        purchase_order_items_data = validated_data.pop('purchaseorderitem_set', [])

        # Create a new order or retrieve an existing one
        order, created = PurchaseOrder.objects.get_or_create(
            user=user,
            supplier=supplier,  # Assign supplier
            status='pending',
            is_paid=False,
            received=False,
        )

        if created:
            order.save()

        # Handle order items
        for item_data in purchase_order_items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            purchase_order_item, item_created = PurchaseOrderItem.objects.get_or_create(
                order=order,
                product=product,
                defaults={'quantity': quantity}
            )

            if not item_created:
                purchase_order_item.quantity += quantity
                purchase_order_item.save()

        # Update the total price of the order
        order.total_price = order.get_product_total
        order.save(update_fields=['total_price'])

        return order
