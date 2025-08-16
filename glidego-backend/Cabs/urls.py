from django.urls import path, re_path, include
from .views import CabAdminCreateAPIView,CabStatusChangeAPIView,VehicleStatusChangeAPIView,DriverStatusChangeAPIView





urlpatterns=[

    path('cab-admin/create/', CabAdminCreateAPIView.as_view(), name='cab-admin-create'),

  

    re_path(r'^Status_change/', include([
        path('cab-status-change', CabStatusChangeAPIView.as_view()),
        path('driver-status-change', DriverStatusChangeAPIView.as_view()),
        path('vehicle-status-change', VehicleStatusChangeAPIView.as_view()),

    ])),

]