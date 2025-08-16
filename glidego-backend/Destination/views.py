from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Destination
from .serializers import DestinationSerializer,DestinationStautsSerializer
from django.core.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from helpers.helper import get_object_or_none,IsSuperUser
import logging



logger = logging.getLogger(__name__)
User = get_user_model()

class DestinationListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if not request.user.has_permission('Destination.view_destination'):
                raise PermissionDenied("You do not have permission to view destinations")
            destinations = Destination.objects.all()
            if not destinations.exists():
                return Response({"message": "No destinations found"}, status=status.HTTP_200_OK)
            serializer = DestinationSerializer(destinations, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error fetching destinations: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            if not request.user.has_permission('Destination.add_destination'):
                raise PermissionDenied("You do not have permission to add destinations")
            serializer = DestinationSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error creating destination: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DestinationRetrieveUpdateDestroyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            if not request.user.has_perm('Destination.view_destination'):
                raise PermissionDenied("You do not have permission to view destinations")
            destination = Destination.objects.get(pk=pk)
            serializer = DestinationSerializer(destination, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Destination.DoesNotExist:
            return Response({"error": "Destination not found"}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error retrieving destination: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            if not request.user.has_perm('Destination.change_destination'):
                raise PermissionDenied("You do not have permission to edit destinations")
            destination = Destination.objects.get(pk=pk)
            serializer = DestinationSerializer(destination, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Destination.DoesNotExist:
            return Response({"error": "Destination not found"}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error updating destination: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            if not request.user.has_perm('Destination.delete_destination'):
                raise PermissionDenied("You do not have permission to delete destinations")
            destination = Destination.objects.get(pk=pk)
            destination.delete()
            return Response({"message": "Destination deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Destination.DoesNotExist:
            return Response({"error": "Destination not found"}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error deleting destination: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# status changing 

class DestinationStatusChangeAPIView(APIView):
    permission_classes = [IsSuperUser,]
    @swagger_auto_schema(tags=['Destination-Status'], request_body=DestinationStautsSerializer)
    def post(self, request, *args, **kwargs):
        try:
            instance    = get_object_or_none(Destination,pk=request.data.get('id',None))
            serializer = DestinationStautsSerializer(instance,data=request.data,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Destination Status Changed successfully"},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Error Changing Destiantion Status")
            return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)