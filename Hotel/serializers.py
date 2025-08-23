import logging
from rest_framework import serializers
from Hotel.models import HotelAdmin, Hotels, Room, Branch, HotelImage, RoomImage
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Permission

UserAccount = get_user_model()
logger = logging.getLogger(__name__)

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'location', 'is_active']
        extra_kwargs = {
            'name': {'required': True},
            'location': {'required': False, 'allow_null': True},
            'is_active': {'required': False},
        }

    def create(self, validated_data):
        logger.debug(f"Creating branch with data: {validated_data}")
        user = self.context['request'].user
        try:
            branch = Branch.objects.create(
                created_by=user,
                modified_by=user,
                **validated_data
            )
            logger.info(f"Branch created successfully: {branch.name}")
            return branch
        except Exception as e:
            logger.error(f"Error creating branch: {e}")
            raise serializers.ValidationError(f"Failed to create branch: {str(e)}")

    def update(self, instance, validated_data):
        logger.debug(f"Updating branch {instance.id} with data: {validated_data}")
        user = self.context['request'].user
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.modified_by = user
            instance.save()
            logger.info(f"Branch updated successfully: {instance.name}")
            return instance
        except Exception as e:
            logger.error(f"Error updating branch {instance.id}: {e}")
            raise serializers.ValidationError(f"Failed to update branch: {str(e)}")

    def validate_name(self, value):
        if self.instance and self.instance.name == value:
            return value
        if Branch.objects.filter(name=value).exists():
            logger.error(f"Branch name already exists: {value}")
            raise serializers.ValidationError("Branch name already exists.")
        return value

class HotelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        fields = ['id', 'image', 'created_date', 'modified_date', 'created_by', 'modified_by']

class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ['id', 'image', 'created_date', 'modified_date', 'created_by', 'modified_by']

class RoomSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    gallery_input = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    hotel_id = serializers.IntegerField(required=True, write_only=True)
    hotel = serializers.SerializerMethodField()
    gallery = RoomImageSerializer(many=True, read_only=True, source='room_images')

    class Meta:
        model = Room
        fields = [
            'id', 'hotel_id', 'hotel', 'room_type', 'name', 'description',
            'sqft', 'room_no', 'block', 'floor','parking', 'buffet', 'tv', 
            'balcony', 'wifi', 'ac', 'amenities', 'price', 'offer',
            'availability', 'max_occupancy', 'facilities', 'image', 'gallery_input', 'gallery', 'is_active'
        ]
        extra_kwargs = {
            'hotel': {'read_only': True},
            'room_type': {'required': True},
            'name': {'required': False, 'allow_null': True},
            'description': {'required': False, 'allow_null': True},
            'price': {'required': True},
            'offer': {'required': False, 'allow_null': True},
            'sqft': {'required': False, 'allow_null': True},
            'room_no': {'required': False, 'allow_null': True},
            'block': {'required': False, 'allow_null': True},
            'floor': {'required': False, 'allow_null': True},
            'parking': {'required': False},
            'buffet': {'required': False},
            'tv': {'required': False},
            'balcony': {'required': False},
            'wifi': {'required': False},
            'ac': {'required': False},
            'amenities': {'required': False},
            'availability': {'required': False},
            'max_occupancy': {'required': True},
            'facilities': {'required': False, 'allow_null': True},
            'is_active': {'required': False},
        }

    def get_hotel(self, obj):
        # Avoid circular import by defining a lightweight hotel representation
        hotel = obj.hotel
        return {
            'id': hotel.id,
            'name': hotel.name,
            'is_verified': hotel.is_verified,
            'is_active': hotel.is_active,
        }

    def validate_hotel_id(self, value):
        try:
            hotel = Hotels.objects.get(id=value)
        except Hotels.DoesNotExist:
            logger.error(f"Hotel does not exist: {value}")
            raise serializers.ValidationError("Hotel does not exist.")
        return hotel

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
        gallery_images = validated_data.pop('gallery_input', [])
        main_image = validated_data.pop('image', None)
        hotel = validated_data.pop('hotel_id')
        user = self.context['request'].user

        try:
            room = Room.objects.create(
                hotel=hotel,
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

    def update(self, instance, validated_data):
        logger.debug(f"Updating room {instance.id} with data: {validated_data}")
        gallery_images = validated_data.pop('gallery_input', [])
        main_image = validated_data.pop('image', None)
        hotel = validated_data.pop('hotel_id', None)
        clear_gallery = validated_data.pop('clear_gallery', False)
        user = self.context['request'].user

        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            if hotel is not None:
                instance.hotel = hotel
            if main_image is not None:
                instance.image = main_image

            instance.modified_by = user
            instance.save()

            if clear_gallery or gallery_images:
                instance.room_images.all().delete()
                if gallery_images:
                    for image in gallery_images:
                        RoomImage.objects.create(
                            room=instance,
                            image=image,
                            created_by=user,
                            modified_by=user
                        )

            logger.info(f"Room updated successfully: {instance}")
            return instance
        except Exception as e:
            logger.error(f"Error updating room {instance.id}: {e}")
            raise serializers.ValidationError(f"Failed to update room: {str(e)}")

class HotelSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(allow_null=True, required=False)
    main_image = serializers.ImageField(required=False, allow_null=True)
    gallery_input = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    branch_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    branch = BranchSerializer(read_only=True)
    gallery = HotelImageSerializer(many=True, read_only=True, source='hotel_images')
    rooms = RoomSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(source='created_date', read_only=True)
    updated_at = serializers.DateTimeField(source='modified_date', read_only=True)

    class Meta:
        model = Hotels
        fields = [
            'branch_id', 'branch', 'id', 'name', 'location', 'address', 'description',
            'facilities', 'main_image', 'gallery_input', 'gallery', 'contact_email',
            'contact_phone', 'website', 'rooms', 'latitude', 'longitude', 'price', 'offer',
            'rooms', 'created_at', 'updated_at', 'is_verified', 'is_active',
        ]
        extra_kwargs = {
            'name': {'required': True},
            'location': {'required': False, 'allow_null': True},
            'address': {'required': False, 'allow_null': True},
            'description': {'required': False, 'allow_null': True},
            'facilities': {'required': False, 'allow_null': True},
            'contact_email': {'required': False, 'allow_null': True},
            'contact_phone': {'required': False, 'allow_null': True},
            'website': {'required': False, 'allow_null': True},
            'latitude': {'required': False, 'allow_null': True},
            'longitude': {'required': False, 'allow_null': True},
            'price': {'required': False, 'allow_null': True},
            'offer': {'required': False, 'allow_null': True},
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
        if value and Hotels.objects.filter(contact_phone=value).exclude(id=self.instance.id if self.instance else None).exists():
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
        gallery_images = validated_data.pop('gallery_input', [])
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

    def update(self, instance, validated_data):
        logger.debug(f"Updating hotel {instance.id} with data: {validated_data}")
        gallery_images = validated_data.pop('gallery_input', [])
        main_image = validated_data.pop('main_image', None)
        branch = validated_data.pop('branch_id', None)
        clear_gallery = validated_data.pop('clear_gallery', False)
        user = self.context['request'].user

        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            if branch is not None:
                instance.branch = branch
            if main_image is not None:
                instance.main_image = main_image

            instance.modified_by = user
            instance.save()

            if clear_gallery or gallery_images:
                instance.hotel_images.all().delete()
                if gallery_images:
                    for image in gallery_images:
                        HotelImage.objects.create(
                            hotel=instance,
                            image=image,
                            created_by=user,
                            modified_by=user
                        )

            logger.info(f"Hotel updated successfully: {instance.name}")
            return instance
        except Exception as e:
            logger.error(f"Error updating hotel {instance.id}: {e}")
            raise serializers.ValidationError(f"Failed to update hotel: {str(e)}")
        

UserAccount = get_user_model()
logger = logging.getLogger(__name__)

class HotelAdminListSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='codename'
    )
    created_date = serializers.DateTimeField(read_only=True)
    modified_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = HotelAdmin
        fields = [
            'id',
            'full_name',
            'email',
            'username',
            'phone_number',
            'primary_phone_number',
            'secondary_phone_number',
            'address',
            'gst_number',
            'license_number',
            'license',
            'pan_number',
            'aadhar',
            'verification_file',
            'is_verified',
            'permissions',
            'created_date',
            'modified_date'
        ]

class HotelAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelAdmin
        fields = ['is_verified']
        extra_kwargs = {
            'is_verified': {'required': True}
        }

    def update(self, instance, validated_data):
        logger.debug(f"Updating HotelAdmin {instance.id} with data: {validated_data}")
        try:
            instance.is_verified = validated_data.get('is_verified', instance.is_verified)
            instance.modified_by = self.context['request'].user
            instance.save()
            logger.info(f"HotelAdmin {instance.id} updated successfully")
            return instance
        except Exception as e:
            logger.error(f"Error updating HotelAdmin {instance.id}: {e}")
            raise serializers.ValidationError(f"Failed to update HotelAdmin: {str(e)}")

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
            'verification_file'
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
        
        valid_permissions = Permission.objects.filter(
            content_type__app_label__in=['Hotel']
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

        user = UserAccount(
            email=validated_data['email'],
            username=validated_data['username'],
            roles='hotel-admin', 
        )
        user.set_password(password)
        user.save()

        hotel_admin = HotelAdmin.objects.create(
            user=user,
            **validated_data
        )

        if permissions:
            hotel_admin.user.user_permissions.set(
                Permission.objects.filter(codename__in=permissions)
            )
        return hotel_admin


class HotelVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotels
        fields = ['id', 'is_verified']
        read_only_fields = ['id']

    def validate(self, data):
        # Ensure is_verified is True for this endpoint
        if not data.get('is_verified', False):
            raise serializers.ValidationError({"is_verified": "Hotel verification requires is_verified to be True."})
        return data
