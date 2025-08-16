from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password

class AbstractDateFieldMix(models.Model):
    created_date = models.DateTimeField(_('created_date'), auto_now_add=True, editable=False, blank=True, null=True)
    modified_date = models.DateTimeField(_('modified_date'), auto_now=True, editable=False, blank=True, null=True)

    class Meta:
        abstract = True

class AbstractDateTimeFieldBaseModel(SafeDeleteModel, AbstractDateFieldMix):
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='%(class)s_created', null=True, blank=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='%(class)s_modified', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

class Branch(AbstractDateTimeFieldBaseModel):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class Hotels(AbstractDateTimeFieldBaseModel):
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, related_name='hotels', null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    location = models.URLField(_('Hotel Location'), blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    facilities = models.TextField(help_text="Comma-separated or JSON list of facilities", blank=True, null=True)
    main_image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    gallery = models.ManyToManyField('HotelImage', blank=True, related_name='hotel_gallery')
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=15, blank=True, null=True, unique=True)
    website = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class HotelImage(AbstractDateTimeFieldBaseModel):
    hotel = models.ForeignKey(Hotels, on_delete=models.CASCADE, related_name='hotel_images')
    image = models.ImageField(upload_to='home/hotel_images/')

class Room(AbstractDateTimeFieldBaseModel):
    ROOM_TYPE_CHOICES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
        ('deluxe', 'Deluxe'),
        ('family', 'Family'),
        ('other', 'Other'),
    ]
    hotel = models.ForeignKey(Hotels, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.CharField(max_length=50, choices=ROOM_TYPE_CHOICES)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)
    max_occupancy = models.PositiveIntegerField(default=1)
    facilities = models.TextField(blank=True, null=True, help_text="Comma-separated or JSON list of facilities")
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)
    gallery = models.ManyToManyField('RoomImage', blank=True, related_name='room_gallery')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type}"

class RoomImage(AbstractDateTimeFieldBaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_images')
    image = models.ImageField(upload_to='room_images/')



UserAccount = get_user_model()
class HotelAdmin(AbstractDateTimeFieldBaseModel):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name="hoteladmin_profile",blank=True, null=True)
    full_name = models.CharField(max_length=255,blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True,unique=True)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255,unique=True)
    primary_phone_number = models.CharField(max_length=15, blank=True, null=True,unique=True)
    secondary_phone_number = models.CharField(max_length=15, blank=True, null=True,unique=True)
    address = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True,unique=True)
    license_number = models.CharField(max_length=30, blank=True, null=True,unique=True)
    pan_number = models.CharField(max_length=30, blank=True, null=True,unique=True)
    aadhar = models.ImageField(upload_to='Hotel/aadhar/')
    license = models.ImageField(upload_to='Hotel/license-file/')
    verification_file = models.ImageField(upload_to='Hotel/aadhar/')

    password = models.CharField(max_length=128,blank=True, null=True)
    permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='hoteladmin_permissions',
        blank=True,
    )

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.full_name or self.user.username
