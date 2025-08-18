from django.db import models

class TripPlan(models.Model):
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    intermediate_locations = models.JSONField()  # list of dicts: [{name, lat, lng}]
    selected_hotels = models.JSONField()         # list of hotel names per location
    cab_type = models.CharField(max_length=100)
    total_price = models.PositiveIntegerField()
    trip_days = models.PositiveIntegerField()
    polyline = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    cab_price = models.PositiveIntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.start_location} → {self.end_location}"
