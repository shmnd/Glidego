from rest_framework import serializers
from .models import Activity

class ActivitySerializer(serializers.ModelSerializer):
    banner_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = '__all__'
        extra_fields = ['banner_image_url']

    def get_banner_image_url(self, obj):
        request = self.context.get('request')
        if obj.banner_image:
            if request:
                return request.build_absolute_uri(obj.banner_image.url)
            return obj.banner_image.url
        return None