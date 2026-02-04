import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from .models import Emailotp

def send_otp(email):
    code = str(random.randint(100000, 999999))

    Emailotp.objects.create(
        email=email,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=10)
    )

    send_mail(
        subject="Verification code",
        message=f"Your code is: {code}",
        from_email=None,
        recipient_list=[email],
    )
