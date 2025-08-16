from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.password_validation import validate_password
import logging

UserAccount = get_user_model()
logger = logging.getLogger(__name__)

class StaffCreateSerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )

    class Meta:
        model = UserAccount
        fields = [
            'email', 'username', 'password', 'first_name', 'last_name',
            'gender', 'address', 'phone_number', 'permissions'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'gender': {'required': False},
            'address': {'required': False},
            'phone_number': {'required': False},
        }

    def validate_email(self, value):
        logger.debug(f"Validating email: {value}")
        if UserAccount.objects.filter(email=value).exists():
            logger.error(f"Email already exists: {value}")
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_username(self, value):
        logger.debug(f"Validating username: {value}")
        if UserAccount.objects.filter(username=value).exists():
            logger.error(f"Username already exists: {value}")
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_gender(self, value):
        logger.debug(f"Validating gender: {value}")
        if value and value not in ['male', 'female', 'others']:
            logger.error(f"Invalid gender: {value}")
            raise serializers.ValidationError("Gender must be 'male', 'female', or 'others'.")
        return value

    def validate_password(self, value):
        logger.debug(f"Validating password")
        try:
            validate_password(value, self.instance)
        except ValidationError as e:
            logger.error(f"Password validation failed: {e}")
            raise serializers.ValidationError(str(e))
        return value

    def validate_permissions(self, value):
        logger.debug(f"Validating permissions: {value}")
        if not value:
            return []

        # Map frontend codenames to Django codenames
        codename_mapping = {
            'add_hotel': 'add_hotels',
            'view_hotel': 'view_hotels',
            'change_hotel': 'change_hotels',
            'delete_hotel': 'delete_hotels',
            'add_cab': 'add_cab',
            'view_cab': 'view_cab',
            'change_cab': 'change_cab',
            'delete_cab': 'delete_cab',
            'add_destination': 'add_destination',
            'view_destination': 'view_destination',
            'change_destination': 'change_destination',
            'delete_destination': 'delete_destination',
            'add_activity': 'add_activity',
            'view_activity': 'view_activity',
            'change_activity': 'change_activity',
            'delete_activity': 'delete_activity',
            'add_driver': 'add_driver',
            'view_driver': 'view_driver',
            'change_driver': 'change_driver',
            'delete_driver': 'delete_driver',
            'add_user': 'add_user',
            'view_user': 'view_user',
            'change_user': 'change_user',
            'delete_user': 'delete_user',
        }

        # Convert frontend codenames to Django codenames
        mapped_permissions = [codename_mapping.get(perm, perm) for perm in value]
        logger.debug(f"Mapped permissions: {mapped_permissions}")

        # Fetch valid permissions
        valid_permissions = Permission.objects.filter(
            content_type__app_label__in=['Hotel', 'Cabs', 'Destination', 'AuthUser']
        )
        valid_codenames = valid_permissions.values_list('codename', flat=True)
        logger.debug(f"Available permissions: {list(valid_codenames)}")
        logger.debug(f"Permission details: {list(valid_permissions.values('codename', 'content_type__app_label', 'content_type__model'))}")

        invalid_permissions = set(mapped_permissions) - set(valid_codenames)
        if invalid_permissions:
            logger.error(f"Invalid permissions: {invalid_permissions}")
            raise serializers.ValidationError(f"Invalid permissions: {invalid_permissions}")
        return mapped_permissions

    def create(self, validated_data):
        logger.debug(f"Creating user with data: {validated_data}")
        permissions = validated_data.pop('permissions', [])
        try:
            user = UserAccount.objects.create_user(
                email=validated_data['email'],
                username=validated_data['username'],
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                gender=validated_data.get('gender', None),
                address=validated_data.get('address', None),
                phone_number=validated_data.get('phone_number', None),
            )
            if permissions:
                user.user_permissions.set(
                    Permission.objects.filter(codename__in=permissions)
                )
            logger.info(f"User created successfully: {user.email}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise serializers.ValidationError(f"Failed to create user: {str(e)}")