from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import RegisterForm
from .models import Location, Emailotp
from .utils import send_otp


# Registrierung (Location) + OTP senden
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_verified = False
            user.save()

            # OTP senden
            send_otp(user.email)

            # email in session speichern für verify page
            request.session["verify_email"] = user.email

            return redirect("verify_code")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


# OTP Code prüfen
def verify_code(request):
    email = request.session.get("verify_email")

    if not email:
        return redirect("register")

    if request.method == "POST":
        code = request.POST.get("code")

        otp = Emailotp.objects.filter(email=email, code=code).order_by("-created_at").first()

        if not otp:
            return render(request, "verify_code.html", {"error": "Wrong code"})

        if timezone.now() > otp.expires_at:
            return render(request, "verify_code.html", {"error": "Code expired"})

        # user verify
        user = Location.objects.get(email=email)
        user.is_verified = True
        user.save()

        # cleanup
        Emailotp.objects.filter(email=email).delete()

     
        request.session["user_email"] = email
        request.session.pop("verify_email", None)

        return redirect("home")

    return render(request, "verify_code.html")


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = Location.objects.filter(email=email, password=password).first()

        if not user:
            return render(request, "index.html", {"error": "Wrong email or password"})

        if not user.is_verified:
            request.session["verify_email"] = user.email
            send_otp(user.email)
            return redirect("verify_code")

        # login ok
        request.session["user_email"] = user.email
        return redirect("home")

    return render(request, "login.html")


def index(request):
    if not request.session.get("user_email"):
        return redirect("login")
    return render(request, "index.html")

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        user = Location.objects.filter(email=email).first()
        if not user:
            return render(request, {"error": "Email not found"})

        send_otp(email)
        request.session["reset_email"] = email
        return redirect("verify_code")

    return render(request, "forgot.html")