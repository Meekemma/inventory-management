from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

User = get_user_model()  # Correct variable naming convention


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}



    def validate_email(self, value):
        value = value.lower()  # Normalize email
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Password and Confirm Password do not match.")
        
        validate_password(attrs['password'])  # Django's built-in password validation
        return attrs
    
    
    def create(self, validated_data):
        validated_data.pop('password2')  # Remove confirm password
        validated_data['email'] = validated_data['email'].lower()  # Normalize email
        return User.objects.create_user(**validated_data)  # Uses Django’s built-in method



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email').lower()  # Normalize email
        password = attrs.get('password')

        user = authenticate(email=email, password=password)  # Authenticate user

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")

        attrs['user'] = user  # Store user object in validated data
        return attrs





class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True, max_length=50, required=True, style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True, max_length=50, required=True, style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True, max_length=50, required=True, style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        """Validate that the old password is correct."""

        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    

    def validate(self, attrs):
        """Validate new password match and apply Django's password validation."""

        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        
        validate_password(attrs['new_password'])  # Django's password validation
        return attrs
    
    
    def save(self, **kwargs): 
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile  
        fields = ['user', 'first_name', 'last_name', 'email','profile_pic', 'gender','phone_number', 'country','state', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'email', 'user']


    def update(self, instance, validated_data):
        """
        Custom update method to properly handle profile image updates.
        """

        profile_pic = validated_data.get('profile_pic', None)


        # Update fields only if they are provided
        for attr,value in validated_data.items():
            setattr(instance, attr, value)


        # If a new profile picture is uploaded, update it
        if profile_pic:
            instance.profile_pic = profile_pic

        instance.save()
        return instance