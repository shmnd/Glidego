from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Activity
from .serializers import ActivitySerializer
from rest_framework.views import APIView

@api_view(['GET'])
@permission_classes([AllowAny])
def list_activities(request):
	activities = Activity.objects.all()
	serializer = ActivitySerializer(activities, many=True, context={'request': request})
	return Response(serializer.data)

class ActivityDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            activity = Activity.objects.get(pk=pk)
        except Activity.DoesNotExist:
            return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ActivitySerializer(activity, context={'request': request})
        return Response(serializer.data)

import logging

# Set up logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_activity(request):
    # Print incoming form data and files
    print("Form Data:", dict(request.data))
    print("Files:", dict(request.FILES))
    logger.debug("Form Data: %s", dict(request.data))
    logger.debug("Files: %s", dict(request.FILES))
    
    serializer = ActivitySerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_activity(request, pk):
    try:
        activity = Activity.objects.get(pk=pk)
    except Activity.DoesNotExist:
        return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)
    
    partial = request.method == 'PATCH'
    
    # Copy the data to make it mutable
    data = request.data.copy()
    
    # Remove read-only or invalid fields
    if 'banner_image_url' in data:
        del data['banner_image_url']
    if 'id' in data:
        del data['id']
    
    # If no new banner_image file is provided, remove the field to avoid validation errors
    if 'banner_image' in data and 'banner_image' not in request.FILES:
        del data['banner_image']
    
    serializer = ActivitySerializer(activity, data=data, partial=partial, context={'request': request})
    print(f"Request data after adjustment: {data}")
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        print(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_activity(request, pk):
	try:
		activity = Activity.objects.get(pk=pk)
	except Activity.DoesNotExist:
		return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)
	activity.delete()
	return Response({'message': 'Activity deleted successfully'}, status=status.HTTP_200_OK)
