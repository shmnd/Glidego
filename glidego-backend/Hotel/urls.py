from django.urls import path, re_path, include
from Hotel.views import BranchListAPIView, HotelCreateAPIView, HotelListAPIView, RoomCreateAPIView, HotelAdminCreateAPIView, HotelStatusChangeAPIView



urlpatterns=[

    path('hotels/', HotelCreateAPIView.as_view(), name='hotel-create'),
    path('rooms/', RoomCreateAPIView.as_view(), name='room-create'),
    path('branches/', BranchListAPIView.as_view(), name='branch-list'),
    path('hotels/list/', HotelListAPIView.as_view(), name='hotel-list'),
  

    re_path(r'^Hotel-Admin/', include([
        path('hotel-admin-creation', HotelAdminCreateAPIView.as_view()),
    ])),

    re_path(r'^Hotel-Status/', include([
        path('hotel-status-change', HotelStatusChangeAPIView.as_view()),
    ])),

]