from django.contrib import admin
from .models import Destination, HighlightImage

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
	list_display = ('id', 'main_destination_city', 'main_destination_state', 'main_destination_country', 'is_active', 'order')
	search_fields = ('main_destination_city', 'main_destination_state', 'main_destination_country')
	list_filter = ('is_active', 'main_destination_country', 'travel_type')

@admin.register(HighlightImage)
class HighlightImageAdmin(admin.ModelAdmin):
	list_display = ('id', 'destination', 'image')

# @admin.register(Activity)
# class ActivityAdmin(admin.ModelAdmin):
# 	list_display = ('id', 'name', 'price', 'duration', 'is_bookable', 'is_active', 'is_featured')
# 	search_fields = ('name', 'description')
# 	list_filter = ('is_bookable', 'is_active', 'is_featured')

# @admin.register(ActivityImage)
# class ActivityImageAdmin(admin.ModelAdmin):
# 	list_display = ('id', 'activity', 'image')
