from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from wagtail.rich_text import expand_db_html
from datetime import datetime


from .serializers import HomePageSerializer,AboutPageSerializer,EventSerializer,IessSerializer,IneeSerializer,WebinarSerializer,OtherEventsSerializer,AwardsSerializer
from home.models import HomePage,AboutPage,Event,ImageGalleryPage,EventsPage,Webinar_Seminar,OtherEvents,Iess,Inee,Awards_Presentation

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
            "faq_items", "product_panel_items", "chairman_pen_items","committee_members"
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
    
class EventsPageAPIView(APIView):
    def get(self, request):
        try:
            events_page = EventsPage.objects.live().first()

            response_data = {}
            # Events Data
            if events_page:
                current_time = datetime.now()
                
                # Forthcoming and Past Events
                forthcoming_events = Event.objects.filter(
                    page=events_page,
                    start_date__gte=current_time
                ).order_by('start_date')
                
                past_events = Event.objects.filter(
                    page=events_page,
                    end_date__lt=current_time
                ).order_by('-end_date')

                events_data = {
                    'forthcoming_events': EventSerializer(forthcoming_events, many=True).data,
                    'past_events': EventSerializer(past_events, many=True).data,
                    'inee': {
                        'body': expand_db_html(events_page.inee_body) if events_page.inee_body else "",
                        'data': IneeSerializer(
                            Inee.objects.filter(page=events_page),
                            many=True
                        ).data
                    },
                    'iess': {
                        'body': expand_db_html(events_page.iess_body) if events_page.iess_body else "",
                        'data': IessSerializer(
                            Iess.objects.filter(page=events_page),
                            many=True
                        ).data
                    },
                    'awards': {
                        'body': expand_db_html(events_page.awards_body) if events_page.awards_body else "",
                        'data': AwardsSerializer(
                            Awards_Presentation.objects.filter(page=events_page),
                            many=True
                        ).data
                    },
                    'webinars_seminars': WebinarSerializer(
                        Webinar_Seminar.objects.filter(page=events_page),
                        many=True
                    ).data,
                    'other_events': OtherEventsSerializer(
                        OtherEvents.objects.filter(page=events_page),
                        many=True
                    ).data
                }
                response_data['events'] = events_data
            else:
                response_data['events'] = None

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status

class SendEmailAPIView(APIView):
    """
    API endpoint to send an email using SendGrid.
    """
    def post(self, request, *args, **kwargs):
        try:
            # Parse the request data
            data = JSONParser().parse(request)
            subject = data.get('subject', 'No Subject')
            message = data.get('message', '')
            recipient_email = 'membership.officer@epcmd.in' 
            sender_email = os.getenv('DEFAULT_FROM_EMAIL')

            if not recipient_email:
                return Response({"error": "Recipient email is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Create email message
            email = Mail(
                from_email=sender_email,
                to_emails=recipient_email,
                subject=subject,
                plain_text_content=message
            )

            # Send email using SendGrid API
            sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
            print("SENDGRID_API_KEY",os.getenv('SENDGRID_API_KEY'))
            response = sg.send(email)

            # Return response
            return Response({
                "success": "Email sent successfully",
                "status_code": response.status_code
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("Error Response:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
