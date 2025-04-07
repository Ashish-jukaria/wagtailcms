from rest_framework import serializers
from wagtail.rich_text import expand_db_html

from home.models import CarouselItem,HomePage,AboutPage,Event,FAQItem,ChairmanPenItem,ProductPanelItem,Inee,Iess,Webinar_Seminar,Awards_Presentation,OtherEvents,CommitteeMemeber,Designation
from users.models import UserFormData
class CarouselItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CarouselItem
        fields = ["id", "image_url", "caption"]

    def get_image_url(self, obj):
        return obj.image.signed_url if obj.image else None


class HomePageSerializer(serializers.ModelSerializer):
    carousel_items = CarouselItemSerializer(many=True)

    class Meta:
        model = HomePage
        fields = ["id", "title", "carousel_items"]
        
        
class FAQItemSerializer(serializers.ModelSerializer):
    rendered_answer = serializers.SerializerMethodField()

    class Meta:
        model = FAQItem
        fields = ["id", "question", "rendered_answer"]

    def get_rendered_answer(self, obj):
        return expand_db_html(obj.answer) if obj.answer else ""

class ProductPanelItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPanelItem
        fields = ["id", "sl_no", "panel_name", "convenor", "officer"]

class ChairmanPenItemSerializer(serializers.ModelSerializer):
    rendered_content = serializers.SerializerMethodField()

    class Meta:
        model = ChairmanPenItem
        fields = ["id", "rendered_content"]

    def get_rendered_content(self, obj):
        return expand_db_html(obj.content) if obj.content else ""
class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['title']


class CommitteeMemberSerializer(serializers.ModelSerializer):
    designations = DesignationSerializer(many=True, source='designations.all')  # Nested serializer for designations

    class Meta:
        model = CommitteeMemeber
        fields = ['name', 'designations', 'image_url','subname']
        
class AboutPageSerializer(serializers.ModelSerializer):
    rendered_content = serializers.SerializerMethodField()
    rendered_activities_services = serializers.SerializerMethodField()
    faq_items = FAQItemSerializer(many=True, read_only=True)
    product_panel_items = ProductPanelItemSerializer(many=True, read_only=True)
    chairman_pen_items = ChairmanPenItemSerializer(many=True, read_only=True)
    committee_members = CommitteeMemberSerializer(many=True, read_only=True)
    

    class Meta:
        model = AboutPage
        fields = [
            "id", "title", "rendered_content",
            "rendered_activities_services", "faq_items",
            "product_panel_items", "chairman_pen_items", "committee_members"
        ]

    def get_rendered_content(self, obj):
        return expand_db_html(obj.content) if obj.content else ""

    def get_rendered_activities_services(self, obj):
        return expand_db_html(obj.activities_services) if obj.activities_services else ""
    
class EventSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "title",
            "location",
            "start_date",
            "end_date",
            "image_url",
            "redirect_url",
        ]

    def get_image_url(self, obj):
        return obj.image.file.url if obj.image else None
    
    
class IneeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inee
        fields = ['sl_no', 'year', 'city', 'country', 'company_participated']

class IessSerializer(serializers.ModelSerializer):
    post_show_report_url = serializers.SerializerMethodField()

    class Meta:
        model = Iess
        fields = ['name', 'event_name', 'from_date', 'to_date', 'venue', 'post_show_report_url']

    def get_post_show_report_url(self, obj):
        return obj.post_show_report.url if obj.post_show_report else None

class AwardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Awards_Presentation
        fields = ['name', 'date', 'places', 'region']

class WebinarSerializer(serializers.ModelSerializer):
    rendered_body = serializers.SerializerMethodField()

    class Meta:
        model = Webinar_Seminar
        fields = ['from_date', 'to_date', 'from_time', 'to_time', 'title', 'rendered_body']

    def get_rendered_body(self, obj):
        return expand_db_html(obj.body) if obj.body else ""

class OtherEventsSerializer(serializers.ModelSerializer):
    flag_url = serializers.SerializerMethodField()
    rendered_body = serializers.SerializerMethodField()

    class Meta:
        model = OtherEvents
        fields = ['flag_url', 'from_date', 'to_date', 'heading', 'rendered_body']

    def get_flag_url(self, obj):
        return obj.flag.file.url if obj.flag else None
    
    def get_rendered_body(self, obj):
        return expand_db_html(obj.body) if obj.body else ""
    
    
class UserFormDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFormData
        fields = "__all__"
        read_only_fields = ["user"]

    def validate(self, data):
        # Ensure all fields except WhatsApp are provided
        required_fields = [
            "address", "contact_email", "contact_name", "description",
            "gst", "pan", "hsn_codes", "organization", "contact_mobile","alternate_email"
        ]
        for field in required_fields:
            if field not in data or not data[field]:
                raise serializers.ValidationError({field: f"{field} is required."})
        return data
    
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         # Add custom claims
#         token['is_admin'] = user.is_admin
#         return token
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        refresh = RefreshToken(attrs['refresh'])
        user_id = refresh['user_id']
        user = User.objects.get(id=user_id)

        # Inject custom claims into the new access token
        new_access = refresh.access_token
        new_access['is_admin'] = user.is_admin
        new_access['email'] = user.email

        data['access'] = str(new_access)
        return data