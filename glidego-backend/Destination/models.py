from django.db import models

from Hotel.models import AbstractDateFieldMix
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Activity(models.Model):
    name = models.CharField(max_length=255,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    # category = models.ForeignKey(ActivityCategory, on_delete=models.SET_NULL, null=True, blank=True)
    # tags = models.ManyToManyField(ActivityTag, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    image = models.ImageField(upload_to="activities/",blank=True, null=True)
    duration = models.CharField(max_length=100,blank=True,null=True,help_text="e.g. 2 hours, Full day")
    start_time = models.TimeField(blank=True,null=True)
    end_time = models.TimeField(blank=True, null=True)
    available_dates = models.TextField(blank=True,null=True,help_text="Comma-separated or JSON for available dates")
    is_bookable = models.BooleanField(default=True)
    max_participants = models.PositiveIntegerField(blank=True, null=True)
    min_age = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    activity_gallery = models.ManyToManyField('ActivityImage', blank=True, related_name='activity_gallery')

    def __str__(self):
        return self.name


class ActivityImage(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='activity_images')
    image = models.ImageField(upload_to='destinations/activity_images/')

    def __str__(self):
        return f"Image for {self.activity.name}"




class Destination(AbstractDateFieldMix):
    class TravelType(models.TextChoices):
        honeymoon = "Honey Moon"
        adventure = "Adventure"
        family = "Family"
        nature = "Nature"

    main_destination_image =  models.FileField(_('Main Destination Name'), blank=True, null=True)
    main_destination_city = models.CharField(_('Main Destination City'), max_length=255, blank=True, null=True)
    main_destination_state = models.CharField(_('Main Destination State'), max_length=255, blank=True, null=True)
    main_destination_country = models.CharField(_('Main Destination Country'), max_length=255, blank=True, null=True)
    main_destination_heading = models.CharField(_('Main Destination Heading'), max_length=255, blank=True, null=True)
    main_destination_description = models.TextField(_('Main Destination Description'), blank=True, null=True)
    destination_highlight_description = models.TextField(_('Destination highlight-description'), blank=True, null=True)
    latitude = models.DecimalField(_('Latitude'), max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(_('Longitude'), max_digits=9, decimal_places=6, blank=True, null=True)
    map_link = models.URLField(_('Map link'), blank=True, null=True)
    highlight_image = models.FileField(_('highlight Main Image'), blank=True, null=True)
    highlight_heading = models.CharField(_('highlight Main Heading'), max_length=255, blank=True, null=True)
    highlight_description = models.TextField(_('highlight Main Description'), blank=True, null=True)
    best_visit_time = models.TextField(_('Best time to visit'), blank=True, null=True)
    avg_cost = models.DecimalField(_('Average cost'), max_digits=10, decimal_places=2, blank=True, null=True)
    activities = models.ForeignKey(Activity,on_delete=models.CASCADE,related_name='activities',blank=True, null=True)
    travel_guide = models.TextField(_('Travel Guide'), blank=True, null=True)
    
    is_active = models.BooleanField(_('Is active'), blank=True, null=True, default=True)
    order = models.PositiveIntegerField(_('Order'), blank=True, null=True, default=0)
    weather = models.URLField(_('Weather'),blank=True, null=True)
    currency = models.CharField(_('Currency'),max_length=255,blank=True, null=True)
    travel_type = models.CharField(_('Travel type'),max_length=255,choices=TravelType.choices,blank=True, null=True)



    class Meta:
        verbose_name          = "Destination"
        verbose_name_plural   = "Destinations"