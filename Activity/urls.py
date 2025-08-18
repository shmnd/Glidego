from django.urls import path
from . import views

urlpatterns = [
    path('activities/', views.list_activities, name='list_activities'),
    path('activities/<int:pk>/', views.ActivityDetailAPIView.as_view(), name='list-activity'),
    path('activities/create/', views.create_activity, name='create_activity'),
    path('activities/<int:pk>/update/', views.update_activity, name='update_activity'),
    path('activities/<int:pk>/delete/', views.delete_activity, name='delete_activity'),
]
