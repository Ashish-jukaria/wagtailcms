from rest_framework import serializers
from wagtail.rich_text import expand_db_html

from home.models import CarouselItem,HomePage,AboutPage,Event,FAQItem,ChairmanPenItem,ProductPanelItem

class CarouselItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CarouselItem
        fields = ["id", "image_url", "caption"]

    def get_image_url(self, obj):
        return obj.image.file.url if obj.image else None


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

class AboutPageSerializer(serializers.ModelSerializer):
    rendered_content = serializers.SerializerMethodField()
    rendered_activities_services = serializers.SerializerMethodField()
    faq_items = FAQItemSerializer(many=True, read_only=True)
    product_panel_items = ProductPanelItemSerializer(many=True, read_only=True)
    chairman_pen_items = ChairmanPenItemSerializer(many=True, read_only=True)

    class Meta:
        model = AboutPage
        fields = [
            "id", "title", "rendered_content",
            "rendered_activities_services", "faq_items",
            "product_panel_items", "chairman_pen_items"
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