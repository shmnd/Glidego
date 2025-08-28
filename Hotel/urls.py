
from django.urls import include, path, re_path
from Hotel.views import (
    BranchCreateAPIView, BranchDeleteAPIView, BranchDetailAPIView, BranchListAPIView, BranchUpdateAPIView,
    HotelAdminCreateAPIView, HotelAdminDetailAPIView, HotelAdminListAPIView, HotelAdminUpdateAPIView,
    HotelCreateAPIView, HotelDeleteAPIView, HotelDetailAPIView, HotelListAPIView, HotelStatusChangeAPIView,
    HotelUpdateAPIView, HotelVerificationAPIView, RoomCreateAPIView, RoomDeleteAPIView, RoomDetailAPIView, RoomListAPIView, RoomUpdateAPIView,
    HotelPublicListAPIView, HotelPublicDetailAPIView, GetHotelsListApiView  # Add new views
)

urlpatterns = [
    path('branches/', BranchListAPIView.as_view(), name='branch-list'),
    path('branches/create/', BranchCreateAPIView.as_view(), name='branch-create'),
    path('branches/<int:pk>/', BranchDetailAPIView.as_view(), name='branch-detail'),
    path('branches/<int:pk>/edit/', BranchUpdateAPIView.as_view(), name='branch-update'),
    path('branches/<int:pk>/delete/', BranchDeleteAPIView.as_view(), name='branch-delete'),
    
    path('hotels/', HotelCreateAPIView.as_view(), name='hotel-create'),
    path('hotels/list/', HotelListAPIView.as_view(), name='hotel-list'),
    path('hotels/<int:pk>/', HotelDetailAPIView.as_view(), name='hotel-detail'),
    path('hotels/<int:pk>/edit/', HotelUpdateAPIView.as_view(), name='hotel-update'),
    path('hotels/<int:pk>/delete/', HotelDeleteAPIView.as_view(), name='hotel-delete'),
    
    path('public/hotels/', HotelPublicListAPIView.as_view(), name='hotel-public-list'),
    path('public/hotels/<int:pk>/', HotelPublicDetailAPIView.as_view(), name='hotel-public-detail'),
    
    path('rooms/', RoomCreateAPIView.as_view(), name='room-create'),
    path('rooms/list/', RoomListAPIView.as_view(), name='room-list'),
    path('rooms/<int:pk>/', RoomDetailAPIView.as_view(), name='room-detail'),
    path('rooms/<int:pk>/edit/', RoomUpdateAPIView.as_view(), name='room-update'),
    path('rooms/<int:pk>/delete/', RoomDeleteAPIView.as_view(), name='room-delete'),
    
    path('status-change/<int:id>/', HotelStatusChangeAPIView.as_view(), name='hotel-status-change'),

        path('verification/<int:id>/', HotelVerificationAPIView.as_view(), name='hotel-verification'),
    
    path('hotel-admin-creation/', HotelAdminCreateAPIView.as_view(), name='hotel-admin-create'),
    path('hotel-admin-list/', HotelAdminListAPIView.as_view(), name='hotel-admin-list'),
    path('hotel-admin-update/<int:pk>/', HotelAdminUpdateAPIView.as_view(), name='hotel-admin-update'),
    path('hotel-admin-detail/<int:pk>/', HotelAdminDetailAPIView.as_view(), name='hotel-admin-detail'),

    re_path(r'^Hotel-detail-place/', include([
        path('list-hotel', GetHotelsListApiView.as_view()),

     ])),
    # stafff
    # path('hotel-staff-creation/', HotelStaffCreateAPIView.as_view(), name='hotel-staff-create'),

]
