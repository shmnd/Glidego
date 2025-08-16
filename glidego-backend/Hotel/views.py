from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Branch, Hotels
from glidego.permissions import  has_permission
from .serializers import BranchSerializer, HotelSerializer, RoomSerializer,HotelAdminCreateSerializer
from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated, BasePermission
from drf_yasg.utils import swagger_auto_schema
from helpers.helper import get_object_or_none,IsSuperUser

import logging
logger = logging.getLogger(__name__)

UserAccount = get_user_model()

class BranchListAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('view_branch', 'Hotel')]

    def get(self, request):
        branches = Branch.objects.all()
        if not branches.exists():
            # Create or get Main Branch as fallback
            main_branch, created = Branch.objects.get_or_create(
                name="Main Branch",
                defaults={'location': "Default Location", 'is_active': True}
            )
            branches = [main_branch]
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class HotelCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('add_hotels', 'Hotel')]

    def post(self, request):
        serializer = HotelSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            hotel = serializer.save()
            return Response({"message": "Hotel created successfully", "id": hotel.id}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class RoomCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('add_room', 'Hotel')]

    def post(self, request):
        serializer = RoomSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            room = serializer.save()
            return Response({"message": "Room created successfully", "id": room.id}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class HotelListAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('view_hotel', 'Hotel')]

    def get(self, request):
        hotels = Hotels.objects.all()
        if not hotels.exists():
            return Response({"message": "No hotels found"}, status=status.HTTP_200_OK)
        serializer = HotelSerializer(hotels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    




# Custom permission to check if user can add CabAdmin
class HasAddCabAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('Hotel.add_hoteladmin')  # app_label.modelname lowercase


class HotelAdminCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, HasAddCabAdminPermission]
    @swagger_auto_schema(tags=['Hotel-Admin'], request_body=HotelAdminCreateSerializer)
    def post(self, request, *args, **kwargs):
        try:
            serializer = HotelAdminCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Hotel Admin created successfully"},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Error creating Hotel Admin")
            return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


# status changing 
class HotelStatusChangeAPIView(APIView):
    permission_classes = [IsSuperUser,]
    @swagger_auto_schema(tags=['Hotel-Status'], request_body=HotelSerializer)
    def post(self, request, *args, **kwargs):
        try:    
            instance    = get_object_or_none(Hotels,pk=request.data.get('id',None))
            serializer = HotelSerializer(instance,data=request.data,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Hotel Status Changed successfully"},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Error Changing Hotel Status")
            return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)