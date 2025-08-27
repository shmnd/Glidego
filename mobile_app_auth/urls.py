from django.urls import path,re_path,include
from .views import SendOTPView, VerifyOTPView, CreateProfileView, LoginView


urlpatterns=[
  re_path(r'^Mobile-App-Authentication/', include([
        path("send-otp/", SendOTPView.as_view(), name="send-otp"),           
        path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),     
        path("create-profile/", CreateProfileView.as_view(), name="create-profile"),
        path("login/", LoginView.as_view(), name="login"),  
    ])),

]
