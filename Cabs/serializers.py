from rest_framework.permissions import AllowAny  # Uncomment to allow any user
from rest_framework import serializers
from .models import Cab, Vehicle, Driver, CabCategory # DriverImage

# CabAdmin serializer with permission logic
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from .models import CabAdmin
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from datetime import date  # Add this import

import logging

logger = logging.getLogger(__name__)
UserAccount = get_user_model()

class CabAdminCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    # For write: accept list of codenames; for read: show list of codenames
    permissions = serializers.SerializerMethodField(read_only=True)

    def get_permissions(self, obj):
        return list(obj.permissions.values_list('codename', flat=True))

    permissions_write = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = CabAdmin
        fields = [
            'id',
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
            'permissions_write',
            'status',
        ]
        read_only_fields = ['status', 'permissions']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'permissions_write': {'write_only': True, 'required': False},
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

    def validate_permissions_write(self, value):
        if not value:
            return []
        # Accept permissions from all allowed apps
        valid_permissions = Permission.objects.all()
        valid_codenames = set(valid_permissions.values_list('codename', flat=True))
        invalid = set(value) - valid_codenames
        if invalid:
            raise serializers.ValidationError(f"Invalid permissions: {invalid}")
        return value

    def create(self, validated_data):
        permissions = validated_data.pop('permissions_write', [])
        password = validated_data.pop('password', None)

        if password:
            validated_data['password'] = make_password(password)

        # Create the linked UserAccount
        user = UserAccount(
            email=validated_data['email'],
            username=validated_data['username'],
            roles='cab-admin', 
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


# class DriverImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DriverImage
#         fields = ['id', 'image', 'caption']

#     def get_image(self, obj):
#         request = self.context.get('request')
#         if obj.image and hasattr(obj.image, 'url'):
#             return request.build_absolute_uri(obj.image.url) if request else obj.image.url
#         return None

class DriverSerializer(serializers.ModelSerializer):
    # images = DriverImageSerializer(many=True, read_only=True)

    class Meta:
        model = Driver
        fields = [
            'id', 'name', 'phone_number', 'email', 'license_number', 'license_expiry',
            'address', 'profile_image', 'aadhar_number', 'aadhar_document',
            'police_verification', 'is_verified', 'is_active', 'total_rides',
            'images', 'created_at'
        ]

    def validate_license_number(self, value):
        # Check for uniqueness, excluding the current instance in edit mode
        queryset = Driver.objects.filter(license_number=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            logger.warning(f"Duplicate license number detected: {value}")
            raise serializers.ValidationError("This license number is already in use")
        return value

    def validate_phone_number(self, value):
        # Check for uniqueness, excluding the current instance in edit mode
        queryset = Driver.objects.filter(phone_number=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            logger.warning(f"Duplicate phone number detected: {value}")
            raise serializers.ValidationError("This phone number is already in use")
        return value

    def validate_email(self, value):
        # Check for uniqueness, excluding the current instance in edit mode
        queryset = Driver.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            logger.warning(f"Duplicate email detected: {value}")
            raise serializers.ValidationError("This email is already in use")
        return value

    def validate(self, data):
        # Ensure license_expiry is a valid date
        if data.get('license_expiry') and not isinstance(data['license_expiry'], date):
            raise serializers.ValidationError({"license_expiry": "Invalid date format"})
        return data

class CabCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CabCategory
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all(), required=False, allow_null=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)  # For display in list/retrieve

    class Meta:
        model = Vehicle
        fields = '__all__'

class CabSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), write_only=True, source='vehicle')
    driver = DriverSerializer(read_only=True)
    driver_id = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all(), write_only=True, source='driver')
    category = CabCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=CabCategory.objects.all(), write_only=True, source='category')

    class Meta:
        model = Cab
        fields = [
            'id', 'vehicle', 'vehicle_id', 'driver', 'driver_id', 'category', 'category_id',
            'price_per_km', 'is_available', 'rating', 'is_verified', 'is_active',
            'base_fare', 'description', 'total_trips',
        ]

# Cab status change
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

class DriverStatusSerializer(serializers.ModelSerializer):
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
