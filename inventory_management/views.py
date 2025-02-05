from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsUser
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Category,Product,InventoryTransaction,Supplier
from .serializers import CategorySerializer,ProductSerializer,InventoryTransactionSerializer,SupplierSerializer


# Create a new category
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_category(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Get all categories
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)  


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        category.delete()
        return Response({"detail": "Category deleted"}, status=status.HTTP_204_NO_CONTENT)
    

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def suppliers(request):
    if request.method == 'GET':
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'GET':
        serializer = SupplierSerializer(supplier)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = SupplierSerializer(supplier, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        supplier.delete()
        return Response({"detail": "Supplier deleted"}, status=status.HTTP_204_NO_CONTENT)





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def products(request):
    products = Product.objects.select_related("category")
    paginator = LimitOffsetPagination()
    paginated_products = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(paginated_products, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_products(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



@api_view(['GET',  'PUT', 'DELETE'])  
@permission_classes([IsAuthenticated])
def update_products(request, pk):
    product = get_object_or_404(Product.objects.select_related("category"), pk=pk) 

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):  
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


    elif request.method == 'DELETE':
        product.delete()
        return Response({"detail": "Product deleted"}, status=status.HTTP_204_NO_CONTENT)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_transaction(request):
    """
    Handles inventory transactions: ADD, REMOVE, ADJUST
    """
    serializer = InventoryTransactionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transaction_history(request):
    """
    Get all inventory transactions.
    """
    transactions = InventoryTransaction.objects.select_related("product").order_by("-created_at")
    serializer = InventoryTransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

