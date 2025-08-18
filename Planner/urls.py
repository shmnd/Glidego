from django.urls import path
from .views import TravelPlanAPIView


urlpatterns=[
    path("travel-plans/", TravelPlanAPIView.as_view(), name="travel-plans"),
]