from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import PurchaseOrderSerializer, PurchaseOrderItemSerializer
from .models import PurchaseOrder, PurchaseOrderItem


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_purchase_order(request):
    serializer = PurchaseOrderSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'message': 'Order created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def track_order_status(request):
    filters = {}
    if 'status' in request.query_params:
        filters['status'] = request.query_params['status']
    if 'is_paid' in request.query_params:
        filters['is_paid'] = request.query_params['is_paid'].lower() == 'true'
    if 'received' in request.query_params:
        filters['received'] = request.query_params['received'].lower() == 'true'

    try:
        orders = PurchaseOrder.objects.filter(**filters)
        serializer = PurchaseOrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def order_status_update(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    serializer = PurchaseOrderSerializer(order, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"message": "Order updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_purchase_order(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    serializer = PurchaseOrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_purchase_order_item(request, order_id, item_id=None):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    
    if request.method == 'POST':
        # Add a new item
        serializer = PurchaseOrderItemSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(order=order, unit_price=serializer.validated_data['product'].cost_price)
        return Response({'message': 'Item added successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    
    elif request.method == 'PUT':
        # Update an existing item
        item = get_object_or_404(PurchaseOrderItem, id=item_id, order=order)
        serializer = PurchaseOrderItemSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Item updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        # Delete an existing item
        item = get_object_or_404(PurchaseOrderItem, id=item_id, order=order)
        item.delete()
        return Response({'message': 'Item deleted successfully'}, status=status.HTTP_204_NO_CONTENT)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_purchase_order(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    order.delete()
    return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)