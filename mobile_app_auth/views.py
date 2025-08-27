# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import PhoneOTP
from django.db import models
from twilio.rest import Client
from django.conf import settings
from .serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    CreateProfileSerializer,
    LoginSerializer
)

from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
# to login with email and username

UserAccount = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None 

        try:
            # check if login input is email or username
            if "@" in username:
                user = UserAccount.objects.get(email=username) 
            else:
                user = UserAccount.objects.get(username=username) 
        except UserAccount.DoesNotExist: 
            return None

        if user.check_password(password):
            return user
        return None
    


class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            otp = PhoneOTP.generate_otp()

            PhoneOTP.objects.update_or_create(
                phone=phone,
                defaults={"otp": otp}
            )

            client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
            twilio_number = settings.TWILIO_NUMBER

            if not settings.ACCOUNT_SID or not settings.AUTH_TOKEN or not twilio_number:
                return Response({"status": False, "error": "Twilio credentials are missing"}, status=500)
            
            
            try:
                message = client.messages.create(
                    body=f"Your OTP for Glidego {otp}",
                    from_=twilio_number,
                    to=phone
                )
                return Response({
                    "status": True,
                    "message": "OTP sent successfully",
                    "sid": message.sid,
                    "twilio_status": message.status
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"status": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"status": False, "error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            otp = serializer.validated_data['otp']

            try:
                phone_otp = PhoneOTP.objects.get(phone=phone)
                if phone_otp.otp == otp:
                    return Response({"status":True, "message": "OTP verified successfully"}, status=status.HTTP_200_OK)
                
                return Response({"status":False, "message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
            except PhoneOTP.DoesNotExist:
                return Response({"status":False, "message": "Phone number not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CreateProfileView(APIView):
    def post(self, request):
        serializer = CreateProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": True,"message": "Profile created successfully. Please login."},
                status=status.HTTP_201_CREATED
            )

        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"] 

            refresh = RefreshToken.for_user(user)
            return Response({
                "status": True,   # ✅ success
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": "Login successful"
            }, status=status.HTTP_200_OK)

        return Response({
            "status": False,
            "errors": serializer.errors,
            "message": "Invalid credentials"
        }, status=status.HTTP_400_BAD_REQUEST)
