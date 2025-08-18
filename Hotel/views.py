from django.http import Http404
from requests import request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission,AllowAny
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import NotFound
import logging
from drf_yasg.utils import swagger_auto_schema
from helpers.helper import get_object_or_none, IsSuperUser

from .models import Branch, HotelAdmin, Hotels, Room
from glidego.permissions import  has_permission
from .serializers import BranchSerializer, HotelAdminCreateSerializer, HotelAdminListSerializer, HotelAdminUpdateSerializer, HotelSerializer, HotelVerificationSerializer, RoomSerializer
from django.contrib.auth import get_user_model

UserAccount = get_user_model()
logger = logging.getLogger(__name__)

class BranchListAPIView(APIView):
    permission_classes = [AllowAny]

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
    

# Add to views.py

class BranchCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('add_branch', 'Hotel')]

    def post(self, request):
        serializer = BranchSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            branch = serializer.save()
            return Response({"message": "Branch created successfully", "id": branch.id}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class BranchDetailAPIView(APIView):
    permission_classes = [AllowAny, has_permission('view_branch', 'Hotel')]

    def get(self, request, pk):
        try:
            branch = get_object_or_404(Branch, pk=pk)
        except Http404:
            raise NotFound(detail="Branch not found.")
        serializer = BranchSerializer(branch)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BranchUpdateAPIView(APIView):
    permission_classes = [AllowAny, has_permission('change_branch', 'Hotel')]

    def put(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        serializer = BranchSerializer(branch, data=request.data, context={'request': request})
        if serializer.is_valid():
            branch = serializer.save()
            serializer = BranchSerializer(branch, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        serializer = BranchSerializer(branch, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            branch = serializer.save()
            serializer = BranchSerializer(branch, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class BranchDeleteAPIView(APIView):
    permission_classes = [AllowAny, has_permission('delete_branch', 'Hotel')]

    def delete(self, request, pk):
        try:
            branch = get_object_or_404(Branch, pk=pk)
            # Associated hotels will have branch set to null due to on_delete=SET_NULL
            branch.delete()
            return Response({"message": "Branch deleted successfully"}, status=status.HTTP_200_OK)
        except Http404:
            raise NotFound(detail="Branch not found.")
        except Exception as e:
            return Response({"error": f"Failed to delete branch: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class HotelCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('add_hotels', 'Hotel')]

    def post(self, request):
        serializer = HotelSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            hotel = serializer.save()
            return Response({"message": "Hotel created successfully", "id": hotel.id}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class HotelListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hotels = Hotels.objects.all()
        if not hotels.exists():
            return Response({"message": "No hotels found"}, status=status.HTTP_200_OK)
        serializer = HotelSerializer(hotels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class HotelDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('view_hotels', 'Hotel')]

    def get(self, request, pk):
        try:
            hotel = get_object_or_404(Hotels, pk=pk)
        except Http404:
            # Return JSON instead of HTML error page
            raise NotFound(detail="Hotel not found.")

        serializer = HotelSerializer(hotel)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HotelUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('change_hotels', 'Hotel')]

    def put(self, request, pk):
        hotel = get_object_or_404(Hotels, pk=pk)
        serializer = HotelSerializer(hotel, data=request.data, context={'request': request})
        if serializer.is_valid():
            hotel = serializer.save()
            serializer = HotelSerializer(hotel, context={'request': request})  # Serialize updated instance
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        hotel = get_object_or_404(Hotels, pk=pk)
        serializer = HotelSerializer(hotel, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            hotel = serializer.save()
            serializer = HotelSerializer(hotel, context={'request': request})  # Serialize updated instance
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class HotelDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('delete_hotels', 'Hotel')]

    def delete(self, request, pk):
        try:
            hotel = get_object_or_404(Hotels, pk=pk)
            # Delete associated hotel images
            hotel.hotel_images.all().delete()
            # Optionally delete associated rooms (cascade might handle this depending on your model)
            Room.objects.filter(hotel=hotel).delete()
            hotel.delete()
            return Response({"message": "Hotel deleted successfully"}, status=status.HTTP_200_OK)
        except Http404:
            raise NotFound(detail="Hotel not found.")
        except Exception as e:
            return Response({"error": f"Failed to delete hotel: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class RoomCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('add_room', 'Hotel')]

    def post(self, request):
        serializer = RoomSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            room = serializer.save()
            return Response({"message": "Room created successfully", "id": room.id}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class RoomListAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('view_room', 'Hotel')]

    def get(self, request):
        rooms = Room.objects.all()
        if not rooms.exists():
            return Response({"message": "No rooms found"}, status=status.HTTP_200_OK)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RoomDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('view_room', 'Hotel')]

    def get(self, request, pk):
        try:
            room = get_object_or_404(Room, pk=pk)
        except Http404:
            raise NotFound(detail="Room not found.")
        
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RoomUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('change_room', 'Hotel')]

    def put(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        serializer = RoomSerializer(room, data=request.data, context={'request': request})
        if serializer.is_valid():
            room = serializer.save()
            serializer = RoomSerializer(room, context={'request': request})  # Serialize updated instance
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        serializer = RoomSerializer(room, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            room = serializer.save()
            serializer = RoomSerializer(room, context={'request': request})  # Serialize updated instance
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class RoomDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, has_permission('delete_room', 'Hotel')]

    def delete(self, request, pk):
        try:
            room = get_object_or_404(Room, pk=pk)
            # Delete associated room images
            room.room_images.all().delete()
            room.delete()
            return Response({"message": "Room deleted successfully"}, status=status.HTTP_200_OK)
        except Http404:
            raise NotFound(detail="Room not found.")
        except Exception as e:
            return Response({"error": f"Failed to delete room: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        





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
        

        
UserAccount = get_user_model()
logger = logging.getLogger(__name__)

class HasAddHotelAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('Hotel.add_hoteladmin')

class HasViewHotelAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('Hotel.view_hoteladmin')

class HasChangeHotelAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('Hotel.change_hoteladmin')

class HotelAdminCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, HasAddHotelAdminPermission]
    
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
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HotelAdminListAPIView(APIView):
    permission_classes = [IsAuthenticated, HasViewHotelAdminPermission]
    
    def get(self, request, *args, **kwargs):
        try:
            hotel_admins = HotelAdmin.objects.all()
            if not hotel_admins.exists():
                return Response({"message": "No hotel admins found"}, status=status.HTTP_200_OK)
            serializer = HotelAdminListSerializer(hotel_admins, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Error listing Hotel Admins")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HotelAdminUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, HasChangeHotelAdminPermission]
    
    def patch(self, request, pk, *args, **kwargs):
        try:
            hotel_admin = HotelAdmin.objects.get(pk=pk)
            serializer = HotelAdminUpdateSerializer(hotel_admin, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Hotel Admin updated successfully"},
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except HotelAdmin.DoesNotExist:
            return Response({"error": "Hotel Admin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Error updating Hotel Admin {pk}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HotelAdminDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.has_perm('Hotel.view_hoteladmin')
        elif request.method == 'DELETE':
            return request.user.has_perm('Hotel.delete_hoteladmin')
        return False

    def get(self, request, pk, *args, **kwargs):
        try:
            hotel_admin = HotelAdmin.objects.get(pk=pk)
            serializer = HotelAdminListSerializer(hotel_admin)
            logger.info(f"Retrieved details for Hotel Admin {pk}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except HotelAdmin.DoesNotExist:
            logger.warning(f"Hotel Admin {pk} not found")
            return Response({"error": "Hotel Admin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Error retrieving Hotel Admin {pk}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk, *args, **kwargs):
        try:
            hotel_admin = HotelAdmin.objects.get(pk=pk)
            hotel_admin.delete()
            logger.info(f"Hotel Admin {pk} deleted successfully")
            return Response({"message": "Hotel Admin deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except HotelAdmin.DoesNotExist:
            logger.warning(f"Hotel Admin {pk} not found")
            return Response({"error": "Hotel Admin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Error deleting Hotel Admin {pk}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class HotelPublicListAPIView(APIView):
    """
    Public API to list all verified hotels (is_verified=True).
    No authentication or permissions required.
    """
    permission_classes = []
    def get(self, request):
        hotels = Hotels.objects.filter(is_verified=True)
        if not hotels.exists():
            return Response({"message": "No verified hotels found"}, status=status.HTTP_200_OK)
        serializer = HotelSerializer(hotels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HotelPublicDetailAPIView(APIView):
    """
    Public API to retrieve details of a specific verified hotel (is_verified=True).
    No authentication or permissions required.
    """
    permission_classes = []
    def get(self, request, pk):
        try:
            hotel = get_object_or_404(Hotels, pk=pk, is_verified=True)
            serializer = HotelSerializer(hotel)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            raise NotFound(detail="Verified hotel not found.")
        


class HotelVerificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, *args, **kwargs):
        try:
            instance = Hotels.objects.filter(pk=id).first()
            if not instance:
                return Response(
                    {"error": "Hotel not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = HotelVerificationSerializer(instance, data={'id': id, 'is_verified': True}, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Hotel verified successfully"},
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Error verifying hotel")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )