# MESSAGES AND SHORTCUT IMPORT
from django.contrib import messages
from django.shortcuts import render, redirect

# AUTHENTICATION IMPORT
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

from app.models import *
from bson import ObjectId
import cloudinary.uploader

# PROFILE PAGE
def profile(request, username):
    if "user_id" not in request.session:
        return redirect("login")

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse("User not found", status=404)

    session_username = request.session.get("username")
    session_user=User.objects.get(username=session_username)
    posts = Post.objects(posted_by=ObjectId(user.id)).order_by("-created_at").limit(5)
    followers = list(reversed(list(user.followers)))
    print(type(followers))
    followings = list(reversed(list(user.followings)))
    print(followings)
    is_following = session_user in user.followers

    print(is_following)

    return render(request, "profile.html", {
        "user": user,
        "posts": posts,
        "session_username": session_username, 
        "is_following":is_following,
        "followers":followers,
        "followings":followings
    })

# EDIT PROFILE
def editProfile(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = User.objects.get(id=ObjectId(request.session.get("user_id")))

    if request.method == "POST":
        profileImage = ""

        profileImageUrl = request.FILES.get("profilePicUrl")
        if profileImageUrl:
            upload_result = cloudinary.uploader.upload(profileImageUrl)
            profileImage = upload_result.get("secure_url")
            user.profilePicUrl = profileImage

        if request.POST.get("username"):
            user.username = request.POST.get("username")
        if request.POST.get("email"):
            user.email = request.POST.get("email")
        if request.POST.get("bio"):
            user.bio = request.POST.get("bio")

        user.save()
        request.session["username"] = user.username
        return redirect("profile", username=user.username)

    # Handle GET request: return current user data to the template
    context = {
        "user_data": {
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "profilePicUrl": user.profilePicUrl
        }
    }

    return render(request, "editProfile.html", context)


# FOLLOW UNFOLLOW
def followUnfollow(request, username):
    if "username" not in request.session:
        return redirect("login")

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse("User not found", status=404)

    session_username = request.session.get("username")

    try:
        loggedInUser = User.objects.get(username=session_username)
    except User.DoesNotExist:
        return HttpResponse("Logged-in user not found", status=404)

    # Toggle follow/unfollow
    if loggedInUser in user.followers:
        user.followers.remove(loggedInUser)
        loggedInUser.followings.remove(user)
    else:
        user.followers.append(loggedInUser)
        loggedInUser.followings.append(user)

    user.save()
    loggedInUser.save()

    return redirect("profile", username=username)