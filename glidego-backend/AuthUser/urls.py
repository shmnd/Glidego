from django.urls import path  
from .views import LoginView, StaffCreateAPIView


urlpatterns=[
  path('login/', LoginView.as_view(), name='login'),
  path('staff/create/', StaffCreateAPIView.as_view(), name='staff-create'),

]
