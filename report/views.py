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
from .utils import get_sales_data


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



@api_view(['GET'])
def sales_report(request):
    
    
    period = request.query_params.get('period', None)
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)

    try:
        # Call the helper function to get sales data
        data = get_sales_data(period=period, start_date=start_date, end_date=end_date)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Handle empty data scenario
    if not data:
        return Response(
            {"message": "No sales data available for the specified period or range."},
            status=status.HTTP_200_OK,
        )

    return Response(data, status=status.HTTP_200_OK)