from rest_framework import serializers
from .models import Destination, Activity, ActivityImage
from django.conf import settings


class ActivityImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ActivityImage
        fields = ['id', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class ActivitySerializer(serializers.ModelSerializer):
    activity_images = ActivityImageSerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = [
            'id', 'name', 'description', 'price', 'image', 'duration',
            'start_time', 'end_time', 'available_dates', 'is_bookable',
            'max_participants', 'min_age', 'is_active', 'is_featured',
            'activity_images'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class DestinationSerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(read_only=True)
    activity_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    main_destination_image = serializers.SerializerMethodField()
    highlight_image = serializers.SerializerMethodField()

    class Meta:
        model = Destination
        fields = [
            'id', 'main_destination_image', 'main_destination_city', 'main_destination_state',
            'main_destination_country', 'main_destination_heading', 'main_destination_description',
            'destination_highlight_description', 'latitude', 'longitude', 'map_link',
            'highlight_image', 'highlight_heading', 'highlight_description', 'best_visit_time',
            'avg_cost', 'activities', 'activity_id', 'travel_guide', 'is_active', 'order',
            'weather', 'currency', 'travel_type'
        ]

    def get_main_destination_image(self, obj):
        request = self.context.get('request')
        if obj.main_destination_image and hasattr(obj.main_destination_image, 'url'):
            return request.build_absolute_uri(obj.main_destination_image.url) if request else obj.main_destination_image.url
        return None

    def get_highlight_image(self, obj):
        request = self.context.get('request')
        if obj.highlight_image and hasattr(obj.highlight_image, 'url'):
            return request.build_absolute_uri(obj.highlight_image.url) if request else obj.highlight_image.url
        return None

    def create(self, validated_data):
        activity_id = validated_data.pop('activity_id', None)
        if activity_id:
            validated_data['activities'] = Activity.objects.get(id=activity_id)
        return Destination.objects.create(**validated_data)

    def update(self, instance, validated_data):
        activity_id = validated_data.pop('activity_id', None)
        if activity_id is not None:
            instance.activities = Activity.objects.get(id=activity_id) if activity_id else None
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
# staus change seriliazer 
class DestinationStautsSerializer(serializers.ModelSerializer):
    id   = serializers.IntegerField(allow_null=True,required=False)

    class Meta:
        model = Destination
        fields = [
          'id', 'is_active'
        ]
        extra_kwargs = {
            'id': {'required': True},
            'is_active': {'required': True},
        }
