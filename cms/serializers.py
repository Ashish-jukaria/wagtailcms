from rest_framework import serializers
from home.models import CarouselItem,HomePage

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