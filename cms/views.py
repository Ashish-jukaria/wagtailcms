from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import HomePageSerializer,AboutPageSerializer,EventSerializer
from home.models import HomePage,AboutPage,Event

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
        # Fetch the first AboutPage instance
        about_page = AboutPage.objects.first()  

        if not about_page:
            return Response({"error": "About page not found"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the data
        serializer = AboutPageSerializer(about_page)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EventsListView(APIView):
    def get(self, request, format=None):
        events = Event.objects.all()  # Optionally filter or order as needed.
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)