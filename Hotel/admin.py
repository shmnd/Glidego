from django.contrib import admin
from safedelete.admin import SafeDeleteAdmin, highlight_deleted
from .models import Branch, Hotels, HotelImage, Room, RoomImage

# Inline for HotelImage to manage gallery images within Hotels admin
class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1  # Number of empty forms to display
    fields = ['image', 'created_date', 'modified_date', 'created_by', 'modified_by']
    readonly_fields = ['created_date', 'modified_date', 'created_by', 'modified_by']

# Inline for RoomImage to manage gallery images within Room admin
class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1
    fields = ['image', 'created_date', 'modified_date', 'created_by', 'modified_by']
    readonly_fields = ['created_date', 'modified_date', 'created_by', 'modified_by']

# Admin for Branch
@admin.register(Branch)
class BranchAdmin(SafeDeleteAdmin):
    list_display = [highlight_deleted, 'name', 'location', 'is_active', 'created_date', 'modified_date']
    list_filter = ['is_active', 'created_date', 'modified_date']
    search_fields = ['name', 'location']
    readonly_fields = ['created_date', 'modified_date', 'created_by', 'modified_by']

# Admin for Hotels
@admin.register(Hotels)
class HotelsAdmin(SafeDeleteAdmin):
    list_display = [highlight_deleted, 'name', 'branch', 'address', 'contact_email', 'contact_phone', 'is_verified', 'is_active']
    list_filter = ['is_active', 'is_verified', 'branch', 'created_date']
    search_fields = ['name', 'address', 'contact_email', 'contact_phone']
    inlines = [HotelImageInline]
    readonly_fields = ['created_date', 'modified_date', 'created_by', 'modified_by']
    fieldsets = (
        (None, {
            'fields': ('name', 'branch', 'location', 'address', 'description', 'facilities', 'main_image', 'contact_email', 'contact_phone', 'website', 'is_verified', 'is_active')
        }),
        ('Audit', {
            'fields': ('created_date', 'modified_date', 'created_by', 'modified_by')
        }),
    )

# Admin for HotelImage
@admin.register(HotelImage)
class HotelImageAdmin(SafeDeleteAdmin):
    list_display = [highlight_deleted, 'hotel', 'image', 'created_date', 'modified_date']
    list_filter = ['hotel', 'created_date']
    search_fields = ['hotel__name']
    readonly_fields = ['created_date', 'modified_date', 'created_by', 'modified_by']

# Admin for Room
@admin.register(Room)
class RoomAdmin(SafeDeleteAdmin):
    list_display = [highlight_deleted, 'hotel', 'room_type', 'name', 'price', 'availability', 'max_occupancy', 'is_active']
    list_filter = ['hotel', 'room_type', 'availability', 'is_active', 'created_date']
    search_fields = ['hotel__name', 'name', 'room_type']
    inlines = [RoomImageInline]
    readonly_fields = ['created_date', 'modified_date', 'created_by', 'modified_by']
    fieldsets = (
        (None, {
            'fields': ('hotel', 'room_type', 'name', 'description', 'price', 'availability', 'max_occupancy', 'facilities', 'image', 'is_active')
        }),
        ('Audit', {
            'fields': ('created_date', 'modified_date', 'created_by', 'modified_by')
        }),
    )

# Admin for RoomImage
@admin.register(RoomImage)
class RoomImageAdmin(SafeDeleteAdmin):
    list_display = [highlight_deleted, 'room', 'image', 'created_date', 'modified_date']
    list_filter = ['room', 'created_date']
    search_fields = ['room__name', 'room__hotel__name']
    readonly_fields = ['created_date', 'modified_date', 'created_by', 'modified_by']