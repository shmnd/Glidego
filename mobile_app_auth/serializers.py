from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PhoneOTP
from django.contrib.auth import authenticate
UserAccount = get_user_model()


# Serializer for sending OTP
class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        # You can add regex validation for phone numbers if needed
        if not value.startswith("+"):
            raise serializers.ValidationError("Phone number must include country code (e.g., +91).")
        return value


# Serializer for verifying OTP
class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)

    # def validate(self, data):
    #     phone = data.get("phone")
    #     otp = data.get("otp")

        # try:
        #     record = PhoneOTP.objects.get(phone=phone)
        # except PhoneOTP.DoesNotExist:
        #     raise serializers.ValidationError({"phone": "Phone number not found."})

        # if record.is_expired():
        #     raise serializers.ValidationError({"otp": "OTP expired."})

        # if record.otp != otp:
        #     raise serializers.ValidationError({"otp": "Invalid OTP."})

        # return data


# Serializer for creating profile
class CreateProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserAccount
        fields = ["phone_number", "username", "email", "password"]

    def create(self, validated_data):
        user = UserAccount.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            phone_number=validated_data["phone_number"],
            password=validated_data["password"]
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username :
            raise serializers.ValidationError("Either username or email is required")

        
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid login credentials")

        data["user"] = user
        return data
