from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from helpers.helper import get_object_or_none
from .serializers import StaffCreateSerializer, StaffDetailSerializer,CreateOrUpdateCustomerSerializer
import logging


# Create your views here.

UserAccount = get_user_model()
logger = logging.getLogger(__name__)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        user = UserAccount.objects.filter(email=email).first()

        if user and user.check_password(password):
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Add custom claims to the refresh token
            refresh["username"] = user.username
            refresh["email"] = user.email
            
            # Fetch user permissions
            permissions = [perm.codename for perm in user.user_permissions.all()]
            logger.debug(f"User {user.email} permissions: {permissions}")

            # Include permissions in access token if needed
            refresh.access_token["permissions"] = permissions

            response_data = {
                'message': 'Login successful!',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'permissions': permissions,  # Explicitly include permissions in response
                'username': user.username,
                'email': user.email,
            }

            logger.info(f"User {user.email} logged in successfully")
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Failed login attempt for email: {email}")
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)        

UserAccount = get_user_model()

class HasAddUserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('users.add_user')
    
class HasViewUserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('users.view_user')

class HasChangeUserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('users.change_user')

class HasDeleteUserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('users.delete_user')
    


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
    

# ---- LIST STAFF ----
class StaffListAPIView(generics.ListAPIView):
    serializer_class = StaffDetailSerializer
    permission_classes = [IsAuthenticated, HasViewUserPermission]
    pagination_class = None

    def get_queryset(self):
        return UserAccount.objects.filter(is_superuser= False)


# ---- STAFF DETAIL ----
class StaffDetailAPIView(generics.RetrieveAPIView):
    serializer_class = StaffDetailSerializer
    permission_classes = [IsAuthenticated, HasViewUserPermission]
    pagination_class = None
    lookup_field = "id"

    def get_queryset(self):
        return UserAccount.objects.filter(is_superuser=False)


# ---- UPDATE STAFF ----
class StaffUpdateAPIView(generics.UpdateAPIView):
    serializer_class = StaffCreateSerializer  # reuse create serializer
    permission_classes = [IsAuthenticated, HasChangeUserPermission]
    pagination_class = None
    lookup_field = "id"

    def get_queryset(self):
        return UserAccount.objects.filter(is_superuser=False)


# ---- DELETE STAFF ----
class StaffDeleteAPIView(generics.DestroyAPIView):
    serializer_class = StaffDetailSerializer
    permission_classes = [IsAuthenticated, HasDeleteUserPermission]
    pagination_class = None
    lookup_field = "id"

    def get_queryset(self):
        return UserAccount.objects.filter(is_superuser=False)
    


# shamnad code
class CreateOrUpdateCustomerApiView(generics.GenericAPIView):

    serializer_class = CreateOrUpdateCustomerSerializer
    # permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:

            user_instance = get_object_or_none(UserAccount, pk=request.data.get('user'))
            print(user_instance,'aaaaaaaaaaaaaaaaaaaaaaa')

            # serializer = self.serializer_class(data=request.data, context = {'request' : request})
            # if not serializer.is_valid():
            #     return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            # user_instance = get_object_or_none(UserAccount,pk=serializer.validated_data.get('user', None))

            serializer = self.serializer_class(user_instance, data=request.data, context = {'request' : request})
            
            if not serializer.is_valid():
                return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response({'data':serializer.data,'message':'Succes'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error':{str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 