from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from Activity.models import Activity
from .models import Destination, HighlightImage
import logging

logger = logging.getLogger(__name__)



class HighlightImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = HighlightImage
        fields = ['id', 'image']

    def get_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url  # Return relative URL as stored
        return None

class ActivitySerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Activity
        fields = '__all__'

class DestinationSerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(read_only=True)
    activity_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    main_destination_image = serializers.FileField(write_only=True, required=False, allow_null=True)
    main_destination_image_url = serializers.SerializerMethodField(read_only=True)
    highlight_images = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False),
        write_only=True,
        required=False,
        allow_null=True
    )
    highlight_images_data = HighlightImageSerializer(source='highlight_images', many=True, read_only=True)

    class Meta:
        model = Destination
        fields = [
            'id', 'main_destination_image', 'main_destination_image_url', 'main_destination_city',
            'main_destination_state', 'main_destination_country', 'main_destination_heading',
            'main_destination_description', 'destination_highlight_description', 'latitude',
            'longitude', 'map_link', 'highlight_heading', 'highlight_description',
            'best_visit_time', 'avg_cost', 'activities', 'activity_id', 'is_active',
            'order', 'weather', 'currency', 'travel_type', 'highlight_images',
            'highlight_images_data',"kind_of_destination"
        ]

    def get_main_destination_image_url(self, obj):
        request = self.context.get('request')
        if obj.main_destination_image and hasattr(obj.main_destination_image, 'url'):
            return request.build_absolute_uri(obj.main_destination_image.url) if request else obj.main_destination_image.url
        return None

    def validate_travel_type(self, value):
        logger.debug(f"Validating travel_type: {value} (type: {type(value)})")
        if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
            logger.debug(f"Stripped quotes from travel_type: {value}")
        valid_choices = [choice[0] for choice in Destination.TravelType.choices]
        if value and value not in valid_choices:
            logger.error(f"Invalid travel_type: {value}. Must be one of {valid_choices}.")
            raise serializers.ValidationError(
                f"Invalid travel_type: {value}. Must be one of {valid_choices}."
            )
        return value
    
    def validate_kind_of_destination(self, value):
        logger.debug(f"Validating kind_of_destination: {value} (type: {type(value)})")
        
        valid_choices = [choice[0] for choice in Destination.DESTINATION_TYPE]

        if value and value not in valid_choices:
            logger.error(f"Invalid kind_of_destination: {value}. Must be one of {valid_choices}.")
            raise serializers.ValidationError(
                f"Invalid kind_of_destination: {value}. Must be one of {valid_choices}."
            )
        
        return value

    def validate_activity_id(self, value):
        logger.debug(f"Validating activity_id: {value}")
        if value is not None:
            try:
                Activity.objects.get(id=value)
            except Activity.DoesNotExist:
                logger.error(f"Activity with id {value} does not exist.")
                raise serializers.ValidationError(f"Activity with id {value} does not exist.")
        return value

    def validate(self, data):
        logger.debug(f"Validating data: {data}")
        # Handle MultiValueDict for main_destination_image
        main_image = data.get('main_destination_image')
        if isinstance(main_image, list):
            logger.debug(f"main_destination_image is a list: {main_image}")
            data['main_destination_image'] = main_image[0] if main_image else None

        # Validate highlight_images
        highlight_images = data.get('highlight_images', [])
        if highlight_images:
            for file in highlight_images:
                if not hasattr(file, 'content_type') or not file.content_type.startswith('image/'):
                    logger.error(f"Invalid file type for {file.name}: {file.content_type}")
                    raise serializers.ValidationError(f"File {file.name} is not a valid image.")
        return data

    def create(self, validated_data):
        logger.debug(f"Creating destination with validated data: {validated_data}")
        activity_id = validated_data.pop('activity_id', None)
        highlight_images = validated_data.pop('highlight_images', [])
        main_image = validated_data.get('main_destination_image')
        
        logger.debug(f"Main image: {main_image}")
        logger.debug(f"Highlight images: {[f.name for f in highlight_images] if highlight_images else []}")

        try:
            if activity_id:
                validated_data['activities'] = Activity.objects.get(id=activity_id)
            destination = Destination.objects.create(**validated_data)
            logger.info(f"Destination created: ID {destination.id}")

            # Save highlight images
            for file in highlight_images:
                logger.debug(f"Attempting to save highlight image: {file.name}")
                HighlightImage.objects.create(destination=destination, image=file)
                logger.debug(f"Created HighlightImage for destination ID {destination.id}: {file.name}")

            return destination
        except Exception as e:
            logger.error(f"Error creating destination: {str(e)}")
            raise serializers.ValidationError(f"Failed to create destination: {str(e)}")

    def update(self, instance, validated_data):
        logger.debug(f"Updating destination with validated data: {validated_data}")
        activity_id = validated_data.pop('activity_id', None)
        highlight_images = validated_data.pop('highlight_images', [])
        main_image = validated_data.get('main_destination_image')

        logger.debug(f"Main image: {main_image}")
        logger.debug(f"Highlight images: {[f.name for f in highlight_images] if highlight_images else []}")

        try:
            if activity_id is not None:
                instance.activities = Activity.objects.get(id=activity_id) if activity_id else None
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(f"Destination updated: ID {instance.id}")

            # Delete existing highlight images if new ones are uploaded
            if highlight_images:
                instance.highlight_images.all().delete()
                logger.debug(f"Deleted existing highlight images for destination ID {instance.id}")
                for file in highlight_images:
                    logger.debug(f"Attempting to save highlight image: {file.name}")
                    HighlightImage.objects.create(destination=instance, image=file)
                    logger.debug(f"Created HighlightImage for destination ID {instance.id}: {file.name}")

            return instance
        except Exception as e:
            logger.error(f"Error updating destination: {str(e)}")
            raise serializers.ValidationError(f"Failed to update destination: {str(e)}")