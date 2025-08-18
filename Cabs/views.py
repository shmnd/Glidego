from .models import CabAdmin
from .serializers import CabAdminCreateSerializer

# CabAdmin creation API view (AllowAny)
from rest_framework.permissions import AllowAny
from .serializers import CabAdminCreateSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics

# Approve a CabAdmin (set status to 'approved')
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status as drf_status

from .models import CabCategory
from .serializers import CabCategorySerializer

from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Cab
from .serializers import CabSerializer
from rest_framework import generics
from .models import Vehicle, Driver
from .serializers import VehicleSerializer, DriverSerializer
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import IntegrityError
from rest_framework.exceptions import ValidationError

import logging


logger = logging.getLogger(__name__)


class CabAdminCreateAPIView(APIView):
    permission_classes = [AllowAny]  # Change to IsAuthenticated, HasAddCabAdminPermission for restricted access

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

# List all CabAdmins
class CabAdminListAPIView(generics.ListAPIView):
    queryset = CabAdmin.objects.all()
    serializer_class = CabAdminCreateSerializer
    permission_classes = [AllowAny]

# Retrieve a single CabAdmin
class CabAdminRetrieveAPIView(generics.RetrieveAPIView):
    queryset = CabAdmin.objects.all()
    serializer_class = CabAdminCreateSerializer
    permission_classes = [AllowAny]

# Delete a CabAdmin
class CabAdminDeleteAPIView(generics.DestroyAPIView):
    queryset = CabAdmin.objects.all()
    serializer_class = CabAdminCreateSerializer



@api_view(["POST"])
@permission_classes([AllowAny])
def CabAdminApproveAPIView(request, pk):
    try:
        cab_admin = CabAdmin.objects.get(pk=pk)
    except CabAdmin.DoesNotExist:
        return Response({"error": "CabAdmin not found"}, status=drf_status.HTTP_404_NOT_FOUND)
    cab_admin.status = "approved"
    cab_admin.save()
    return Response({"message": "CabAdmin approved successfully"}, status=drf_status.HTTP_200_OK)
    



class VehicleListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]

    permission_classes
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    from rest_framework.permissions import AllowAny
    

class VehicleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)


# DRIVER CRUD
class DriverListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Driver.objects.all().order_by('id')
    serializer_class = DriverSerializer

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError as e:
            logger.error(f"IntegrityError during driver creation: {e}")
            if "UNIQUE constraint failed" in str(e):
                field = str(e).split('.')[-1]
                raise ValidationError({field: f"This {field.replace('_', ' ')} is already in use"})
            raise ValidationError({"non_field_errors": "Failed to create driver due to database error"})
        
class DriverDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    lookup_field = 'id'

    def perform_update(self, serializer):
        try:
            serializer.save()
        except IntegrityError as e:
            logger.error(f"IntegrityError during driver update: {e}")
            if "UNIQUE constraint failed" in str(e):
                field = str(e).split('.')[-1]
                raise ValidationError({field: f"This {field.replace('_', ' ')} is already in use"})
            raise ValidationError({"non_field_errors": "Failed to update driver due to database error"})

class DriverUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    def perform_update(self, serializer):
        try:
            serializer.save()
        except IntegrityError as e:
            logger.error(f"IntegrityError during driver update: {e}")
            if "UNIQUE constraint failed" in str(e):
                field = str(e).split('.')[-1]
                raise ValidationError({field: f"This {field.replace('_', ' ')} is already in use"})
            raise ValidationError({"non_field_errors": "Failed to update driver due to database error"})
    

class DriverRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Driver.objects.all().order_by('id')
    serializer_class = DriverSerializer

# CAB CATEGORY CRUD
from .models import CabCategory
from .serializers import CabCategorySerializer

class CabCategoryListCreateView(generics.ListCreateAPIView):
    permission_classes=[AllowAny]

    queryset = CabCategory.objects.all()
    serializer_class = CabCategorySerializer
    from rest_framework.permissions import AllowAny
    permission_classes = [AllowAny]

class CabCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=[AllowAny]
    queryset = CabCategory.objects.all()
    serializer_class = CabCategorySerializer

# CREATE Cab
@api_view(['POST'])
@permission_classes([AllowAny])
def create_cab(request):
    serializer = CabSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# READ all Cabs
@api_view(['GET'])
@permission_classes([AllowAny])
def list_cabs(request):

    cabs = Cab.objects.all()
    serializer = CabSerializer(cabs, many=True)
    return Response(serializer.data)


# READ single Cab
@api_view(['GET'])
@permission_classes([AllowAny])
def get_cab(request, pk):
    try:
        cab = Cab.objects.get(pk=pk)
    except Cab.DoesNotExist:
        return Response({"error": "Cab not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = CabSerializer(cab)
    return Response(serializer.data)


# UPDATE Cab
@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def update_cab(request, pk):
    try:
        cab = Cab.objects.get(pk=pk)
    except Cab.DoesNotExist:
        return Response({"error": "Cab not found"}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == 'PATCH'
    serializer = CabSerializer(cab, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DELETE Cab
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_cab(request, pk):
    try:
        cab = Cab.objects.get(pk=pk)
    except Cab.DoesNotExist:
        return Response({"error": "Cab not found"}, status=status.HTTP_404_NOT_FOUND)
    cab.delete()
    return Response({"message": "Cab deleted successfully"}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_Vehicle(request, pk):
    try:
        veh = Vehicle.objects.get(pk=pk)
    except Vehicle.DoesNotExist:
        return Response({"error": "vehicle not found"}, status=status.HTTP_404_NOT_FOUND)
    veh.delete()
    return Response({"message": "vehicle deleted successfully"}, status=status.HTTP_200_OK)

# Cab status changing
class CabStatusChangeAPIView(APIView):
    permission_classes = [AllowAny]

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        from .serializers import CabStautsSerializer
        from .models import Cab
        from rest_framework.response import Response
        from rest_framework import status
        def get_object_or_none(model, **kwargs):
            try:
                return model.objects.get(**kwargs)
            except model.DoesNotExist:
                return None
        try:
            instance = get_object_or_none(Cab, pk=request.data.get('id', None))
            serializer = CabStautsSerializer(instance, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Cab Status Changed successfully"}, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error Changing Cab Status")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Vehicle status changing
class VehicleStatusChangeAPIView(APIView):

    permission_classes = [AllowAny]

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        from .serializers import VehicleStautsSerializer
        from .models import Vehicle
        from rest_framework.response import Response
        from rest_framework import status
        def get_object_or_none(model, **kwargs):
            try:
                return model.objects.get(**kwargs)
            except model.DoesNotExist:
                return None
        try:
            instance = get_object_or_none(Vehicle, pk=request.data.get('id', None))
            serializer = VehicleStautsSerializer(instance, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Vehicle Status Changed successfully"}, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error Changing Vehicle Status")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Driver status changing
class DriverStatusChangeAPIView(APIView):
    permission_classes = [AllowAny]

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        from .serializers import DriverStatusSerializer
        from .models import Driver
        from rest_framework.response import Response
        from rest_framework import status
        def get_object_or_none(model, **kwargs):
            try:
                return model.objects.get(**kwargs)
            except model.DoesNotExist:
                return None
        try:
            instance = get_object_or_none(Driver, pk=request.data.get('id', None))
            serializer = DriverStatusSerializer(instance, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Driver Status Changed successfully"}, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error Changing Driver Status")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CabCategoryDeleteView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        try:
            category = CabCategory.objects.get(pk=pk)
            category.delete()
            return Response(
                {"message": "Category deleted successfully"},
                status=status.HTTP_200_OK
            )
        except CabCategory.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )
