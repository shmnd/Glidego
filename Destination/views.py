from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth import get_user_model
from .models import Activity, Destination
from .serializers import ActivitySerializer, DestinationSerializer
from django.core.exceptions import PermissionDenied
from glidego.permissions import has_permission  # Adjust import based on where has_permission is defined
from django.db.models import Q
# from drf_yasg.utils import swagger_auto_schema
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class DestinationListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            destinations = Destination.objects.all().order_by('order')
            serializer = DestinationSerializer(destinations, many=True, context={'request': request})
            logger.debug(f"Fetched {len(destinations)} destinations")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching destinations: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    # @swagger_auto_schema(tags=['estination-create'],request_body=DestinationSerializer)

    def post(self, request):
        try:
            logger.debug(f"Received data: {dict(request.data)}")
            print(f"Received data: {dict(request.data)}")
            serializer = DestinationSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                destination = serializer.save()
                logger.info(f"Destination created successfully: ID {destination.id}")
                return Response(
                    {"message": "Destination created successfully","data": serializer.data},
                    status=status.HTTP_201_CREATED
                )
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating destination: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DestinationListCreatePublicAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            destinations = Destination.objects.all().order_by('order')
            serializer = DestinationSerializer(destinations, many=True, context={'request': request})
            logger.debug(f"Fetched {len(destinations)} destinations")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching destinations: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.debug(f"Received data: {dict(request.data)}")
            print(f"Received data: {dict(request.data)}")
            serializer = DestinationSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                destination = serializer.save()
                logger.info(f"Destination created successfully: ID {destination.id}")
                return Response(
                    {"message": "Destination created successfully", "id": destination.id},
                    status=status.HTTP_201_CREATED
                )
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating destination: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ActivityListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            activities = Activity.objects.filter(is_active=True)
            serializer = ActivitySerializer(activities, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching activities: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DestinationDetailAPIView(APIView):
    permission_classes = [
        AllowAny
    ]

    def get(self, request, pk):
        try:
            destination = Destination.objects.get(pk=pk)
            serializer = DestinationSerializer(destination, context={'request': request})
            logger.debug(f"Fetched destination ID {pk}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Destination.DoesNotExist:
            logger.error(f"Destination with ID {pk} not found")
            return Response({"error": "Destination not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching destination: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            destination = Destination.objects.get(pk=pk)
            serializer = DestinationSerializer(destination, data=request.data, context={'request': request})
            if serializer.is_valid():
                destination = serializer.save()
                logger.info(f"Destination updated successfully: ID {destination.id}")
                return Response(
                    {"message": "Destination updated successfully", "id": destination.id},
                    status=status.HTTP_200_OK
                )
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Destination.DoesNotExist:
            logger.error(f"Destination with ID {pk} not found")
            return Response({"error": "Destination not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating destination: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            destination = Destination.objects.get(pk=pk)
            destination.delete()
            logger.info(f"Destination deleted successfully: ID {pk}")
            return Response({"message": "Destination deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Destination.DoesNotExist:
            logger.error(f"Destination with ID {pk} not found")
            return Response({"error": "Destination not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting destination: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DestinationListCrAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get search query from request
            search_query = request.query_params.get("search", None)
            destinations = Destination.objects.all().order_by("order")
            if search_query:
                destinations = destinations.filter(
                    Q(main_destination_city__icontains=search_query) |
                    Q(main_destination_state__icontains=search_query) |
                    Q(main_destination_country__icontains=search_query) |
                    Q(main_destination_description__icontains=search_query)
                )
            serializer = DestinationSerializer(destinations, many=True, context={"request": request})
            logger.debug(f"Fetched {len(destinations)} destinations")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching destinations: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DestinationDeleteAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        has_permission('delete_destination', 'destination')
    ]

    def delete(self, request, pk):
        try:
            destination = Destination.objects.get(pk=pk)
            destination.delete()
            logger.info(f"Destination deleted successfully: ID {pk}")
            return Response({"message": "Destination deleted successfully"}, status=status.HTTP_200_OK)
        except Destination.DoesNotExist:
            logger.error(f"Destination with ID {pk} not found")
            return Response({"error": "Destination not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting destination: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)