from django.shortcuts import render,redirect
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RegistrationSerializer
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.utils.timezone import now


User = get_user_model()
from .models import *






@csrf_exempt
@api_view(['POST'])
def registration_view(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()  
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    
    return Response({"error": "Failed to register user", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)







# Custom serializer for obtaining JWT token with additional claims
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_id'] = user.id
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        token['is_verified'] = user.is_verified
    
        return token
    

    
# validate method is overridden to add extra responses to the data returned by the parent class's validate method.
    def validate(self, attrs):
        # Normalize the email to lowercase before validation
        attrs['email'] = attrs['email'].lower()
        # call validates the provided attributes using the parent class's validate method and returns the validated data.
        data = super().validate(attrs)

        
        # Adds the user id to the response
        data.update({'user_id': self.user.id})
        full_name = f"{self.user.first_name} {self.user.last_name}"
        data.update({'full_name': full_name})
        data.update({'email': self.user.email})
        data.update({'is_verified': self.user.is_verified})

        return data

       
    

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class =MyTokenObtainPairSerializer 





@api_view(['POST'])
def logout_view(request):
    refresh_token = request.data.get('refresh') 
    if not refresh_token:
        return Response({"detail": "Refresh token is required."}, status=400)

    try:
        # Decode the refresh token
        token = RefreshToken(refresh_token)

        # Fetch the corresponding OutstandingToken instance
        outstanding_token = OutstandingToken.objects.get(jti=token['jti'])

        # Blacklist the token by creating a BlacklistedToken entry
        BlacklistedToken.objects.create(token=outstanding_token, blacklisted_at=now())

        return Response({"detail": "Successfully logged out."}, status=200)
    except OutstandingToken.DoesNotExist:
        return Response({"detail": "Token does not exist or is already blacklisted."}, status=404)
    except InvalidToken:
        return Response({"detail": "Invalid token."}, status=401)

