from django.urls import path,re_path,include
from .views import LoginView, StaffCreateAPIView, StaffDeleteAPIView, StaffDetailAPIView, StaffListAPIView, StaffUpdateAPIView,CreateOrUpdateCustomerApiView


urlpatterns=[
  path('login/', LoginView.as_view(), name='login'),
  path('staff/create/', StaffCreateAPIView.as_view(), name='staff-create'),
  path('staff/', StaffListAPIView.as_view(), name='staff-list'),
  path('staff/<int:id>/', StaffDetailAPIView.as_view(), name='staff-detail'),
  path('staff/<int:id>/update/', StaffUpdateAPIView.as_view(), name='staff-update'),
  path('staff/<int:id>/delete/', StaffDeleteAPIView.as_view(), name='staff-delete'),

  re_path(r'^Custmer-login/', include([
    path('create-or-update-user', CreateOrUpdateCustomerApiView.as_view()),
  ])),
]
