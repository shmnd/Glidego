from django.db import models
import random
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class PhoneOTP(models.Model):
    phone = models.CharField(max_length=15, unique=True,blank=True, null=True)
    otp = models.CharField(max_length=6,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))