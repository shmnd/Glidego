# CabAdmin model for cab admin details with permissions
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from Hotel.models import AbstractDateTimeFieldBaseModel
from safedelete.models import SOFT_DELETE
from AuthUser.models import Permission

class Driver(AbstractDateTimeFieldBaseModel):
    __safedelete_policy__ = SOFT_DELETE

    class GenderType(models.TextChoices):
        male    = 'Male'
        female  = 'Female'
        other   = 'Other'

    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15,unique=True)
    email = models.EmailField(unique=True)
    license_number = models.CharField(max_length=100, unique=True)
    license_expiry = models.DateField(blank=True, null=True)
    address = models.TextField()
    profile_image = models.ImageField(upload_to='home/drivers/', blank=True, null=True)
    aadhar_number = models.CharField(max_length=20, blank=True)
    aadhar_document = models.FileField(upload_to='home/aadhar/', blank=True, null=True)
    police_verification = models.FileField(upload_to='home/police/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    total_rides = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    language = models.CharField(max_length=255,blank=True, null=True)
    experience = models.BigIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=100,choices=GenderType.choices,default=GenderType.male)


    def __str__(self):
        return self.name

# # Driver image model (inline to Driver)
# class DriverImage(AbstractDateTimeFieldBaseModel):
#     driver = models.ForeignKey(Driver, related_name='images', on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='drivers/gallery/')
#     caption = models.CharField(max_length=255, blank=True)

#     def __str__(self):
#         return f"Image for {self.driver}"



# Vehicle model
class Vehicle(AbstractDateTimeFieldBaseModel):
    
    class FuelType(models.TextChoices):
        petrol    = 'Petrol'
        deisel  = 'Deisel'
        electric   = 'Electric'
        cng = "CNG"

    owner = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='owned_vehicles', null= True, blank= True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, unique=True)
    seating_capacity = models.PositiveIntegerField(blank=True, null=True)
    vehicle_image = models.ImageField(upload_to='home/vehicle_image/', blank=True, null=True)
    vehicle_type = models.CharField(max_length=20)
    color = models.CharField(max_length=30, blank=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    insurance_number = models.CharField(max_length=100, blank=True)
    insurance_expiry = models.DateField(blank=True, null=True)
    rc_document = models.FileField(upload_to='home/rc/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    fuel = models.CharField(choices=FuelType.choices,max_length=100, blank=True, null=True)
    features = models.TextField(blank=True, null=True)

    transmission = models.CharField(max_length=25,blank=True, null=True)
    luggage = models.TextField(blank=True, null=True)
    air_conditioning = models.CharField(max_length=25,blank=True, null=True)
    rent_per_day = models.PositiveIntegerField(blank=True, null=True)
    rent_per_km = models.PositiveIntegerField(blank=True, null=True)
    rent_per_hour = models.PositiveIntegerField(blank=True, null=True)
    rent = models.PositiveIntegerField(blank=True, null=True)




    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.registration_number})"

# Vehicle Image model (inline to Vehicle)
class VehicleImage(AbstractDateTimeFieldBaseModel):
    vehicle = models.ForeignKey(Vehicle, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='vehicles/gallery/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.vehicle}"
    


##CAB##

# Category of the cab (e.g., SUV, Sedan, etc.)
class CabCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=False, default='Default description')
    # icon = models.CharField(max_length=50, blank=True)  # For admin/UI
    is_active = models.BooleanField(default=True)

    # order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name



# Cab model
class Cab(AbstractDateTimeFieldBaseModel):
    category = models.ForeignKey(CabCategory, on_delete=models.SET_NULL, null=True)
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2)
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    description = models.TextField(blank=True, null=True)
    rating = models.FloatField(default=0.0)
    total_trips = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return f"Cab - {self.vehicle} with Driver - {self.driver}"


UserAccount = get_user_model()
class CabAdmin(AbstractDateTimeFieldBaseModel):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name="cabadmin_profile", blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    primary_phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    secondary_phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    address = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    license_number = models.CharField(max_length=30, blank=True, null=True, unique=True)
    license = models.ImageField(upload_to='Cabs/license/')
    aadhar = models.ImageField(upload_to='Cabs/aadhar/')
    password = models.CharField(max_length=128, blank=True, null=True)
    permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='cabadmin_permissions',
        blank=True,
    )
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.full_name or (self.user.username if self.user else self.username)        