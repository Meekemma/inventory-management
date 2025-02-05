from rest_framework import serializers
from .models import LowStockAlert
from inventory_management.models import Product



class LowStockAlertSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(
        queryset=Product.objects.all(), slug_field="name"
    )

    class Meta:
        model = LowStockAlert
        fields = ["product", "threshold", "is_alerted"]