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
    get_item_total = serializers.ReadOnlyField()

    class Meta:
        model = PurchaseOrderItem
        fields = ('id', 'product', 'product_name', 'product_description', 
                  'product_cost_price', 'quantity', 'unit_price', 'received_quantity', 
                  'get_item_total', 'date_added')
        read_only_fields = ('id', 'date_added')

class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier = serializers.SlugRelatedField(queryset=Supplier.objects.all(), slug_field='name')  
    purchase_order_items = PurchaseOrderItemSerializer(many=True, source='purchaseorderitem_set')
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    product_items = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = ('id', 'user', 'supplier', 'total_price', 'ordered_date', 'status', 
                  'is_paid', 'received', 'expected_delivery_date', 'received_date', 
                  'po_number', 'purchase_order_items', 'product_items')
        read_only_fields = ('id', 'user', 'total_price', 'ordered_date', 'received_date')

    def get_product_items(self, obj):
        return obj.get_product_items

    def create(self, validated_data):
        user = self.context['request'].user
        supplier = validated_data.pop('supplier')
        purchase_order_items_data = validated_data.pop('purchaseorderitem_set', [])

        # Use get_or_create with defaults for new POs
        order, created = PurchaseOrder.objects.get_or_create(
            user=user,
            supplier=supplier,
            status='pending',
            defaults={
                'is_paid': False,
                'received': False,
                'total_price': 0.00,  # Signal will update this
                **validated_data  # Include any extra fields like expected_delivery_date
            }
        )

        # Handle order items
        for item_data in purchase_order_items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            purchase_order_item, item_created = PurchaseOrderItem.objects.get_or_create(
                order=order,
                product=product,
                defaults={
                    'quantity': quantity,
                    'unit_price': product.cost_price  # Default to cost_price
                }
            )
            if not item_created:
                purchase_order_item.quantity += quantity
                purchase_order_item.save()

        return order