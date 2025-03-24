from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    """
    FilterSet for Product model, allowing filtering by various fields.
    """
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    category = filters.CharFilter(field_name="category__name", lookup_expr="iexact")
    supplier = filters.CharFilter(field_name="supplier__name", lookup_expr="iexact")
    sku = filters.CharFilter(field_name="sku", lookup_expr="exact")
    min_quantity = filters.NumberFilter(field_name="quantity", lookup_expr="gte")
    max_quantity = filters.NumberFilter(field_name="quantity", lookup_expr="lte")
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_cost_price = filters.NumberFilter(field_name="cost_price", lookup_expr="gte")
    max_cost_price = filters.NumberFilter(field_name="cost_price", lookup_expr="lte")
    description = filters.CharFilter(field_name="description", lookup_expr="icontains")
    created_at = filters.DateTimeFromToRangeFilter(field_name="created_at")

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'supplier', 'sku', 'quantity', 
            'price', 'cost_price', 'description', 'created_at'
        ]