from rest_framework import serializers
from wagtail.rich_text import expand_db_html

from home.models import CarouselItem,HomePage,AboutPage,Event

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
        
class AboutPageSerializer(serializers.ModelSerializer):
    rendered_content = serializers.SerializerMethodField()
    class Meta:
        model = AboutPage
        fields = ["id", "title", "content","rendered_content"]
        
    def get_rendered_content(self, obj):
        # Convert the rich text content stored in the database into full HTML.
        return expand_db_html(obj.content)
        
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