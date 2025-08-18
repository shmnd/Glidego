from .views import CabAdminCreateAPIView, CabCategoryDeleteView, DriverDetailView, DriverUpdateView
from django.urls import path

from . import views
from .views import (
    DriverListCreateView, DriverRetrieveUpdateDestroyView,
    VehicleListCreateView, VehicleRetrieveUpdateDestroyView,
    CabCategoryListCreateView, CabCategoryRetrieveUpdateDestroyView,
    CabStatusChangeAPIView, DriverStatusChangeAPIView, VehicleStatusChangeAPIView
    , CabAdminListAPIView, CabAdminRetrieveAPIView, CabAdminDeleteAPIView
)

urlpatterns = [
    path('cab-admin/create/', CabAdminCreateAPIView.as_view(), name='cab-admin-create'),
    path('cab-admin/', CabAdminListAPIView.as_view(), name='cab-admin-list'),
    path('cab-admin/<int:pk>/', CabAdminRetrieveAPIView.as_view(), name='cab-admin-detail'),
    path('cab-admin/<int:pk>/delete/', CabAdminDeleteAPIView.as_view(), name='cab-admin-delete'),

    # Approve CabAdmin
    path('cab-admin/<int:pk>/approve/', views.CabAdminApproveAPIView, name='cab-admin-approve'),
    path('cabs/', views.list_cabs, name='list_cabs'),
    path('cabs/create/', views.create_cab, name='create_cab'),
    path('cabs/<int:pk>/', views.get_cab, name='get_cab'),
    path('cabs/<int:pk>/update/', views.update_cab, name='update_cab'),
    path('cabs/<int:pk>/delete/', views.delete_cab, name='delete_cab'),
    path('vehicle/<int:pk>/delete/', views.delete_Vehicle, name='delete_cab'),

    path('vehicles/', VehicleListCreateView.as_view(), name='vehicle-list-create'),
    path('vehicles/<int:pk>/', VehicleRetrieveUpdateDestroyView.as_view(), name='vehicle-detail'),

    path('api/drivers/', DriverListCreateView.as_view(), name='driver-list-create'),
    path('api/drivers/<int:pk>/', DriverUpdateView.as_view(), name='driver-update'),
    path('drivers/<int:id>/', DriverDetailView.as_view(), name='driver-detail'),

    path('cab-categories/', CabCategoryListCreateView.as_view(), name='cabcategory-list-create'),
    path('cab-categories/<int:pk>/', CabCategoryRetrieveUpdateDestroyView.as_view(), name='cabcategory-detail'),

    path('cab-categories/<int:pk>/delete/', CabCategoryDeleteView.as_view(), name='cab-category-delete'),

    path('Status_change/cab-status-change/', CabStatusChangeAPIView.as_view()),
    path('Status_change/driver-status-change/', DriverStatusChangeAPIView.as_view()),
    path('Status_change/vehicle-status-change/', VehicleStatusChangeAPIView.as_view()),
]
