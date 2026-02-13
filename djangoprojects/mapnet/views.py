from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import RegisterForm
from .models import Location, Emailotp
from .utils import send_otp


# Registrierung  + OTP senden
def register(request):
    # Post
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_verified = False
            user.save()

            # OTP senden
            send_otp(user.email)
            
            request.session["verify_email"] = user.email

            return redirect("verify_code")
            
            # Get
    else:
        form = RegisterForm(request.GET)

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

        # Decide what this OTP is for
        flow = request.session.get("otp_flow")

        if flow == "reset":
            # OTP ok -> go to reset password page
            Emailotp.objects.filter(email=email).delete()
            request.session.pop("verify_email", None)
            request.session.pop("otp_flow", None)
            return redirect("reset_password")

        # normal verify (register/login)
        user = Location.objects.get(email=email)
        user.is_verified = True
        user.save()

        Emailotp.objects.filter(email=email).delete()

        request.session["user_email"] = email
        request.session.pop("verify_email", None)
        request.session.pop("otp_flow", None)

        return redirect("home")

    return render(request, "verify_code.html")



def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = Location.objects.filter(email=email, password=password).first()

            if not user:
                return render(request, "login.html", {"form": form, "error": "Wrong email or password"})

            if not user.is_verified:
                request.session["verify_email"] = user.email
                send_otp(user.email)
                return redirect("verify_code")

            
            request.session["user_email"] = user.email
            return redirect("home")

       
        return render(request, "login.html", {"form": form})

    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})

def index(request):
    if not request.session.get("user_email"):
        return redirect("login")
    return render(request, "index.html")

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        user = Location.objects.filter(email=email).first()
        if not user:
            return render(request, "forgot.html", {"error": "Email not found"})

        send_otp(email)
        request.session["otp_flow"] = "reset"
        request.session["verify_email"] = email
        request.session["reset_email"] = email
        return redirect("verify_code")

    return render(request, "forgot.html")

def reset_password(request):
    email = request.session.get("reset_email")
    if not email:
        return redirect("forgot_password")

    if request.method == "POST":
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            return render(request, "reset_password.html", {"error": "Passwords do not match"})

        user = Location.objects.filter(email=email).first()
        if not user:
            return render(request, "reset_password.html", {"error": "Email not found"})

        user.password = password
        user.save()

        request.session.pop("reset_email", None)
        return redirect("login")

    return render(request, "reset_password.html")

