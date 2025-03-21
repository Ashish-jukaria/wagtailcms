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
from cloudinary_storage.storage import RawMediaCloudinaryStorage



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
    activities_services = RichTextField(blank=True, null=True)
    content_panels = Page.content_panels + [
        FieldPanel("content"),
        FieldPanel("activities_services"),
        InlinePanel("faq_items", label="FAQs"),
        InlinePanel("product_panel_items", label="Product Panel"),
        InlinePanel("chairman_pen_items", label="Chairman Pen",max_num=1),
        InlinePanel("committee_members", label="Committee Members")
    ]
          
    api_fields = [
        APIField("content"),
        APIField("activities_services"),
        APIField("faq_items"),
        APIField("product_panel_items"),
        APIField("chairman_pen_items"),
    ]
from modelcluster.models import ClusterableModel  # Import ClusterableModel

class CommitteeMemeber(Orderable,ClusterableModel):
    page=ParentalKey(AboutPage,on_delete=models.CASCADE,related_name="committee_members")
    name=models.CharField(max_length=255)
    image=models.ForeignKey(CustomImage,on_delete=models.CASCADE,related_name="committee_member_image")
    
    panels=[
        FieldPanel("name"),
        InlinePanel("designations", label="Designations"),  # Add InlinePanel for designations
        FieldPanel("image"),
    ]
    
    api_fields=[
        APIField("name"),
        APIField("designation"),
        APIField("image_url"),
    ]
    
    @property
    def image_url(self):
        if self.image:
            return self.image.file.url
        return None
class Designation(Orderable):
    """
    A model to store multiple designations for a committee member.
    """
    member = ParentalKey(CommitteeMemeber, on_delete=models.CASCADE, related_name="designations")
    title = models.CharField(max_length=255)

    panels = [
        FieldPanel("title"),
    ]

    api_fields = [
        APIField("title"),
    ]
class FAQItem(Orderable):
    page = ParentalKey(AboutPage, on_delete=models.CASCADE, related_name="faq_items")
    question = models.CharField(max_length=255)
    answer = RichTextField()
    
    panels = [
        FieldPanel("question"),
        FieldPanel("answer"),
    ]
    
    api_fields = [
        APIField("question"),
        APIField("answer"),
    ]
    
class ProductPanelItem(Orderable):
    page = ParentalKey(AboutPage, on_delete=models.CASCADE, related_name="product_panel_items")
    sl_no = models.IntegerField()
    panel_name = models.CharField(max_length=255)
    convenor = models.CharField(max_length=255)
    officer = models.CharField(max_length=255)

    panels = [
        FieldPanel("sl_no"),
        FieldPanel("panel_name"),
        FieldPanel("convenor"),
        FieldPanel("officer"),
    ]
    
    api_fields = [
        APIField("sl_no"),
        APIField("panel_name"),
        APIField("convenor"),
        APIField("officer"),
    ]
    
class ChairmanPenItem(Orderable):
    page = ParentalKey(AboutPage, on_delete=models.CASCADE, related_name="chairman_pen_items")
    content = RichTextField()

    panels = [
        FieldPanel("content"),
    ]

    api_fields = [
        APIField("content"),
        
    ]

class EventsPage(Page):
    """
    A Wagtail page to list and manage multiple events.
    """
    inee_body=RichTextField(blank=True)
    iess_body=RichTextField(blank=True)
    awards_body=RichTextField(blank=True)


    content_panels = Page.content_panels + [
        InlinePanel('events', label="Events"),
        FieldPanel('inee_body'),
        InlinePanel('inee_events',label="INEE"),
        FieldPanel('iess_body'),  
        InlinePanel('iess_events',label="IESS"),
        FieldPanel('awards_body'),  
        InlinePanel('events_awards',label="Awards"),
        InlinePanel('events_webinar',label="Webinars/Seminars"),
        InlinePanel('other_events',label="Other_Events"),



    ]
    api_fields = [
        APIField("events"), 
        APIField("inee_body"),
        APIField("inee_events"),
        APIField("iess_body"),
        APIField("iess_events"),
        APIField("awards_body"),
        APIField("events_awards"),
        APIField("events_webinar"),
        APIField("other_events")

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
    



class ImageGalleryPage(Page):
    """
    A Wagtail page to store multiple images in an image gallery.
    """
    content_panels = Page.content_panels + [
        InlinePanel('gallery_images', label="Gallery Images"),
    ]

    api_fields = [
        APIField("gallery_images"),
    ]


class ImageGalleryItem(Orderable):
    """
    An image entry for the ImageGalleryPage.
    """
    page = ParentalKey(
        ImageGalleryPage, on_delete=models.CASCADE, related_name='gallery_images'
    )
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name="gallery_images")

    panels = [
        FieldPanel('image'),
    ]

    api_fields = [
        APIField("image"),
        APIField("image_id"),
        APIField("image_url"),
    ]

    @property
    def image_id(self):
        return self.image.id if self.image else None

    @property
    def image_url(self):
        return self.image.file.url if self.image else None
    
    
class Inee(Orderable):
    page=ParentalKey(EventsPage,on_delete=models.CASCADE,related_name="inee_events")
    sl_no=models.IntegerField()
    year=models.PositiveIntegerField()
    city=models.CharField(max_length=255)
    country=models.CharField(max_length=255)
    company_participated=models.IntegerField()
    
    panels=[
        FieldPanel('sl_no'),
        FieldPanel('year'),
        FieldPanel('city'),
        FieldPanel('country'),
        FieldPanel('company_participated'),

    ]
    
    api_fields=[
        APIField('sl_no'),
        APIField('year'),
        APIField('city'),
        APIField('country'),
        APIField('company_participated'),
        
    ]
    
class Iess(Orderable):
    page=ParentalKey(EventsPage,on_delete=models.CASCADE,related_name="iess_events")
    name=models.CharField(max_length=255)
    event_name=models.CharField(max_length=255)
    from_date=models.DateField("From")
    to_date=models.DateField("To")
    venue=models.CharField(max_length=255)
    post_show_report = models.FileField(upload_to="documents/", storage=RawMediaCloudinaryStorage(), blank=True, null=True)
    
    
    panels=[
        FieldPanel('name'),
        FieldPanel('event_name'),
        FieldPanel('from_date'),
        FieldPanel('to_date'),
        FieldPanel('venue'),
        FieldPanel('post_show_report'),
    ]
    
    api_fields=[
        APIField('name'),
        APIField('event_name'),
        APIField('from_date'),
        APIField('to_date'),
        APIField('venue'),
        APIField('post_show_report'),
    ]


class Awards_Presentation(Orderable):
    REGION_CHOICES = [
    ("EASTERN", "Eastern"),
    ("WESTERN", "Western"),
    ("NORTHERN", "Northern"),
    ("SOUTHERN", "Southern"),
    ]

    page=ParentalKey(EventsPage,on_delete=models.CASCADE,related_name="events_awards")
    name=models.CharField(max_length=255)
    date=models.DateField()
    places=models.CharField(max_length=255)
    region=models.CharField(max_length=10,choices=REGION_CHOICES,default="NORTHERN")
    
    
    panels=[
        FieldPanel('name'),
        FieldPanel('date'),
        FieldPanel('places'),
        FieldPanel('region'),
    ]
    
    api_fields=[
        APIField('name'),
        APIField('date'),
        APIField('places'),
        APIField('region'),
    ]
    
    
class Webinar_Seminar(Orderable):
    page=ParentalKey(EventsPage,on_delete=models.CASCADE,related_name="events_webinar")
    from_date=models.DateField()
    to_date=models.DateField()
    from_time=models.TimeField()
    to_time=models.TimeField()
    title=models.CharField(max_length=255)
    body=RichTextField(blank=True)
    
    panels=[
        FieldPanel('from_date'),
        FieldPanel('to_date'),
        FieldPanel('from_time'),
        FieldPanel('to_time'),
        FieldPanel('title'),
        FieldPanel('body'),
    ]
    
    api_fields=[
        APIField('from_date'),
        APIField('to_date'),
        APIField('from_time'),
        APIField('to_time'),
        APIField('title'),
        APIField('body'),
    ]
    
    
class OtherEvents(Orderable):
    page=ParentalKey(EventsPage,on_delete=models.CASCADE,related_name="other_events")
    flag=models.ForeignKey(CustomImage,on_delete=models.CASCADE,related_name="flag_image")
    from_date=models.DateField()
    to_date=models.DateField()
    heading=models.CharField(max_length=255)
    body=RichTextField(blank=True)
    
    panels=[
        FieldPanel("flag"),
        FieldPanel("from_date"),
        FieldPanel("to_date"),
        FieldPanel("heading"),
        FieldPanel("body"),
    ]
    
    api_fields=[
        APIField("flag"),
        APIField("from_date"),
        APIField("to_date"),
        APIField("heading"),
        APIField("body"),
    ]
    
    
class MembershipPage(Page):
    membership_benefit=RichTextField(blank=True)
    content_panels=Page.content_panels+[
    FieldPanel('membership_benefit'),
    ]