from rest_framework import serializers
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from .models import CabAdmin,Cab,Driver,Vehicle
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
import logging

logger = logging.getLogger(__name__)
UserAccount = get_user_model()

class CabAdminCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    permissions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = CabAdmin
        fields = [
            'full_name',
            'email',
            'username',
            'password', 
            'phone_number',
            'primary_phone_number',
            'secondary_phone_number',
            'address',
            'gst_number',
            'license_number',
            'license',
            'aadhar',
            'permissions',
            'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'full_name': {'required': False},
            'phone_number': {'required': False},
            'primary_phone_number': {'required': True},
            'secondary_phone_number': {'required': False},
            'address': {'required': False},
            'gst_number': {'required': True},
            'license_number': {'required': True},
            'license': {'required': False},
            'aadhar': {'required': False},
        }

    def validate_email(self, value):
        if CabAdmin.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    
    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_username(self, value):
        if CabAdmin.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_permissions(self, value):
        if not value:
            return []
        
        # Get all available permissions for allowed apps
        valid_permissions = Permission.objects.filter(
            content_type__app_label__in=['Cabs']  # limit to your app
        )
        valid_codenames = set(valid_permissions.values_list('codename', flat=True))

        invalid = set(value) - valid_codenames
        if invalid:
            raise serializers.ValidationError(f"Invalid permissions: {invalid}")
        return value

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        password = validated_data.pop('password', None)

        if password:
            validated_data['password'] = make_password(password)

        # Create the linked UserAccount
        user = UserAccount(
            email=validated_data['email'],
            username=validated_data['username'],
        )
        user.set_password(password)
        user.save()

        # Create CabAdmin linked to that user
        cab_admin = CabAdmin.objects.create(
            user=user,
            **validated_data
        )

        if permissions:
            cab_admin.permissions.set(
                Permission.objects.filter(codename__in=permissions)
            )
        return cab_admin




#Cab status change

class CabStautsSerializer(serializers.ModelSerializer):
    id   = serializers.IntegerField(allow_null=True,required=False)

    class Meta:
        model = Cab
        fields = [
          'id','is_verified', 'is_active'
        ]
        extra_kwargs = {
            'id': {'required': True},
            'is_verified': {'required': True},
            'is_active': {'required': True},
        }


class VehicleStautsSerializer(serializers.ModelSerializer):
    id   = serializers.IntegerField(allow_null=True,required=False)

    class Meta:
        model = Vehicle
        fields = [
          'id','is_verified', 'is_active'
        ]
        extra_kwargs = {
            'id': {'required': True},
            'is_verified': {'required': True},
            'is_active': {'required': True},
        }


class DriverStautsSerializer(serializers.ModelSerializer):
    id   = serializers.IntegerField(allow_null=True,required=False)

    class Meta:
        model = Driver
        fields = [
          'id','is_verified', 'is_active'
        ]
        extra_kwargs = {
            'id': {'required': True},
            'is_verified': {'required': True},
            'is_active': {'required': True},
        }