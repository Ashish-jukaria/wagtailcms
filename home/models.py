# models.py - FIRST 3 LINES
from django.core.cache import caches
cache = caches['default']  #
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
from storages.backends.s3boto3 import S3Boto3Storage  # Import S3 storage backend
import boto3
from django.conf import settings
from django.core.files.storage import default_storage
from wagtail.images.models import Filter


class CustomImage(AbstractImage):
    file = models.ImageField(
        upload_to='images/',
        storage=S3Boto3Storage(),  # Ensure S3 is used
        height_field='height',
        width_field='width',
        verbose_name='file'
    )
    admin_form_fields = Image.admin_form_fields
    
    @property
    def signed_url(self):
        """Generate a pre-signed URL that's valid for 1 hour"""
        if not self.file:
            return None
        
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
                config=boto3.session.Config(signature_version='s3v4')
            )
            return s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': self.file.name,
                    'ResponseContentDisposition': 'inline'
                },
                ExpiresIn=3600  # 1 hour expiration
            )
        except Exception as e:
            print(f"Error generating signed URL: {str(e)}")
            return None
    

    

class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name='renditions')
    
    class Meta:
        unique_together = (('image', 'filter_spec', 'focal_point_key'),)
# class CustomImage(AbstractImage):
#     file = models.ImageField(
#         upload_to='images/',
#         # storage=MediaCloudinaryStorage(),  # Cloudinary storage
#         storage=S3Boto3Storage(),  # Use S3 storage instead of Cloudinary
#         height_field='height',
#         width_field='width',
#         verbose_name='file'
#     )
#     admin_form_fields=Image.admin_form_fields
#     def get_signed_url(self):
#         """Generate a temporary signed URL for accessing the image"""
#         s3_client = boto3.client(
#             "s3",
#             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#             region_name=settings.AWS_S3_REGION_NAME,
#         )

#         return s3_client.generate_presigned_url(
#             "get_object",
#             Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": self.file.name},
#             ExpiresIn=3600,  # URL expires in 1 hour
#         )

#     api_fields = [
#         APIField("id"),
#         APIField("signed_url", serializer=SerializerMethodField()),
#     ]

#     def get_signed_url_field(self, obj):
#         return self.get_signed_url()


# class CustomRendition(AbstractRendition):
#     image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name='renditions')

#     class Meta:
#         unique_together = (('image', 'filter_spec', 'focal_point_key'),)
        
        
        
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
            return self.image.signed_url
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
    subname=models.CharField(max_length=255,null=True,blank=True)
    image=models.ForeignKey(CustomImage,on_delete=models.CASCADE,related_name="committee_member_image")
    
    panels=[
        FieldPanel("name"),
        InlinePanel("designations", label="Designations"),  # Add InlinePanel for designations
        FieldPanel("image"),
        FieldPanel("subname"),

    ]
    
    api_fields=[
        APIField("name"),
        APIField("designation"),
        APIField("image_url"),
        APIField("subname"),
    ]
    
    @property
    def image_url(self):
        if self.image:
            return self.image.signed_url
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
        return self.image.signed_url if self.image else None
    
    
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

class Organization_Member_Page(Page):
    content_panels = Page.content_panels + [
        InlinePanel("members", label="Organization Members"),
    ]
from users.models import CustomUser  # Instead of from home.models
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from users.models import CustomUser

class OrganizationMember(Orderable):
    page = ParentalKey(Organization_Member_Page, on_delete=models.CASCADE, related_name="members")
    email = models.EmailField(unique=True)
    temp_password = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Initial Password",
        help_text="Set initial password (won't be stored after save)"
    )

    panels = [
        FieldPanel("email"),
        FieldPanel("temp_password"),
    ]

    def clean(self):
        """Validate before saving"""
        if self.temp_password and len(self.temp_password) < 8:
            raise ValidationError("Password must be at least 8 characters")

    def save(self, *args, **kwargs):
        """Create user account on save"""
        if self.temp_password:
            # Create/update user with hashed password
            CustomUser.objects.update_or_create(
                email=self.email,
                defaults={'password': make_password(self.temp_password)}
            )
            self.temp_password = ""  # Clear immediately after use
        
        super().save(*args, **kwargs)