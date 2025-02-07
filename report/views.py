from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status
from django.shortcuts import get_object_or_404
from inventory_management.models import Product
from inventory_management.serializers import ProductSerializer
from .serializers import LowStockAlertSerializer
from .models import LowStockAlert


# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def low_stock_alerts(request):
    """Get all products with active low stock alerts"""
    alerts = LowStockAlert.objects.filter(is_alerted=True)
    products = [alert.product for alert in alerts]  
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def low_stock_products(request):
    """Fetch products below a threshold using query params."""
    threshold = request.query_params.get('threshold', 5)

    try:
        threshold = int(threshold)  # Ensure threshold is an integer
    except ValueError:
        return Response({"error": "Threshold must be a valid integer."}, status=status.HTTP_400_BAD_REQUEST)

    low_stock_products = Product.objects.filter(quantity__lte=threshold).order_by('quantity') 

    if not low_stock_products.exists():
        return Response(
            {"message": f"No products found with quantity less than or equal to {threshold}."},
            status=status.HTTP_200_OK
        )

    # Serialize and return the data
    serializer = ProductSerializer(low_stock_products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
