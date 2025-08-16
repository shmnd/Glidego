from django.urls import path, re_path, include
from .views import DestinationListCreateAPIView, DestinationRetrieveUpdateDestroyAPIView,DestinationStatusChangeAPIView

urlpatterns = [
    path('destinations/', DestinationListCreateAPIView.as_view(), name='destination-list-create'),
    path('destinations/<int:pk>/', DestinationRetrieveUpdateDestroyAPIView.as_view(), name='destination-detail'),
    path('destinations/<int:pk>/delete/', DestinationRetrieveUpdateDestroyAPIView.as_view(), name='destination-delete'),



    re_path(r'^Destination-Status/', include([
        path('destination-status-change', DestinationStatusChangeAPIView.as_view()),
    ])),

]