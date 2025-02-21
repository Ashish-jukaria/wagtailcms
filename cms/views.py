from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now

from .serializers import HomePageSerializer,AboutPageSerializer,EventSerializer
from home.models import HomePage,AboutPage,Event,ImageGalleryPage

class HomePageAPIView(APIView):
    def get(self,request):
        try:
            homepage = HomePage.objects.first()
            if not homepage:
                return Response({"error": "HomePage not found"}, status=404)

            serializer = HomePageSerializer(homepage)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class AboutPageAPIView(APIView):
    def get(self, request, *args, **kwargs):
        about_page = AboutPage.objects.prefetch_related(
            "faq_items", "product_panel_items", "chairman_pen_items"
        ).first()

        if not about_page:
            return Response({"error": "About page not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AboutPageSerializer(about_page)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EventsListView(APIView):
    def get(self, request, format=None):
        events = Event.objects.all()  # Optionally filter or order as needed.
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class UpcomingEventsListView(APIView):
    """
    API endpoint to fetch only upcoming events (events with start_date > current datetime).
    """
    def get(self, request, format=None):
        events = Event.objects.filter(start_date__gt=now()).order_by('start_date')
        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class PastEventsListView(APIView):
    """
    API endpoint to fetch only past events (events where end_date < current datetime).
    """
    def get(self, request, format=None):
        events = Event.objects.filter(end_date__lt=now()).order_by('-end_date')  # Show latest past events first
        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ImageGalleryAPIView(APIView):
    def get(self, request):
        # Fetch the first ImageGalleryPage (or modify for multiple galleries)
        gallery = ImageGalleryPage.objects.live().first()
        if not gallery:
            return Response({"error": "No gallery found"}, status=404)

        # Get all images in order
        images = gallery.gallery_images.all().order_by("sort_order")

        # Format response
        data = [
            {"id": img.image_id, "image_url": img.image_url} for img in images
        ]

        return Response({"gallery_images": data})