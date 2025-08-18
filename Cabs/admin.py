from django.contrib import admin
from .models import CabAdmin

@admin.register(CabAdmin)
class CabAdminAdmin(admin.ModelAdmin):
	list_display = ('id', 'full_name', 'email', 'username', 'phone_number', 'primary_phone_number', 'gst_number', 'license_number')
	search_fields = ('full_name', 'email', 'username', 'phone_number', 'primary_phone_number', 'gst_number', 'license_number')

from django.contrib import admin
from .models import Cab, CabCategory, Driver, Vehicle


@admin.register(Cab)
class CabAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Cab._meta.fields]
	search_fields = [field.name for field in Cab._meta.fields]
	list_filter = [field.name for field in Cab._meta.fields]

@admin.register(CabCategory)
class CabCategoryAdmin(admin.ModelAdmin):
	list_display = [field.name for field in CabCategory._meta.fields]
	search_fields = [field.name for field in CabCategory._meta.fields]
	list_filter = [field.name for field in CabCategory._meta.fields]

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Driver._meta.fields]
	search_fields = [field.name for field in Driver._meta.fields]
	list_filter = [field.name for field in Driver._meta.fields]

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Vehicle._meta.fields]
	search_fields = [field.name for field in Vehicle._meta.fields]
	list_filter = [field.name for field in Vehicle._meta.fields]
