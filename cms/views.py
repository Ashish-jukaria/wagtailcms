from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import HomePageSerializer
from home.models import HomePage

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