from django.db import models
from django.utils.translation import gettext_lazy as _


from django.db import models
from django.utils.translation import gettext_lazy as _

from Activity.models import Activity

# Assuming AbstractDateFieldMix is defined
class AbstractDateFieldMix(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# class Activity(models.Model):
#     name = models.CharField(max_length=255, blank=True, null=True)
#     description = models.TextField(blank=True, null=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     image = models.ImageField(upload_to="activities/", blank=True, null=True)
#     duration = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. 2 hours, Full day")
#     start_time = models.TimeField(blank=True, null=True)
#     end_time = models.TimeField(blank=True, null=True)
#     available_dates = models.TextField(blank=True, null=True, help_text="Comma-separated or JSON for available dates")
#     is_bookable = models.BooleanField(default=True)
#     max_participants = models.PositiveIntegerField(blank=True, null=True)
#     min_age = models.PositiveIntegerField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     is_featured = models.BooleanField(default=False)
#     activity_gallery = models.ManyToManyField('ActivityImage', blank=True, related_name='activity_gallery')

#     def __str__(self):
#         return self.name or "Unnamed Activity"

# class ActivityImage(models.Model):
#     activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='activity_images')
#     image = models.ImageField(upload_to='activities/images/')

#     def __str__(self):
#         return f"Image for {self.activity.name}"

class HighlightImage(models.Model):
    destination = models.ForeignKey('Destination', on_delete=models.CASCADE, related_name='highlight_images')
    image = models.ImageField(upload_to='destinations/highlight_images/',blank=False, null=False)

    def __str__(self):
        return f"Highlight Image for {self.destination.main_destination_city}"

class Destination(AbstractDateFieldMix):
    class TravelType(models.TextChoices):
        honeymoon = "honeymoon", _("Honey Moon")
        adventure = "adventure", _("Adventure")
        family = "family", _("Family")
        nature = "nature", _("Nature")

    
    DESTINATION_TYPE = [
        ('beach', 'Beach'),
        ('mountain', 'Mountain'),
        ('city', 'City'),
        ('island', 'Island'),
        ('desert', 'Desert'),
        ('countryside', 'Countryside'),
        ('forest', 'Forest'),
        ('historical', 'Historical'),
        ('adventure', 'Adventure'),
        ('wildlife', 'Wildlife / Safari'),
        ('kind_of_destination', 'Kind of destinationther'),
    ]


    main_destination_image = models.FileField(_('Main Destination Image'), upload_to='destinations/main/', blank=True, null=True)
    main_destination_city = models.CharField(_('Main Destination City'), max_length=255, blank=True, null=True)
    main_destination_state = models.CharField(_('Main Destination State'), max_length=255, blank=True, null=True)
    main_destination_country = models.CharField(_('Main Destination Country'), max_length=255, blank=True, null=True)

    main_destination_heading = models.CharField(_('Main Destination Heading'), max_length=255, blank=True, null=True)
    main_destination_description = models.TextField(_('Main Destination Description'), blank=True, null=True)
    destination_highlight_description = models.TextField(_('Destination Highlight Description'), blank=True, null=True)

    latitude = models.DecimalField(_('Latitude'), max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(_('Longitude'), max_digits=9, decimal_places=6, blank=True, null=True)
    map_link = models.URLField(_('Map Link'), blank=True, null=True)
    highlight_heading = models.CharField(_('Highlight Heading'), max_length=255, blank=True, null=True)

    highlight_description = models.TextField(_('Highlight Description'), blank=True, null=True)

    best_visit_time = models.TextField(_('Best Time to Visit'), blank=True, null=True)
    avg_cost = models.DecimalField(_('Average Cost'), max_digits=10, decimal_places=2, blank=True, null=True)
    activities = models.ForeignKey(Activity, on_delete=models.SET_NULL, related_name='destinations', blank=True, null=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    order = models.PositiveIntegerField(_('Order'), default=0)
    weather = models.URLField(_('Weather'), blank=True, null=True)
    currency = models.CharField(_('Currency'), max_length=255, blank=True, null=True)
    travel_type = models.CharField(_('Travel Type'), max_length=255, choices=TravelType.choices, blank=True, null=True)
    
    kind_of_destination = models.CharField(max_length=255,choices=DESTINATION_TYPE,blank=True, null=True)




    class Meta:
        verbose_name = "Destination"
        verbose_name_plural = "Destinations"

    def __str__(self):
        return f"{self.main_destination_city or 'Unnamed Destination'}"
    

class DestiantionFeatures(AbstractDateFieldMix):
    destination = models.OneToOneField(Destination,on_delete=models.SET_NULL,blank=True, null=True)
    image = models.ImageField(upload_to='destinations/feature/',blank=True, null=True)
    heading = models.CharField(max_length=255,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(_('Latitude'), max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(_('Longitude'), max_digits=9, decimal_places=6, blank=True, null=True)
    map_link = models.URLField(_('Map Link'), blank=True, null=True)


    def __str__(self):
        return self.destination
