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
#
def send_email_via_sendgrid(recipient_email, subject, message):
    """
    Reusable function to send emails using your preferred SendGrid approach
    """
    try:
        sender_email = os.getenv('DEFAULT_FROM_EMAIL')
        
        email = Mail(
            from_email=sender_email,
            to_emails=recipient_email,
            subject=subject,
            plain_text_content=message
        )
        
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(email)
        return True, response.status_code
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False, str(e)

import random
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from users.models import CustomUser, PasswordHistory, OTP
from rest_framework import status
from datetime import datetime, timedelta
import re

def validate_password(password):
    """Enforce password policy"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    return True, ""

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
from django.contrib.auth.hashers import check_password
from django.db import models
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        if not check_password(password, user.password):  
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        if user.is_password_expired():
            return Response({
                'error': 'Password expired. Please reset your password.',
                'password_expired': True
            }, status=status.HTTP_403_FORBIDDEN)
        
        tokens = get_tokens_for_user(user)
        return Response({
            **tokens,
            'is_admin': user.is_admin
        })

class RequestOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Delete any existing OTPs for this user
        OTP.objects.filter(user=user).delete()
        
        otp = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, otp=otp)
        
        success, response = send_email_via_sendgrid(
            recipient_email=email,
            subject='Your OTP Code',
            message=f'Your OTP is {otp}. It expires in 10 minutes.'
        )
        
        if not success:
            return Response({'error': 'Failed to send OTP', 'details': response}, status=500)
            
        return Response({'message': 'OTP sent'})
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        otp_record = OTP.objects.filter(user=user, otp=otp).first()
        if not otp_record or not otp_record.is_valid():
            return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate a one-time token for password reset
        reset_token = default_token_generator.make_token(user)
        otp_record.reset_token = reset_token
        otp_record.save()
        
        return Response({
            'message': 'OTP verified successfully',
            'reset_token': reset_token,
            'user_id': user.id
        })
        
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        reset_token = request.data.get('reset_token')
        new_password = request.data.get('new_password')
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verify the reset token is associated with a valid OTP
        otp_record = OTP.objects.filter(
            user=user,
            reset_token=reset_token,
            created_at__gte=timezone.now()-timezone.timedelta(minutes=10)
        ).first()
        
        if not otp_record:
            return Response({'error': 'Invalid or expired reset token'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate password policy
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        
        print(check_password(new_password, user.password))

        if check_password(new_password, user.password):
            return Response({'error': 'New password cannot be same as current password'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        # Check password history
        if self._is_password_reused(user, new_password):
            return Response({'error': 'Cannot reuse last 3 passwords'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update password
        with transaction.atomic():
            hashed_password = make_password(new_password)
            PasswordHistory.objects.create(user=user, password_hash=hashed_password)
            user.password = hashed_password
            user.password_changed_date = now()
            user.save()
            otp_record.delete()
        
        return Response({'message': 'Password reset successfully'})
    
    def _is_password_reused(self, user, new_password):
        last_passwords = PasswordHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:3]
        return any(check_password(new_password, record.password_hash) for record in last_passwords)
# class VerifyOTPView(APIView):
#     permission_classes = [AllowAny]
    
#     def post(self, request):
#         email = request.data.get('email')
#         otp = request.data.get('otp')
#         new_password = request.data.get('new_password')
        
#         user = CustomUser.objects.filter(email=email).first()
#         if not user:
#             return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
#         otp_record = OTP.objects.filter(user=user, otp=otp).first()
#         if not otp_record or not otp_record.is_valid():
#             return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
#         # Validate password policy
#         is_valid, message = validate_password(new_password)
#         if not is_valid:
#             return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        
#         # Check if new password matches last 3 passwords
#         last_passwords = PasswordHistory.objects.filter(user=user).order_by('-created_at')[:3]
#         for record in last_passwords:
#             if check_password(new_password, record.password_hash):
#                 return Response({'error': 'Cannot reuse last 3 passwords'}, status=status.HTTP_400_BAD_REQUEST)
        
#         # Update password
#         with transaction.atomic():
#             hashed_password = make_password(new_password)
#             PasswordHistory.objects.create(user=user, password_hash=hashed_password)
#             user.password = hashed_password
#             user.password_changed_date = now()
#             user.save()
#             otp_record.delete()
        
#         return Response({'message': 'Password reset successfully'})

class ForcePasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Basic validation
        if not all([email, old_password, new_password, confirm_password]):
            return Response(
                {'error': 'All fields are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if new_password != confirm_password:
            return Response(
                {'error': 'New passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify old password
        if not check_password(old_password, user.password):
            return Response(
                {'error': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if password is actually expired (defense in depth)
        # if not user.is_password_expired():
        #     return Response(
        #         {'error': 'Password is not expired yet'},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        
        # Validate password policy
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if new password is same as old password
        if check_password(new_password, user.password):
            return Response(
                {'error': 'New password cannot be same as current password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check password history (last 3 passwords)
        if self._is_password_reused(user, new_password):
            return Response(
                {'error': 'Cannot reuse last 3 passwords'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update password
        with transaction.atomic():
            hashed_password = make_password(new_password)
            PasswordHistory.objects.create(user=user, password_hash=hashed_password)
            user.password = hashed_password
            user.password_changed_date = now()
            user.save()
        
        return Response(
            {'message': 'Password reset successfully'},
            status=status.HTTP_200_OK
        )
    
    def _is_password_reused(self, user, new_password):
        last_passwords = PasswordHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:3]
        return any(check_password(new_password, record.password_hash) for record in last_passwords)
    
import pandas as pd
from rest_framework.parsers import FileUploadParser, MultiPartParser
from io import StringIO
import csv
from django.core.exceptions import ValidationError
from django.db import IntegrityError

class UserCreateView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Check if data is a single user or multiple users
        user_data_list = request.data if isinstance(request.data, list) else [request.data]
        
        required_fields = [
            'firm_name', 'gst_no', 
            'membership_start_date', 'membership_end_date',
            'contact_person_name', 'contact_person_email',
            'contact_person_phone'
        ]
        
        created_users = []
        errors = []
        
        try:
            with transaction.atomic():
                for index, user_data in enumerate(user_data_list):
                    # Validate required fields for each user
                    missing_fields = [field for field in required_fields if field not in user_data]
                    if missing_fields:
                        errors.append({
                            'index': index,
                            'error': f'Missing required fields: {", ".join(missing_fields)}'
                        })
                        continue
                    
                    try:
                        user = CustomUser(
                            firm_name=user_data['firm_name'],
                            gst_no=user_data['gst_no'],
                            membership_start_date=user_data['membership_start_date'],
                            membership_end_date=user_data['membership_end_date'],
                            contact_person_name=user_data['contact_person_name'],
                            contact_person_email=user_data['contact_person_email'],
                            contact_person_phone=user_data['contact_person_phone'],
                            is_active=False
                        )
                        
                        user.full_clean()
                        user.save()
                        
                        # Generate activation token
                        token = default_token_generator.make_token(user)
                        user.activation_token = token
                        user.token_created_at = now()
                        user.save()
                        
                        # Send activation email
                        activation_link = f"{settings.FRONTEND_URL}/activate-account?id={user.id}&token={token}"
                        send_email_via_sendgrid(
                            recipient_email=user.contact_person_email,
                            subject='Activate Your Account',
                            message=f'''
                            Please activate your account for {user.firm_name} by clicking the link below:
                            {activation_link}
                            
                            You will be asked to provide:
                            - Your email address (for login)
                            - A secure password
                            '''
                        )
                        
                        created_users.append({
                            'id': user.id,
                            'firm_name': user.firm_name,
                            'contact_email': user.contact_person_email
                        })
                        
                    except ValidationError as e:
                        errors.append({
                            'index': index,
                            'error': str(e),
                            'data': user_data
                        })
                    except IntegrityError:
                        errors.append({
                            'index': index,
                            'error': 'A firm with this GST number already exists',
                            'data': user_data
                        })
        
                if not created_users and errors:
                    return Response(
                        {'error': 'All user creations failed', 'details': errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                return Response({
                    'message': f'Successfully created {len(created_users)} user(s)',
                    'created_users': created_users,
                    'errors': errors if errors else None
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class BulkUserUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]
    
    def post(self, request):
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file uploaded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        
        try:
            # Read file
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                return Response(
                    {'error': 'Unsupported file format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            required_columns = [
                'firm_name', 'gst_no',
                'membership_start_date', 'membership_end_date',
                'contact_person_name', 'contact_person_email',
                'contact_person_phone'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response(
                    {'error': f'Missing columns: {", ".join(missing_columns)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            success_count = 0
            errors = []
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        user = CustomUser(
                            firm_name=row['firm_name'],
                            gst_no=row['gst_no'],
                            membership_start_date=row['membership_start_date'],
                            membership_end_date=row['membership_end_date'],
                            contact_person_name=row['contact_person_name'],
                            contact_person_email=row['contact_person_email'],
                            contact_person_phone=row['contact_person_phone'],
                            is_active=False
                        )
                        
                        user.full_clean()
                        user.save()
                        
                        # Generate token
                        token = default_token_generator.make_token(user)
                        user.activation_token = token
                        user.token_created_at = now()
                        user.save()
                        
                        # Send email
                        activation_link = f"{settings.FRONTEND_URL}/activate-account?id={user.id}&token={token}"
                        send_email_via_sendgrid(
                            recipient_email=user.contact_person_email,
                            subject=f'Activate {user.firm_name} Account',
                            message=f'Activation link: {activation_link}'
                        )
                        
                        success_count += 1
                        
                    except ValidationError as e:
                        errors.append(f"Row {index+1}: {str(e)}")
                    except IntegrityError:
                        errors.append(f"Row {index+1}: Duplicate GST number")
            
            return Response({
                'message': f'Processed {len(df)} records',
                'success_count': success_count,
                'errors': errors
            })
            
        except Exception as e:
            return Response(
                {'error': f'File processing error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
class ActivateAccountView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        token = request.data.get('token')
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            user = CustomUser.objects.get(id=user_id, is_active=False)
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'Invalid activation request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate token
        if not default_token_generator.check_token(user, token):
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate email
        if not email or '@' not in email:
            return Response(
                {'error': 'Valid email required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if email already used
        if CustomUser.objects.filter(email=email).exclude(id=user.id).exists():
            return Response(
                {'error': 'Email already in use'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Activate user
        with transaction.atomic():
            user.email = email
            user.set_password(password)
            user.is_active = True
            user.activation_token = None
            user.token_created_at = None
            user.password_changed_date = now()
            user.save()
            
            # Record password
            PasswordHistory.objects.create(
                user=user,
                password_hash=user.password
            )
        
        return Response(
            {'message': 'Account activated successfully'},
            status=status.HTTP_200_OK
        )
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from users.models import UserFormData
from .serializers import UserFormDataSerializer
class UserFormDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch user form data"""
        user_data, created = UserFormData.objects.get_or_create(user=request.user)
        serializer = UserFormDataSerializer(user_data)
        return Response(serializer.data)

    def post(self, request):
        """Update user form data"""
        user_data, created = UserFormData.objects.get_or_create(user=request.user)
        serializer = UserFormDataSerializer(user_data, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)