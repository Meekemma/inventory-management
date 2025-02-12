from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import PurchaseOrderSerializer
from .models import PurchaseOrder, PurchaseOrderItem





# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_purchase_order(request):
    serializer = PurchaseOrderSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({'message': 'Order created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response({'message': 'Order creation failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def track_order_status(request):
    order_status = request.query_params.get('status', None)
    is_paid = request.query_params.get('is_paid', None)
    received = request.query_params.get('received', None)

    if order_status is None or is_paid is None or received is None:
        return Response({"error": "All query parameters ('status', 'is_paid', 'received') are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        is_paid = is_paid.lower() == 'true' if is_paid else None
        received = received.lower() == 'true' if received else None

        # Filter only if the params exist
        filters = {"status": order_status}
        if is_paid is not None:
            filters["is_paid"] = is_paid
        if received is not None:
            filters["received"] = received

        orders = PurchaseOrder.objects.filter(**filters)
        serializer = PurchaseOrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def order_status_update(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)

    allowed_fields = {'status', 'is_paid', 'received'}
    update_data = {key: request.data[key] for key in request.data if key in allowed_fields}

    if update_data:
        for key, value in update_data.items():
            setattr(order, key, value)
        order.save()

    return Response({"message": "Order updated successfully", "data": PurchaseOrderSerializer(order).data}, status=status.HTTP_200_OK)
