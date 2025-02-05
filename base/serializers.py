from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password do not match.")
        
        # Validate the password using Django's built-in validators
        validate_password(password)

        return attrs
    


    def validate_email(self, value):
        # Normalize the email before checking if it exists
        normalized_email = value.lower()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized_email

    def create(self, validated_data):
        # Ensure the email is stored in lowercase
        validated_data['email'] = validated_data['email'].lower()
        # Remove password2 from validated data
        validated_data.pop('password2')  
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        # Hash the password
        user.set_password(password) 
        user.save()
        return user

        