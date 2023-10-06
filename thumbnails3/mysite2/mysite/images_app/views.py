from datetime import timedelta

from django.utils import timezone
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action

from images_app.models import Image, ImageLink, ImageUser
from images_app.serializers import (
    ImageSerializer,
    BasicPlanImageSerializer,
    PremiumPlanImageSerializer,
    UploadImageSerializer, TempLinkSerializer, UserSerializer
)

from rest_framework.response import Response

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from wsgiref.util import FileWrapper
import mimetypes


# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = ImageUser.objects.all()
    serializer_class = UserSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = UploadImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # @action: To dekorator dostarczony przez Django REST Framework (DRF),
    @action(detail=False, methods=['get'], url_path='my-images')
    def my_images(self, request):
        user_plan = request.user.plan

        if user_plan == 'B':
            # Dla użytkownika z planem B, zwróć tylko obrazy z miniaturą 200px
            images = Image.objects.filter(owner=request.user)
            serializer = BasicPlanImageSerializer(images, many=True)
            return Response(serializer.data)
        elif user_plan == 'P':
            # Dla użytkownika z planem P, zwróć obrazy z miniaturą 200px i 400px
            images = Image.objects.filter(owner=request.user)
            serializer = PremiumPlanImageSerializer(images, many=True)
            return Response(serializer.data)
        elif user_plan == 'E':
            # Dla użytkownika z planem E, zwróć wszystkie obrazy (oryginalne, miniatury 200px i 400px)
            images = Image.objects.filter(owner=request.user)
            serializer = ImageSerializer(images, many=True)
            return Response(serializer.data)
        else:
            # W przypadku, gdy plan nie jest rozpoznany, zwróć pusty wynik
            return Response([])

    @action(detail=True, methods=['get'], url_path='temp/(?P<expiration_time>\d+)')
    def temp_link(self, request, pk, expiration_time):
        try:
            if request.user.plan == 'E':
                # Convert expiration_time to an integer
                expiration_time = int(expiration_time)

                # Check if expiration_time is within the allowed range (300 to 30000)
                if not (300 <= expiration_time <= 30000):
                    return Response({'detail': 'Expiration time must be between 300 and 30000'},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Calculate the valid_to based on expiration_time
                valid_to = timezone.now() + timedelta(seconds=expiration_time)

                # Query the Image model to find an image that matches the given criteria
                image = Image.objects.get(pk=pk, owner=request.user)

                # Create a temporary link
                link = ImageLink.objects.create(
                    user=request.user, image=image, valid_to=valid_to, expiration_time=expiration_time
                )

                serializer = TempLinkSerializer(link)
                return Response(serializer.data)
            else:
                return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        except Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='download/(?P<code>[^/.]+)')
    def download_image(self, request, code=None):
        # Retrieve the ImageLink object based on the provided code
        link = get_object_or_404(ImageLink, code=code)

        # Check if the link is still valid
        if link.is_valid():
            # Get the path to the image file
            path = link.image.image.path

            # Open the file in binary mode
            with open(path, 'rb') as file:
                # Create a Django FileWrapper, which is useful for large files
                file_wrapper = FileWrapper(file)

                # Get the MIME type of the file
                content_type = mimetypes.guess_type(path)[0]

                # Build the response with the appropriate content type and attachment header
                response = HttpResponse(file_wrapper, content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{link.image.image.name}"'

                return response
        else:
            # Handle expired link
            return Response({'detail': 'Link has expired'}, status=status.HTTP_400_BAD_REQUEST)





