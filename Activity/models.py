from django.db import models
from ckeditor.fields import RichTextField

class Activity(models.Model):
    DURATION_UNITS = (
        ('days', 'Days'),
        ('hours', 'Hours'),
        ('minutes', 'Minutes'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    location = models.URLField(blank=True, null=True)
    rating = models.PositiveIntegerField(blank=True, null=True, help_text="Number of stars for rating (1-5)")
    cost_per_person = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    is_bookable = models.BooleanField(default=True)
    max_participants = models.PositiveIntegerField(blank=True, null=True)
    min_age = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    banner_image = models.ImageField(upload_to="activity_banner/", blank=True, null=True, help_text="Banner image for the activity")
    duration_value = models.PositiveIntegerField(blank=True, null=True, help_text="Numeric value for duration")
    duration_unit = models.CharField(max_length=10, choices=DURATION_UNITS, blank=True, null=True, help_text="Unit of duration")

    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return self.name



	





