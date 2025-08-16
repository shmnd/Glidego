import logging
from rest_framework import serializers
from Hotel.models import Hotels, Room, Branch, HotelImage, RoomImage, HotelAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
import logging

logger = logging.getLogger(__name__)
UserAccount = get_user_model()



UserAccount = get_user_model()
logger = logging.getLogger(__name__)

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name']

class HotelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        fields = ['image']

class HotelSerializer(serializers.ModelSerializer):
    id   = serializers.IntegerField(allow_null=True,required=False)
    main_image = serializers.ImageField(required=False, allow_null=True)
    gallery = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    branch_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Hotels
        fields = [
            'branch_id','id', 'name', 'location', 'address', 'description',
            'facilities', 'main_image', 'gallery', 'contact_email',
            'contact_phone', 'website', 'is_verified', 'is_active'
        ]
        extra_kwargs = {
            'name': {'required': False, 'allow_null': True},
            'location': {'required': False, 'allow_null': True},
            'address': {'required': False, 'allow_null': True},
            'description': {'required': False, 'allow_null': True},
            'facilities': {'required': False, 'allow_null': True},
            'contact_email': {'required': False, 'allow_null': True},
            'contact_phone': {'required': False, 'allow_null': True},
            'website': {'required': False, 'allow_null': True},
            'is_verified': {'required': False},
            'is_active': {'required': False},
        }

    def validate_branch_id(self, value):
        if value:
            try:
                branch = Branch.objects.get(id=value)
            except Branch.DoesNotExist:
                logger.error(f"Branch does not exist: {value}")
                raise serializers.ValidationError("Branch does not exist.")
            return branch
        return None

    def validate_contact_phone(self, value):
        if value and Hotels.objects.filter(contact_phone=value).exists():
            logger.error(f"Phone number already exists: {value}")
            raise serializers.ValidationError("Phone number already exists.")
        return value

    def validate_facilities(self, value):
        if value:
            try:
                if isinstance(value, str):
                    facilities_list = [f.strip() for f in value.split(',') if f.strip()]
                    return ','.join(facilities_list)
            except Exception as e:
                logger.error(f"Invalid facilities format: {e}")
                raise serializers.ValidationError("Facilities must be a comma-separated list or valid JSON.")
        return value

    def create(self, validated_data):
        logger.debug(f"Creating hotel with data: {validated_data}")
        gallery_images = validated_data.pop('gallery', [])
        main_image = validated_data.pop('main_image', None)
        branch = validated_data.pop('branch_id', None)
        user = self.context['request'].user

        try:
            hotel = Hotels.objects.create(
                branch=branch,
                created_by=user,
                modified_by=user,
                **validated_data
            )
            if main_image:
                hotel.main_image = main_image
                hotel.save()

            for image in gallery_images:
                HotelImage.objects.create(
                    hotel=hotel,
                    image=image,
                    created_by=user,
                    modified_by=user
                )
            logger.info(f"Hotel created successfully: {hotel.name}")
            return hotel
        except Exception as e:
            logger.error(f"Error creating hotel: {e}")
            raise serializers.ValidationError(f"Failed to create hotel: {str(e)}")

class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ['image']

class RoomSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    gallery = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Room
        fields = [
            'hotel', 'room_type', 'name', 'description', 'price',
            'availability', 'max_occupancy', 'facilities', 'image', 'gallery'
        ]
        extra_kwargs = {
            'hotel': {'required': True},
            'room_type': {'required': True},
            'name': {'required': False, 'allow_null': True},
            'description': {'required': False, 'allow_null': True},
            'price': {'required': True},
            'availability': {'required': False},
            'max_occupancy': {'required': True},
            'facilities': {'required': False, 'allow_null': True},
        }

    def validate_hotel(self, value):
        if not value:
            logger.error("Hotel is required")
            raise serializers.ValidationError("Hotel is required.")
        if not Hotels.objects.filter(id=value.id).exists():
            logger.error(f"Hotel does not exist: {value.id}")
            raise serializers.ValidationError("Hotel does not exist.")
        return value

    def validate_price(self, value):
        if value <= 0:
            logger.error(f"Invalid price: {value}")
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_max_occupancy(self, value):
        if value <= 0:
            logger.error(f"Invalid max occupancy: {value}")
            raise serializers.ValidationError("Max occupancy must be greater than zero.")
        return value

    def validate_facilities(self, value):
        if value:
            try:
                if isinstance(value, str):
                    facilities_list = [f.strip() for f in value.split(',') if f.strip()]
                    return ','.join(facilities_list)
            except Exception as e:
                logger.error(f"Invalid facilities format: {e}")
                raise serializers.ValidationError("Facilities must be a comma-separated list or valid JSON.")
        return value

    def create(self, validated_data):
        logger.debug(f"Creating room with data: {validated_data}")
        gallery_images = validated_data.pop('gallery', [])
        main_image = validated_data.pop('image', None)
        user = self.context['request'].user

        try:
            room = Room.objects.create(
                created_by=user,
                modified_by=user,
                **validated_data
            )
            if main_image:
                room.image = main_image
                room.save()

            for image in gallery_images:
                RoomImage.objects.create(
                    room=room,
                    image=image,
                    created_by=user,
                    modified_by=user
                )
            logger.info(f"Room created successfully: {room}")
            return room
        except Exception as e:
            logger.error(f"Error creating room: {e}")
            raise serializers.ValidationError(f"Failed to create room: {str(e)}")
        


class HotelAdminCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    permissions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = HotelAdmin
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
            'pan_number',
            'aadhar',
            'permissions',
            'verification_file',
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
            'pan_number': {'required': True},
            'license_number': {'required': True},
            'license': {'required': False},
            'aadhar': {'required': False},
            'verification_file': {'required': False},

        }

    def validate_email(self, value):
        if HotelAdmin.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    
    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_username(self, value):
        if HotelAdmin.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_permissions(self, value):
        if not value:
            return []
        
        # Get all available permissions for allowed apps
        valid_permissions = Permission.objects.filter(
            content_type__app_label__in=['Hotel']  # limit to your app
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
        hotel_admin = HotelAdmin.objects.create(
            user=user,
            **validated_data
        )

        if permissions:
            hotel_admin.permissions.set(
                Permission.objects.filter(codename__in=permissions)
            )
        return hotel_admin


# status change

# class HotelStautsSerializer(serializers.ModelSerializer):
#     id   = serializers.IntegerField(allow_null=True,required=False)

#     class Meta:
#         model = Hotels
#         fields = [
#           'id','is_verified', 'is_active'
#         ]
#         extra_kwargs = {
#             'id': {'required': True},
#             'is_verified': {'required': True},
#             'is_active': {'required': True},
#         }