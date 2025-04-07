from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from .views import HomePageAPIView,AboutPageAPIView,EventsListView,UpcomingEventsListView,PastEventsListView,ImageGalleryAPIView,EventsPageAPIView,SendEmailAPIView
from .views import LoginView, RequestOTPView, VerifyOTPView,ResetPasswordView, ForcePasswordResetView, UserCreateView, BulkUserUploadView,ActivateAccountView, UserFormDataView, VerifyActivationOTPView, CompleteActivationView, GetAllUsersAPIView
from rest_framework_simplejwt.views import TokenRefreshView
from search import views as search_views

from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import CustomTokenRefreshSerializer

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
    
urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    path("api/homepage/",HomePageAPIView.as_view(),name="home_page"),
    path("api/aboutpage/",AboutPageAPIView.as_view(),name="about_page"),
    path("api/events/",EventsListView.as_view(),name="events_page"),
    path('api/upcoming-events/', UpcomingEventsListView.as_view(), name='upcoming-events'),
    path('api/past-events/', PastEventsListView.as_view(), name='past-events'),
    path('api/image-gallery/', ImageGalleryAPIView.as_view(), name='past-events'),
    path('api/eventpage/',EventsPageAPIView.as_view(),name="events-page"),
    path('api/send-email/', SendEmailAPIView.as_view(), name='send_email'),
    
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/request-otp/', RequestOTPView.as_view(), name='request_otp'),
    path('api/auth/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('api/auth/forget-password/', ResetPasswordView.as_view(), name='forget_password'),
    path('api/auth/expired-password/', ForcePasswordResetView.as_view(), name='expired_password'),
    path('api/users/create/', UserCreateView.as_view(), name='user-create'),
    path('api/users/bulk-upload/', BulkUserUploadView.as_view(), name='bulk-user-upload'),
    # path('api/users/activate-account/', ActivateAccountView.as_view(), name='activate-account'),
    path("user-form-data/", UserFormDataView.as_view(), name="user-form-data"),
    path('auth/verify-activation-otp/', VerifyActivationOTPView.as_view(), name='verify-activation-otp'),
    path('auth/complete-activation/', CompleteActivationView.as_view(), name='complete-activation'),
    path('get-all-users/', GetAllUsersAPIView.as_view(), name='get-all-users'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
