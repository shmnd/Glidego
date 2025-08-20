from django.urls import path#, re_path, include
from .views import ActivityListAPIView, DestinationDeleteAPIView, DestinationDetailAPIView, DestinationListCrAPIView, DestinationListCreateAPIView, DestinationListCreatePublicAPIView

urlpatterns = [
    # re_path(r'^Destination-create/', include([
        path('destinations/', DestinationListCreateAPIView.as_view(), name='destination-list-create'),
    # ])),

    # re_path(r'^Destination/', include([
        path('destinations/client/', DestinationListCrAPIView.as_view(), name='destination-list-create'),

        path('destinations/public/', DestinationListCreatePublicAPIView.as_view(), name='destination-list-create'),
        path('activities/', ActivityListAPIView.as_view(), name='activity-list'),
        path('destinations/<int:pk>/', DestinationDetailAPIView.as_view(), name='destination-detail'),
        path('destinations/<int:pk>/delete/', DestinationDeleteAPIView.as_view(), name='destination-delete'),
    # ])),
    # path('destinations/<int:pk>/', DestinationRetrieveUpdateDestroyAPIView.as_view(), name='destination-detail'),
    # path('destinations/<int:pk>/delete/', DestinationRetrieveUpdateDestroyAPIView.as_view(), name='destination-delete'),
]
