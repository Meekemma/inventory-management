from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .serializers import OrderSerializer
from .models import Order, OrderItem
from .utils import update_order_totals




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create a new order with items."""
    serializer = OrderSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        order = serializer.save()
        return Response(
            {'message': 'Order created successfully', 'data': serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(
        {'message': 'Order creation failed', 'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
    """Retrieve all orders for the authenticated user."""
    orders = Order.objects.filter(user=request.user).prefetch_related('orderitem_set__product')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)





@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """Retrieve, update, or delete a specific order."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = OrderSerializer(order, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Order updated successfully', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {'message': 'Order update failed', 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == 'DELETE':
        with transaction.atomic():
            # Revert stock for all items
            for item in order.orderitem_set.all():
                item.product.quantity += item.quantity
                item.product.save()
            order.delete()
        return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)






@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_item(request, order_item_id):
    """Update the quantity of an order item, adjusting stock and order totals."""
    try:
        order_item = OrderItem.objects.get(id=order_item_id, order__user=request.user)
        new_quantity = request.data.get('quantity')

        try:
            new_quantity = int(new_quantity)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid quantity format'}, status=status.HTTP_400_BAD_REQUEST)

        if new_quantity < 0:
            return Response({'error': 'Quantity cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)

        order = order_item.order
        if order.status != 'pending':
            return Response({'error': 'Can only update items in pending orders'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Calculate stock adjustment
            old_quantity = order_item.quantity
            quantity_diff = new_quantity - old_quantity

            if quantity_diff > 0:  # Increasing quantity
                if order_item.product.quantity < quantity_diff:
                    return Response(
                        {'error': f"Insufficient stock for {order_item.product.name}. Available: {order_item.product.quantity}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                order_item.product.quantity -= quantity_diff
            elif quantity_diff < 0:  # Decreasing quantity
                order_item.product.quantity -= quantity_diff  # Adds back the difference (negative diff)

            # Update or delete the order item
            if new_quantity == 0:
                order_item.delete()
                response_data = update_order_totals(order)
                if response_data.get('deleted'):
                    return Response(response_data, status=status.HTTP_200_OK)
                return Response({
                    'message': 'Order item removed successfully',
                    'updated_order': response_data
                }, status=status.HTTP_200_OK)
            else:
                order_item.quantity = new_quantity
                order_item.save()

            order_item.product.save()
            response_data = update_order_totals(order)

            return Response({
                'message': 'Order item updated successfully',
                'order_item': {
                    'id': order_item.id,
                    'quantity': order_item.quantity,
                    'item_total': order_item.get_item_total
                },
                'updated_order': response_data
            }, status=status.HTTP_200_OK)

    except OrderItem.DoesNotExist:
        return Response({'error': 'Order item not found'}, status=status.HTTP_404_NOT_FOUND)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def track_status(request):
    """
    Filter orders based on their status, is_paid field, and received.
    """
    order_status = request.query_params.get('status', None)
    is_paid = request.query_params.get('is_paid', None)

    # Check if all required query parameters are provided
    if order_status is None or is_paid is None:
        return Response( {"error": "All query parameters ('status', 'is_paid', 'received') are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Convert is_paid and received to boolean
        is_paid = is_paid.lower() == 'true'

        # Filter orders
        orders = Order.objects.filter(status=order_status, is_paid=is_paid)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # Catch unexpected errors and return an internal server error
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



    
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def status_update(request, order_id):
    """
    Admin users can update the status and payment status of an order.
    """
    # Fetch the order instance
    order = get_object_or_404(Order, id=order_id)

    # Define allowed fields for update
    allowed_fields = {'status', 'is_paid'}
    update_data = {key: request.data[key] for key in request.data if key in allowed_fields}

    # Update the order with the provided data
    serializer = OrderSerializer(order, data=update_data, partial=True)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # If the data is invalid, this will be raised automatically by `raise_exception=True`
    return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)