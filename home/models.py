from django.db import models
from wagtail.models import Page,Orderable
from wagtail.images.models import Image
from wagtail.admin.panels import FieldPanel, MultiFieldPanel,InlinePanel
from wagtail.api import APIField
from modelcluster.fields import ParentalManyToManyField
from wagtail.fields import RichTextField
from django.db import models
from wagtail.images.models import AbstractImage, AbstractRendition
from cloudinary_storage.storage import MediaCloudinaryStorage
from modelcluster.fields import ParentalKey
from rest_framework.serializers import SerializerMethodField
from wagtail.rich_text import expand_db_html
from bs4 import BeautifulSoup


class CustomImage(AbstractImage):
    file = models.ImageField(
        upload_to='images/',
        storage=MediaCloudinaryStorage(),  # Cloudinary storage
        height_field='height',
        width_field='width',
        verbose_name='file'
    )
    admin_form_fields=Image.admin_form_fields
    

class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (('image', 'filter_spec', 'focal_point_key'),)
        
        
        
# Carousel Item Model (linked to HomePage)

class HomePage(Page):
    content_panels = Page.content_panels + [
        InlinePanel("carousel_items", label="Carousel Images")
    ]
    api_fields = [
        APIField("carousel_items"),
    ]
class CarouselItem(models.Model):
    page = ParentalKey("home.HomePage", on_delete=models.CASCADE, related_name="carousel_items")
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name="+")
    caption = models.CharField(max_length=255, blank=True, null=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]
    
    api_fields = [
        APIField("image"),
        APIField("caption"),
        APIField("image_url")
    ]
    
    @property
    def image_url(self):
        if self.image:
            return self.image.file.url
        return None    
    
class AboutPage(Page):
    content = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("content"),
    ]
    
        
    api_fields = [
        APIField("content"),
       
    ]
    
    

class EventsPage(Page):
    """
    A Wagtail page to list and manage multiple events.
    """
    content_panels = Page.content_panels + [
        InlinePanel('events', label="Events"),
    ]
    api_fields = [
        APIField("events"), 
    ]


class Event(Orderable):
    """
    An event item that belongs to an EventsPage.
    """
    page = ParentalKey(
        EventsPage, on_delete=models.CASCADE, related_name='events'
    )
    title = models.CharField(max_length=255)
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name="event_image")
    location = models.CharField(max_length=255)
    start_date = models.DateTimeField("From")
    end_date = models.DateTimeField("To")
    
    redirect_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to redirect user when they click the event button."
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('image'),
        FieldPanel('location'),
        FieldPanel('start_date'),
        FieldPanel('end_date'),
        FieldPanel('redirect_url'),

    ]
    
    
    api_fields = [
        APIField("title"),
        APIField("image"),
        APIField("location"),
        APIField("start_date"),    
        APIField("end_date"), 
        APIField("redirect_url"),
   
    ]
    
    