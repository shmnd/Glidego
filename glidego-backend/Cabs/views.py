
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from .models import Cab,Vehicle,Driver
from .serializers import CabAdminCreateSerializer,VehicleStautsSerializer,CabStautsSerializer,DriverStautsSerializer
from helpers.helper import get_object_or_none,IsSuperUser
import logging
logger = logging.getLogger(__name__)

# Custom permission to check if user can add CabAdmin
class HasAddCabAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('Cabs.add_cabadmin')  # app_label.modelname lowercase


class CabAdminCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, HasAddCabAdminPermission]
    @swagger_auto_schema(request_body=CabAdminCreateSerializer)
    def post(self, request, *args, **kwargs):
        serializer = CabAdminCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "CabAdmin created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )



# Cab status changing 
class CabStatusChangeAPIView(APIView):
    permission_classes = [IsSuperUser,]
    @swagger_auto_schema(tags=['Cab-Status'], request_body=CabStautsSerializer)
    def post(self, request, *args, **kwargs):
        try:
            instance    = get_object_or_none(Cab,pk=request.data.get('id',None))
            serializer = CabStautsSerializer(instance,data=request.data,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Cab Status Changed successfully"},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Error Changing Cab Status")
            return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# Vehicle status changing 
class VehicleStatusChangeAPIView(APIView):
    permission_classes = [IsSuperUser]
    @swagger_auto_schema(tags=['Vehicle-Status'], request_body=VehicleStautsSerializer)
    def post(self, request, *args, **kwargs):
        try:
            instance    = get_object_or_none(Vehicle,pk=request.data.get('id',None))
            serializer = VehicleStautsSerializer(instance,data=request.data,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Vehicle Status Changed successfully"},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Error Changing Vehicle Status")
            return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


# Driver status changing 
    
class DriverStatusChangeAPIView(APIView):
    permission_classes = [IsSuperUser,]
    @swagger_auto_schema(tags=['Driver-Status'], request_body=DriverStautsSerializer)
    def post(self, request, *args, **kwargs):
        try:
            instance    = get_object_or_none(Driver,pk=request.data.get('id',None))
            serializer = DriverStautsSerializer(instance,data=request.data,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Driver Status Changed successfully"},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Error Changing Driver Status")
            return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)