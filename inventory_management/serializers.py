from rest_framework import serializers
from django.db import transaction
from .models import Category,Product, InventoryTransaction,Supplier

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):  
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
    




class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_name', 'phone', 'email', 'address', 'created_at']
        read_only_fields = ['created_at']


    def create(self, validated_data):
        return Supplier.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.contact_name = validated_data.get('contact_name', instance.contact_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance




class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(queryset=Category.objects.all(), slug_field='name')
    supplier = serializers.SlugRelatedField(queryset=Supplier.objects.all(), slug_field='name')
    profit_margin = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category', 'supplier', 'quantity', 
            'price', 'cost_price', 'description', 'created_at', 'profit_margin'
        ]
        read_only_fields = ['created_at']

    def validate_quantity(self, value):
        """Ensure the quantity is non-negative."""
        if value < 0:
            raise serializers.ValidationError('The quantity cannot be less than 0.')
        return value

    def validate_price(self, value):
        """Ensure the price is non-negative if provided."""
        if value is not None and value < 0.0:
            raise serializers.ValidationError('The price cannot be less than 0.0.')
        return value
    
    def validate_cost_price(self, value):
        """Ensure the cost price is non-negative if provided."""
        if value is not None and value < 0.0:
            raise serializers.ValidationError('The cost price cannot be less than 0.0.')
        return value

    def create(self, validated_data):
        """Create a new product."""
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing product."""
        instance.name = validated_data.get('name', instance.name)
        instance.sku = validated_data.get('sku', instance.sku)
        instance.description = validated_data.get('description', instance.description)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.price = validated_data.get('price', instance.price)
        instance.cost_price = validated_data.get('cost_price', instance.cost_price)
        instance.category = validated_data.get('category', instance.category)
        instance.supplier = validated_data.get('supplier', instance.supplier)  # Added supplier update
        instance.save()
        return instance

    def get_profit_margin(self, obj):
        """Calculate the profit margin if price and cost_price are available."""
        if obj.price is not None and obj.cost_price is not None:
            return obj.price - obj.cost_price
        return None






class InventoryTransactionSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(
        queryset=Product.objects.all(), slug_field="name"
    )

    class Meta:
        model = InventoryTransaction
        fields = ["id", "product", "transaction_type", "quantity", "created_at"]
        read_only_fields = ["created_at"]

    def validate_quantity(self, value):
        if value <= 0 and self.initial_data.get("transaction_type") != "ADJUST":
            raise serializers.ValidationError("Quantity must be greater than zero for ADD/REMOVE.")
        return value

    def create(self, validated_data):
        """
        Create a transaction and update the product quantity accordingly.
        """
        with transaction.atomic():
            product = validated_data["product"]
            transaction_type = validated_data["transaction_type"]
            quantity = validated_data["quantity"]

            if transaction_type == "ADD":
                product.quantity += quantity  # Increase stock
            elif transaction_type == "REMOVE":
                if product.quantity < quantity:
                    raise serializers.ValidationError("Not enough stock to remove.")
                product.quantity -= quantity  # Decrease stock
            elif transaction_type == "ADJUST":
                product.quantity = quantity  # Set new stock level
            
            product.save()
            return super().create(validated_data)






