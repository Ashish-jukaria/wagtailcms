from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from users.models import CustomUser
import secrets
import string
from .views import send_email_via_sendgrid


@receiver(post_save, sender=CustomUser)
def handle_user_creation(sender, instance, created, **kwargs):
    if created:        
        success, _ = send_email_via_sendgrid(
            recipient_email=instance.email,
            subject='Your Account Credentials',
            message=f'Hello,\n\n'
                    f'Your account has been created with the following credentials:\n\n'
                    f'Email: {instance.email}\n'
                    'Please login and change your password immediately using forget password.'
        )
      