from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
import datetime
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.hashers import make_password, check_password

# class CustomUser(AbstractUser):
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=128)
#     password_changed_date = models.DateTimeField(auto_now_add=True)
#     username = None  # Remove username field
#     USERNAME_FIELD = 'email'  # Use email as login field
#     REQUIRED_FIELDS = []  # Remove username from required fields

#     def __str__(self):
#         return self.email
    
#     def save(self, *args, **kwargs):
#         if self.pk is None and self.password:
#             self.password_changed_date = now()
#         if not self.password.startswith('pbkdf2_sha256$'):
#             self.password = make_password(self.password)
#         super().save(*args, **kwargs)
    
#     def is_password_expired(self):
#         return (now() - self.password_changed_date) > datetime.timedelta(days=90)
    
#     def clean(self):
#         password_regex = r'^(?=.*[A-Z])(?=.*\d).{8,}$'
#         if not re.match(password_regex, self.password):
#             raise ValidationError("Password must be at least 8 characters long and contain...")
class CustomUser(AbstractUser):
    # Basic auth fields
    email = models.EmailField(unique=True,blank=True, null=True)
    password = models.CharField(max_length=128,blank=True, null=True)
    password_changed_date = models.DateTimeField(blank=True, null=True)
    username = None  # Remove username field
    
    # Firm information
    firm_name = models.CharField(max_length=255, blank=True, null=True)
    gst_no = models.CharField(max_length=15, blank=True, null=True, unique=True)
    membership_start_date = models.DateField(blank=True, null=True)
    membership_end_date = models.DateField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    # Contact person details
    contact_person_name = models.CharField(max_length=255, blank=True, null=True)
    contact_person_email = models.EmailField(blank=True, null=True)
    contact_person_phone = models.CharField(max_length=15, blank=True, null=True)
    # Activation fields
    is_active = models.BooleanField(default=False)
    activation_token = models.CharField(max_length=100, blank=True, null=True)
    token_created_at = models.DateTimeField(blank=True, null=True)

    # Auth configuration
    USERNAME_FIELD = 'email'  # Use email as login field
    REQUIRED_FIELDS = []  # Remove username from required fields

    def __str__(self):
        return self.email or self.firm_name
    
    def save(self, *args, **kwargs):
        if self.password:
            if not self.password.startswith('pbkdf2_sha256$'):
                self.password = make_password(self.password)
            if not self.pk or not self.password_changed_date:
                self.password_changed_date = now()
        super().save(*args, **kwargs)
    
    def is_password_expired(self):
        if not self.password_changed_date:
            return False
        return (now() - self.password_changed_date) > datetime.timedelta(days=90)
    
    def clean(self):
        # Password validation
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            password_regex = r'^(?=.*[A-Z])(?=.*\d).{8,}$'
            if not re.match(password_regex, self.password):
                raise ValidationError("Password must be at least 8 characters long and contain at least one uppercase letter and one digit")
        
        # GST number validation (basic format check)
        if self.gst_no:
            if not re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', self.gst_no):
                raise ValidationError("Invalid GST number format")
        
        # Membership date validation
        if self.membership_start_date and self.membership_end_date:
            if self.membership_end_date <= self.membership_start_date:
                raise ValidationError("Membership end date must be after start date")
            
class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    reset_token = models.CharField(max_length=100, blank=True)

    
    def is_valid(self):
        return (now() - self.created_at) < datetime.timedelta(minutes=10)

class PasswordHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    
class UserFormData(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="form_data")
    address = models.TextField()
    contact_email = models.EmailField()
    contact_name = models.CharField(max_length=255)
    description = models.TextField()
    gst = models.CharField(max_length=15, unique=True)
    pan = models.CharField(max_length=10, unique=True)
    hsn_codes = models.JSONField(default=list)
    organization = models.CharField(max_length=255)
    contact_mobile = models.CharField(max_length=15)
    whatsapp = models.CharField(max_length=15, blank=True, null=True)  # Optional field

    def __str__(self):
        return f"Data for {self.user.email if self.user else 'Unknown User'}"
