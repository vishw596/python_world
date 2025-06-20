from django.shortcuts import render
from app.models import *
from authlib.integrations.django_client import OAuth
import traceback
from django.conf import settings

from django.http import HttpResponse, JsonResponse, HttpResponseServerError
from django.conf import settings
from authlib.integrations.django_client import OAuth
from django.shortcuts import redirect, render
from django.contrib import messages
import traceback
from django.contrib.auth.hashers import make_password, check_password
import re
from django.http import HttpResponseServerError
import string
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from threading import Thread

def get_oauth_client(name):

    oauth = OAuth()
    if name == "google":
        oauth.register(
            name="google",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url=settings.GOOGLE_META_URL,
            client_kwargs={
                "scope": "openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read"
            },
        )
    if name == "github":
        oauth.register(
            "github",
            client_id=settings.GITHUB_CLIENT_ID,
            client_secret=settings.GITHUB_CLIENT_SECRET,
            access_token_url="https://github.com/login/oauth/access_token",
            access_token_params=None,
            authorize_url="https://github.com/login/oauth/authorize",
            authorize_params=None,
            api_base_url=settings.GITHUB_API_URL,
            client_kwargs={"scope": "read:user user:email"},
        )
    if name == "x":
        oauth.register(
            name="x",
            client_id=settings.X_CLIENT_ID,
            client_secret=settings.X_CLIENT_SECRET,
            request_token_url=settings.X_REQUEST_TOKEN_URL,
            authorize_url=settings.X_AUTHORIZE_URL,
            access_token_url=settings.X_ACCESS_TOKEN_URL,
            api_base_url=settings.X_API_URL,
            client_kwargs=None,
        )
    return oauth

def x_login(request):
   try:
        oauth = get_oauth_client("x")
        x = oauth.create_client("x")
        # OAuth 1.0a requires token fetching step
        redirect_uri = settings.X_CALLBACK_URI
        return x.authorize_redirect(request, redirect_uri)
   except Exception as e:
        print("Error during X login:", e)
        return HttpResponseServerError("X login failed")

def x_callback(request):
    try:
        oauth = get_oauth_client("x")
        x = oauth.create_client("x")
        token = x.authorize_access_token(request)  # exchanges oauth_token+verifier for access token

        user_info_resp = x.get(
            "account/verify_credentials.json",
            params={"include_email": "true"},
            token=token,
        )

        user_info = user_info_resp.json()
        print("User Info from X:", user_info)

        email = user_info.get("email")
        if not email:
            return HttpResponse("We could not access your email from X. Please use another login method.")

        x_id = user_info.get("id_str")
        username = user_info.get("screen_name")
        name = user_info.get("name")
        picture = user_info.get("profile_image_url_https")

        return oauth_handler(
            request=request,
            email=email,
            auth_provider="x",
            picture=picture,
            username=username
        )
    except Exception as e:
        print("X OAuth Callback Error:", e)
        traceback.print_exc()
        return redirect("login")

def find_user_email(email):
    user = User.objects(email=email).first()
    return user

def google_login(request):
    oauth = get_oauth_client("google")
    return oauth.google.authorize_redirect(request, settings.GOOGLE_REDIRECT_URL)

def oauth_handler(request, email, auth_provider, picture, username=None):
    print("Method invoked")
    print(username)
    try:
        db_user = find_user_email(email=email)
        if not db_user:
            user = User(
                username=username or email,
                email=email,
                auth_provider=auth_provider,
                profilePicUrl=picture or "",
            )
            user.save()
            request.session["user_id"] = str(user.id)
            request.session["username"] = user.username
            
            subject = "🎉 Welcome To Python World"
            from_email = "your_email@gmail.com"
            to_email = [user.email]

            html_content = f"""
            <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Python World!</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
</head>
<body style="margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; background-color: #0f172a; color: #e2e8f0; line-height: 1.6;">
    
    <!-- Outer Container -->
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #0f172a; padding: 20px 0;">
        <tr>
            <td align="center">
                
                <!-- Main Email Container -->
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="max-width: 600px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 16px; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
                    
                    <!-- Header Section -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #3498db, #6366f1); padding: 40px 32px; text-align: center; position: relative;">
                            
                            <!-- Animated Background Effect -->
                            <div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); pointer-events: none;"></div>
                            
                            <!-- Logo Section -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td align="center" style="position: relative; z-index: 2;">
                                        
                                        
                                        <!-- Logo Text -->
                                        <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: #093793; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                                            Python<span style="color:rgb(6, 205, 69);"> World</span>
                                        </h1>
                                        
                                        <!-- Welcome Message -->
                                        <p style="margin: 16px 0 0 0; color: white; font-size: 18px; font-weight: 500; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
                                            🎉 Welcome to Python World! 🎉
                                        </p>
                                        
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Body Section -->
                    <tr>
                        <td style="padding: 32px;">
                            
                            <!-- Main Notification Card -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: rgba(30, 41, 59, 0.8); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 24px;">
                                <tr>
                                    <td style="padding: 24px;">
                                        
                                        <!-- Greeting -->
                                        <p style="margin: 0 0 16px 0; font-size: 18px; color: #e2e8f0;">
                                            Hi <span style="color: #2ecc71; font-weight: 600;">{user.username}</span>,
                                        </p>
                                        
                                        <!-- Welcome Content Box -->
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background: linear-gradient(135deg, rgba(52, 152, 219, 0.15), rgba(99, 102, 241, 0.15)); border-left: 4px solid #3498db; border-radius: 8px; margin: 16px 0;">
                                            <tr>
                                                <td style="padding: 16px;">
                                                    <p style="margin: 0 0 8px 0; font-size: 16px; color: white; font-weight: 500;">
                                                        🚀 <strong style="color: #2ecc71;">Python World</strong> Welcomes You!
                                                        <br>
                                                        <span style="color: #3498db; font-weight: 600; font-style: italic;">"{user.username}"</span>
                                                    </p>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                        <!-- Impact Message -->
                                        <p style="margin: 16px 0; color: #94a3b8; font-size: 16px; text-align: center;">
                                            🐍 Your journey into the Python community starts here! 🌟
                                            <br>
                                            <span style="color: #ffd43b;">✨ Get ready to code, learn, and connect! ✨</span>
                                        </p>
                                        
                                        <!-- CTA Button -->
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                            <tr>
                                                <td align="center" style="padding: 16px 0;">
                                                    <a href="http://pythonworld.mooo.com" style="display: inline-block; background: linear-gradient(135deg, #3498db, #6366f1); color: white; padding: 14px 28px; border-radius: 50px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); transition: all 0.3s ease;">
                                                        🌍 Explore Python World
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                        
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Divider -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td style="height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); margin: 24px 0;"></td>
                                </tr>
                            </table>
                            
                            <!-- Additional Info Section -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background: linear-gradient(135deg, rgba(46, 204, 113, 0.1), rgba(52, 152, 219, 0.1)); border-radius: 12px; border: 1px solid rgba(46, 204, 113, 0.2);">
                                <tr>
                                    <td style="padding: 20px; text-align: center;">
                                        <h3 style="margin: 0 0 12px 0; color: #2ecc71; font-size: 18px;">🎯 What's Next?</h3>
                                        <p style="margin: 0; color: #94a3b8; font-size: 14px; line-height: 1.6;">
                                            🔍 Explore amazing Python projects<br>
                                            💬 Connect with fellow developers<br>
                                            📚 Share your knowledge and learn from others<br>
                                            🏆 Build your developer profile
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                        </td>
                    </tr>
                    
                    <!-- Footer Section -->
                    <tr>
                        <td style="background-color: #020617; padding: 24px 32px; text-align: center; border-top: 1px solid rgba(255, 255, 255, 0.05);">
                            
                            <p style="margin: 0 0 8px 0; font-size: 14px; color: #94a3b8;">
                                This is an automatic notification from Python World
                            </p>
                            <p style="margin: 0 0 16px 0; font-size: 12px; color: #64748b;">
                                © 2025 Python World. All rights reserved.
                            </p>
                            
                            <!-- Social Links -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td align="center">
                                        <table role="presentation" cellspacing="0" cellpadding="8" border="0">
                                            <tr>
                                                <td>
                                                    <a href="#" style="display: inline-block; width: 36px; height: 36px; background: rgba(30, 41, 59, 0.5); border-radius: 50%; color: #94a3b8; text-decoration: none; text-align: center; line-height: 36px; transition: all 0.3s ease;">📧</a>
                                                </td>
                                                <td>
                                                    <a href="#" style="display: inline-block; width: 36px; height: 36px; background: rgba(30, 41, 59, 0.5); border-radius: 50%; color: #94a3b8; text-decoration: none; text-align: center; line-height: 36px; transition: all 0.3s ease;">🐦</a>
                                                </td>
                                                <td>
                                                    <a href="#" style="display: inline-block; width: 36px; height: 36px; background: rgba(30, 41, 59, 0.5); border-radius: 50%; color: #94a3b8; text-decoration: none; text-align: center; line-height: 36px; transition: all 0.3s ease;">X</a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                        </td>
                    </tr>
                    
                </table>
                
            </td>
        </tr>
    </table>
    
    <!-- Mobile Responsive Styles -->
    <style>
        @media only screen and (max-width: 600px) {{
            .email-container {{
                width: 100% !important;
                margin: 10px !important;
            }}
            
            .email-header {{
                padding: 24px 20px !important;
            }}
            
            .email-body {{
                padding: 20px !important;
            }}
            
            .logo {{
                font-size: 24px !important;
            }}
            
            .notification-icon {{
                font-size: 32px !important;
            }}
            
            .greeting {{
                font-size: 16px !important;
            }}
            
            .notification-text {{
                font-size: 14px !important;
            }}
            
            .cta-button {{
                padding: 12px 20px !important;
                font-size: 14px !important;
            }}
            
            .footer-text {{
                font-size: 12px !important;
            }}
        }}
    </style>
    
</body>
</html>
            """

            # Plain text fallback
            text_content = f"""
            Hi there 👋,

            Welcome to Python World!

            We're excited to have you on board. Get ready to explore, learn, and grow with us in the world of Python programming.

            Happy coding! 🚀

            — The Python World Team

            Check it out on your profile!

            ---
            This is an automatic notification from Python World.
            © 2025 Python World. All rights reserved.
            """

            try:
                send_email_async(subject, text_content, html_content, from_email, to_email, user)
            
            except Exception as e:
                print(f"Failed to send email: {str(e)}")
            return redirect("/")
        elif db_user.email == email and db_user.auth_provider == auth_provider:
            request.session["user_id"] = str(db_user.id)
            request.session["username"] = db_user.username
            return redirect("/")
        else:
            messages.error(
                request,
                f"You are signed in on our website using email {email} via {db_user.auth_provider}",
            )
            return redirect("login")
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        messages.error(request,"Login failed")
        return redirect("login")

def google_callback(request):
    try:
        oauth = get_oauth_client("google")
        token = oauth.google.authorize_access_token(request)
        user_info = oauth.google.userinfo(token=token)

        email = user_info["email"]
        pic = user_info["picture"]
        
        username = email.split("@")[0]  # ← get the part before @
        print("Google username:", username)
        print("Google profile pic:", pic)

        return oauth_handler(
            request=request,
            email=email,
            auth_provider="google",
            picture=pic,
            username=username,  # pass username if needed
        )

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        messages.error(request, "Login failed! Please Try Again")
        return redirect("/login")


def github_login(request):
    print("Request reached")
    try:
        oauth = get_oauth_client("github")
        return oauth.github.authorize_redirect(
            request, settings.GITHUB_REDIRECT_URL, prompt="consent"
        )
    except Exception as e:
        print("ERROR " + e)
        messages.error(request,"Login failed")
        return redirect("/login")

def github_callback(request):
    try:
        oauth = get_oauth_client("github")
        token = oauth.github.authorize_access_token(request)
        print(token)
        profileRes = oauth.github.get(f"{settings.GITHUB_API_URL}user", token=token)
        profileJson = profileRes.json()
        print(profileJson)
        emailRes = oauth.github.get(
            f"{settings.GITHUB_API_URL}user/emails", token=token
        )
        emailList = emailRes.json()
        if len(emailList) == 0:
            messages.error(
                request,
                "You have not added email in your github account please add email to github to login",
            )
            return redirect("/")
        email = emailList[0]["email"]
        username = profileJson["login"]
        pic = profileJson["avatar_url"]
        return oauth_handler(
            request=request,
            email=email,
            auth_provider="github",
            picture=pic,
            username=username,
        )
    except Exception as e:
        print("ERROR: ", e)
        messages.error(request,"Login failed")
        return redirect("/login")

# LOGIN PAGE
def loginUser(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        user = User.objects(username=username).first()
        if user and check_password(password=password, encoded=user.password):
            request.session["user_id"] = str(user.id)
            request.session["username"] = user.username
            return redirect("/")
        else:
            messages.error(request, "User Id or Password did not matched")
            return render(request, "login.html")

    return render(request, "login.html")

# SIGNUP PAGE
def signupUser(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        pass1 = request.POST.get("password")

        # consent_given = request.POST.get('consent') == 'on'

        user = User.objects.filter(username=username).count()

        email_exists = User.objects.filter(email=email).count()
        if email_exists:
            messages.error(request, "Email Already Exists! Try a different Email")
            return redirect("signup")


        if not user:
            email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(email_regex, email):
                messages.error(request, "Please Enter Valid Email Address")
                return redirect("signup")

            

            if len(pass1) < 8:
                messages.error(
                    request, "Password length must be grater or equal to 8 Characters"
                )
                return redirect("signup")
            hashedPass = make_password(password=pass1, salt="12")
            user = User(username=username, email=email, password=hashedPass)
            user.save()

            subject = "🎉 Welcome To Python World"
            from_email = "your_email@gmail.com"
            to_email = [user.email]

            html_content = f"""
            <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Welcome to Python World!</title>
                    <!--[if mso]>
                    <noscript>
                        <xml>
                            <o:OfficeDocumentSettings>
                                <o:PixelsPerInch>96</o:PixelsPerInch>
                            </o:OfficeDocumentSettings>
                        </xml>
                    </noscript>
                    <![endif]-->
                </head>
                <body style="margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; background-color: #0f172a; color: #e2e8f0; line-height: 1.6;">
                    
                    <!-- Outer Container -->
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #0f172a; padding: 20px 0;">
                        <tr>
                            <td align="center">
                                
                                <!-- Main Email Container -->
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="max-width: 600px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 16px; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1);">
                                    
                                    <!-- Header Section -->
                                    <tr>
                                        <td style="background: linear-gradient(135deg, #3498db, #6366f1); padding: 40px 32px; text-align: center; position: relative;">
                                            
                                            <!-- Animated Background Effect -->
                                            <div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); pointer-events: none;"></div>
                                            
                                            <!-- Logo Section -->
                                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                                <tr>
                                                    <td align="center" style="position: relative; z-index: 2;">
                                                        
                                                        
                                                        <!-- Logo Text -->
                                                        <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: #093793; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                                                            Python<span style="color:rgb(6, 205, 69);"> World</span>
                                                        </h1>
                                                        
                                                        <!-- Welcome Message -->
                                                        <p style="margin: 16px 0 0 0; color: white; font-size: 18px; font-weight: 500; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
                                                            🎉 Welcome to Python World! 🎉
                                                        </p>
                                                        
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                    
                                    <!-- Body Section -->
                                    <tr>
                                        <td style="padding: 32px;">
                                            
                                            <!-- Main Notification Card -->
                                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: rgba(30, 41, 59, 0.8); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 24px;">
                                                <tr>
                                                    <td style="padding: 24px;">
                                                        
                                                        <!-- Greeting -->
                                                        <p style="margin: 0 0 16px 0; font-size: 18px; color: #e2e8f0;">
                                                            Hi <span style="color: #2ecc71; font-weight: 600;">{user.username}</span>,
                                                        </p>
                                                        
                                                        <!-- Welcome Content Box -->
                                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background: linear-gradient(135deg, rgba(52, 152, 219, 0.15), rgba(99, 102, 241, 0.15)); border-left: 4px solid #3498db; border-radius: 8px; margin: 16px 0;">
                                                            <tr>
                                                                <td style="padding: 16px;">
                                                                    <p style="margin: 0 0 8px 0; font-size: 16px; color: white; font-weight: 500;">
                                                                        🚀 <strong style="color: #2ecc71;">Python World</strong> Welcomes You!
                                                                        <br>
                                                                        <span style="color: #3498db; font-weight: 600; font-style: italic;">"{user.username}"</span>
                                                                    </p>
                                                                </td>
                                                            </tr>
                                                        </table>
                                                        
                                                        <!-- Impact Message -->
                                                        <p style="margin: 16px 0; color: #94a3b8; font-size: 16px; text-align: center;">
                                                            🐍 Your journey into the Python community starts here! 🌟
                                                            <br>
                                                            <span style="color: #ffd43b;">✨ Get ready to code, learn, and connect! ✨</span>
                                                        </p>
                                                        
                                                        <!-- CTA Button -->
                                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                                            <tr>
                                                                <td align="center" style="padding: 16px 0;">
                                                                    <a href="http://pythonworld.mooo.com" style="display: inline-block; background: linear-gradient(135deg, #3498db, #6366f1); color: white; padding: 14px 28px; border-radius: 50px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); transition: all 0.3s ease;">
                                                                        🌍 Explore Python World
                                                                    </a>
                                                                </td>
                                                            </tr>
                                                        </table>
                                                        
                                                    </td>
                                                </tr>
                                            </table>
                                            
                                            <!-- Divider -->
                                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                                <tr>
                                                    <td style="height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); margin: 24px 0;"></td>
                                                </tr>
                                            </table>
                                            
                                            <!-- Additional Info Section -->
                                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background: linear-gradient(135deg, rgba(46, 204, 113, 0.1), rgba(52, 152, 219, 0.1)); border-radius: 12px; border: 1px solid rgba(46, 204, 113, 0.2);">
                                                <tr>
                                                    <td style="padding: 20px; text-align: center;">
                                                        <h3 style="margin: 0 0 12px 0; color: #2ecc71; font-size: 18px;">🎯 What's Next?</h3>
                                                        <p style="margin: 0; color: #94a3b8; font-size: 14px; line-height: 1.6;">
                                                            🔍 Explore amazing Python projects<br>
                                                            💬 Connect with fellow developers<br>
                                                            📚 Share your knowledge and learn from others<br>
                                                            🏆 Build your developer profile
                                                        </p>
                                                    </td>
                                                </tr>
                                            </table>
                                            
                                        </td>
                                    </tr>
                                    
                                    <!-- Footer Section -->
                                    <tr>
                                        <td style="background-color: #020617; padding: 24px 32px; text-align: center; border-top: 1px solid rgba(255, 255, 255, 0.05);">
                                            
                                            <p style="margin: 0 0 8px 0; font-size: 14px; color: #94a3b8;">
                                                This is an automatic notification from Python World
                                            </p>
                                            <p style="margin: 0 0 16px 0; font-size: 12px; color: #64748b;">
                                                © 2025 Python World. All rights reserved.
                                            </p>
                                            
                                            <!-- Social Links -->
                                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                                <tr>
                                                    <td align="center">
                                                        <table role="presentation" cellspacing="0" cellpadding="8" border="0">
                                                            <tr>
                                                                <td>
                                                                    <a href="#" style="display: inline-block; width: 36px; height: 36px; background: rgba(30, 41, 59, 0.5); border-radius: 50%; color: #94a3b8; text-decoration: none; text-align: center; line-height: 36px; transition: all 0.3s ease;">📧</a>
                                                                </td>
                                                                <td>
                                                                    <a href="#" style="display: inline-block; width: 36px; height: 36px; background: rgba(30, 41, 59, 0.5); border-radius: 50%; color: #94a3b8; text-decoration: none; text-align: center; line-height: 36px; transition: all 0.3s ease;">🐦</a>
                                                                </td>
                                                                <td>
                                                                    <a href="#" style="display: inline-block; width: 36px; height: 36px; background: rgba(30, 41, 59, 0.5); border-radius: 50%; color: #94a3b8; text-decoration: none; text-align: center; line-height: 36px; transition: all 0.3s ease;">X</a>
                                                                </td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                </tr>
                                            </table>
                                            
                                        </td>
                                    </tr>
                                    
                                </table>
                                
                            </td>
                        </tr>
                    </table>
                    
                    <!-- Mobile Responsive Styles -->
                    <style>
                        @media only screen and (max-width: 600px) {{
                            .email-container {{
                                width: 100% !important;
                                margin: 10px !important;
                            }}
                            
                            .email-header {{
                                padding: 24px 20px !important;
                            }}
                            
                            .email-body {{
                                padding: 20px !important;
                            }}
                            
                            .logo {{
                                font-size: 24px !important;
                            }}
                            
                            .notification-icon {{
                                font-size: 32px !important;
                            }}
                            
                            .greeting {{
                                font-size: 16px !important;
                            }}
                            
                            .notification-text {{
                                font-size: 14px !important;
                            }}
                            
                            .cta-button {{
                                padding: 12px 20px !important;
                                font-size: 14px !important;
                            }}
                            
                            .footer-text {{
                                font-size: 12px !important;
                            }}
                        }}
                    </style>
                    
                </body>
                </html>
                            """

            # Plain text fallback
            text_content = f"""
            Hi there 👋,

            Welcome to Python World!

            We're excited to have you on board. Get ready to explore, learn, and grow with us in the world of Python programming.

            Happy coding! 🚀

            — The Python World Team

            Check it out on your profile!

            ---
            This is an automatic notification from Python World.
            © 2025 Python World. All rights reserved.
            """

            try:
                send_email_async(subject, text_content, html_content, from_email, to_email, user)
            
            except Exception as e:
                print(f"Failed to send email: {str(e)}")
            return redirect("login")
        else:
            messages.error(
                request, "Username Already Exists! Please Try a different Username"
            )
            return redirect("signup")

    return render(request, "signup.html")

# LOGOUT PAGE
def logoutUser(request):

    request.session.flush()
    messages.success(request, "Logged Out Successfully")
    return redirect("login")

# FORGOT PASSWORD PAGE
def forgotpass(request):

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        try:
            user = User.objects.get(username=username, email=email)
            newPassword = get_random_string(
                length=8, allowed_chars=string.ascii_letters + string.digits
            )
            user.password = make_password(newPassword)
            user.save()
            
            subject = "🔒 New Password Request | Python World"
            from_email = "your_email@gmail.com"
            to_email = [user.email]

            html_content = f"""
            <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python World Password Reset</title>
</head>
<body style="margin: 0; padding: 20px; font-family: Arial, Helvetica, sans-serif; background-color: #f8fafc; color: #1e293b; line-height: 1.6;">
    <!-- Main Container -->
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;">
        <!-- Header -->
        <tr>
            <td style="background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%); padding: 40px 30px; text-align: center; color: white;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="width: 100%;">
                    <tr>
                        <td style="text-align: center;">
                            <!-- Logo -->
                            <div style="font-size: 28px; font-weight: bold; margin-bottom: 8px;">
                                <span style="color: #ffffff;">Python</span>
                                <span style="color: #10b981;"> World</span>
                            </div>
                            <!-- Tagline -->
                            <p style="margin: 0; font-size: 16px; opacity: 0.9;">Where Python Developers Thrive</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <!-- Main Content -->
        <tr>
            <td style="padding: 40px 30px;">
                <!-- Notification Card -->
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="width: 100%; background-color: #f8fafc; border-radius: 12px; border: 2px solid #e2e8f0;">
                    <tr>
                        <td style="padding: 24px;">
                            <!-- Greeting -->
                            <p style="margin: 0 0 20px 0; font-size: 18px; color: #1e293b;">
                                Hi <span style="color: #10b981; font-weight: bold;">{username}</span>,
                            </p>
                            
                            <!-- Password Reset Content -->
                            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left: 4px solid #f59e0b; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                <p style="margin: 0 0 15px 0; font-size: 16px; color: #1e293b;">
                                    <strong style="color: #dc2626;">🔐 Password Reset Request</strong>
                                </p>
                                <p style="margin: 0; font-size: 15px; color: #374751;">
                                    We've received a request to reset your password. Please find your new password below:
                                </p>
                            </div>
                            
                            <!-- New Password Display -->
                            <div style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); border: 2px solid #10b981; padding: 20px; border-radius: 12px; margin: 25px 0; text-align: center;">
                                <p style="margin: 0 0 10px 0; font-size: 14px; color: #065f46; font-weight: bold;">
                                    Your New Password:
                                </p>
                                <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #10b981; margin: 10px 0;">
                                    <code style="font-size: 18px; color: #1e293b; font-weight: bold; letter-spacing: 1px;">{newPassword}</code>
                                </div>
                                <p style="margin: 10px 0 0 0; font-size: 12px; color: #047857;">
                                    💡 We recommend changing this password after logging in
                                </p>
                            </div>
                            
                            <!-- Login Button -->
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="https://pythonworld.mooo.com/login" style="display: inline-block; background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%); color: white; padding: 14px 28px; border-radius: 25px; text-decoration: none; font-weight: bold; font-size: 16px; box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);">
                                    Login to Your Account →
                                </a>
                            </div>
                        </td>
                    </tr>
                </table>
                
                <!-- Divider -->
                <div style="height: 1px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 30px 0;"></div>
                
                <!-- Security Alert Section -->
                <div style="text-align: center; margin: 30px 0;">
                    <div style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); padding: 20px; border-radius: 12px; border: 1px solid #fca5a5;">
                        <p style="margin: 0 0 12px 0; color: #dc2626; font-size: 16px; font-weight: bold;">
                            🚨 Security Notice
                        </p>
                        <p style="margin: 0; color: #7f1d1d; font-size: 14px;">
                            If you didn't request this password reset, please contact our support team immediately to secure your account.
                        </p>
                    </div>
                </div>
                
                <!-- Tips Section -->
                <div style="background-color: #f1f5f9; padding: 20px; border-radius: 10px; border: 1px solid #cbd5e1; margin: 20px 0;">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="width: 100%;">
                        <tr>
                            <td style="width: 60px; text-align: center; vertical-align: top; padding-right: 15px;">
                                <div style="font-size: 32px;">🔒</div>
                            </td>
                            <td style="vertical-align: top;">
                                <p style="margin: 0 0 8px 0; color: #1e293b; font-size: 14px; font-weight: bold;">
                                    Security Best Practices:
                                </p>
                                <p style="margin: 0; color: #64748b; font-size: 13px;">
                                    • Change your password after logging in<br>
                                    • Use a strong, unique password<br>
                                    • Enable two-factor authentication if available
                                </p>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <!-- Support Section -->
                <div style="text-align: center; margin: 25px 0;">
                    <p style="margin: 0; color: #64748b; font-size: 14px;">
                        Need help? Contact our support team at 
                        <a href="mailto:official.pythonworld@gmail.com" style="color: #1e40af; text-decoration: none; font-weight: bold;">official.pythonworld@gmail.com</a>
                    </p>
                </div>
            </td>
        </tr>
        
        <!-- Footer -->
        <tr>
            <td style="background-color: #1e293b; padding: 30px; text-align: center; color: #94a3b8;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="width: 100%;">
                    <tr>
                        <td style="text-align: center;">
                            <!-- Social Links -->
                            
                            <!-- Footer Text -->
                            <p style="margin: 0 0 10px 0; font-size: 14px; color: #9ca3af;">
                                This is an automatic notification from Python World
                            </p>
                            <p style="margin: 0 0 15px 0; font-size: 12px; color: #6b7280;">
                                © 2025 Python World. All rights reserved.
                            </p>
                            
                            <!-- Unsubscribe -->
                            <p style="margin: 0; font-size: 11px; color: #6b7280;">
                                <a href="#" style="color: #9ca3af; text-decoration: underline;">Unsubscribe</a> | 
                                <a href="#" style="color: #9ca3af; text-decoration: underline;">Manage Notifications</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    
    <!-- Mobile Styles -->
    <style>
        @media only screen and (max-width: 600px) {{
            .email-container {{
                width: 100% !important;
                margin: 10px !important;
            }}
            .header-padding {{
                padding: 30px 20px !important;
            }}
            .content-padding {{
                padding: 30px 20px !important;
            }}
            .logo-text {{
                font-size: 24px !important;
            }}
        }}
    </style>
</body>
</html>
 """

            # Plain text fallback
            text_content = f"""This is a Hidden Notification from Python World
            """

            try:
                send_email_async(subject, text_content, html_content, from_email, to_email, user)
            
            except Exception as e:
                print(f"Failed to send email: {str(e)}")
                return redirect("login")

            return render(
                request,
                "forgot.html",
                {"message": "Updated Password sent to your email!"},
            )

        except User.DoesNotExist:

            return render(
                request,
                "forgot.html",
                {"message": "User with the given username and email not found!"},
            )
    return render(request, "forgot.html")

# SEND MAIL ASYNC
def send_email(subject, text_content, html_content, from_email, to_email, post):
    try:
        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        # print(f"Email sent successfully to {post.posted_by.email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def send_email_async(subject, text_content, html_content, from_email, to_email, post):
    Thread(target=send_email, args=(subject, text_content, html_content, from_email, to_email, post)).start()
