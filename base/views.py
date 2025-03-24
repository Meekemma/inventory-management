from django.shortcuts import render, redirect  
from rest_framework.decorators import api_view  
from rest_framework.response import Response  
from rest_framework import status 
from rest_framework.decorators import api_view,permission_classes,throttle_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from .serializers import RegistrationSerializer, LoginSerializer, ChangePasswordSerializer,ProfileSerializer
from base.throttles import RegisterThrottle, LoginThrottle, LogoutThrottle, ChangePasswordThrottle, UpdateProfileThrottle


# JWT authentication imports
from rest_framework_simplejwt.tokens import RefreshToken  
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model  

User = get_user_model()  
from .models import *  


@api_view(['POST'])
@throttle_classes([RegisterThrottle])
def registration_view(request):
    """Handles user registration"""

    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@throttle_classes([LoginThrottle])
def login_view(request):
    """Handles user login and returns JWT tokens"""

    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)  # Generate JWT tokens
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                "user_id": user.id,  
                "full_name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "is_verified": user.is_verified,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






@api_view(['POST'])
@throttle_classes([LogoutThrottle])
def logout_view(request):
    """
    Logs out a user by blacklisting their refresh token.
    This prevents the token from being reused to generate a new access token.
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Create a RefreshToken instance from the provided token
        token = RefreshToken(refresh_token)

        # Blacklist the token to prevent reuse
        token.blacklist()  
        
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    
    except TokenError:
        # Handle cases where the token is invalid or expired
        return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)





@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@throttle_classes([ChangePasswordThrottle])
def change_password_view(request):
    """Handles user password change"""

    if request.method == 'PUT':
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




@api_view(['PATCH'])
@permission_classes([IsAuthenticated])  
@throttle_classes([UpdateProfileThrottle])
def update_profile(request):
    """
    Updates the authenticated user's profile.
    Handles both text and file uploads.
    """
    user_profile = request.user.userprofile  # Get the user's profile

    serializer = ProfileSerializer(user_profile, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)