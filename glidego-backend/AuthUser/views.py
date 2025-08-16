from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission

from .serializers import StaffCreateSerializer



# Create your views here.

UserAccount = get_user_model()


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        user = UserAccount.objects.filter(email=email).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            
            # Add custom claims to the access token
            refresh["username"] = user.username
            refresh["email"] = user.email
            refresh["permissions"] = [perm.codename for perm in user.user_permissions.all()]

            # Detect if user is CabAdmin
            refresh["is_cabadmin"] = hasattr(user, "cabadmin_profile")

            access_token = str(refresh.access_token)

            response_data = {
                'message': 'Login successful!',
                'access_token': access_token,
                'refresh_token': str(refresh),
                'permissions': [perm.codename for perm in user.user_permissions.all()],
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        

UserAccount = get_user_model()

class HasAddUserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('users.add_user')

class StaffCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, HasAddUserPermission]

    def post(self, request, *args, **kwargs):
        serializer = StaffCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Staff created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )