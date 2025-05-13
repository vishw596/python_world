# MESSAGES AND SHORTCUT IMPORT
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from mongoengine import ObjectIdField

# AUTHENTICATION IMPORT
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse

# MODEL IMPORT
from app.models import *

from datetime import datetime

# THIRD PARTY AND OTHER NECCESARRY UTILITY IMPORT
import yt_dlp
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
import string
import re
from .models import User
from bson import ObjectId
from bson import json_util
import json
from .models import User
import cloudinary.uploader
from bson import ObjectId
from .models import User, Post, Comment 

# HOME PAGE
def index(request):
    return render(request, "index.html")


# LOGIN PAGE
def loginUser(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        user = User.objects(username=username).first()
        if user and check_password(password=password, encoded=user.password):
            request.session["user_id"] = str(user.id)
            request.session["username"] = user.username
            return render(request, "index.html", {"user": user})
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

        user = User.objects.filter(username=username).count()
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
            return redirect("login")
        else:
            messages.error(
                request, "Username Already Exists! Please Try a different Username"
            )
            return redirect("signup")

    return render(request, "signup.html")

def feed(request):
    if "user_id" not in request.session:
        return redirect("login")
    
    return redirect("post")

    
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
            user.set_password(newPassword)
            user.save()
            
            try:
                send_mail(
                    "Your New Password for Python World",
                    f"""We’ve received a request to reset your password. Please find your new password below:
                    \nNew Password: {newPassword}\nIf you didn’t request this change or have any questions, please contact our support team immediately.\n\nStay secure,\nThe Python World Team""",
                    "official.pythonworld@gmail.com",
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send email: {e}")

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


# ABOUT PAGE
def article(request):
    if "user_id" not in request.session:
        return redirect("login")
    return render(request, "article.html")


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

    is_following = session_user in user.followers

    print(is_following)

    return render(request, "profile.html", {
        "user": user,
        "posts": posts,
        "session_username": session_username, 
        "is_following":is_following
    })


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


# SERVICE PAGE
def utils(request):
    if "user_id" not in request.session:
        return redirect("login")

    return render(request, "utils.html")

# QNA PAGE
def qna(request):
    if "user_id" not in request.session and (not request.GET.get("from")):

        return redirect("login")
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        question = QnA(
            title=title,
            content=content,
            posted_by=ObjectId(request.session.get("user_id")),
        )
        question.save()

    questions = QnA.objects()
    modified_ques = []
    if len(questions) > 0:
        for question in questions:
            userId = ObjectId(question.posted_by.id)
            user = User.objects.get(id=userId)
            que_dict = question.to_mongo().to_dict()
            que_dict["username"] = user.username
            que_dict["id"] = str(question.id)
            modified_ques.append(que_dict)

    if request.GET.get("from") == "js":
        if not request.GET.get("uid"):
            return redirect("login")
        else:
            obj_id = ObjectId(request.GET.get("qid"))
            que = QnA.objects.get(id=obj_id)
            answers = que.answers
            data = []
            for ans in answers:
                ans_dict = {}
                ans_dict["id"] = ans.id
                ans_dict["created_at"] = ans.created_at
                ans_dict["username"] = ans.created_by.username
                ans_dict["content"] = ans.answer_body
                data.append(ans_dict)
            return JsonResponse(json_util.dumps(data), safe=False)
    return render(request, "qna.html", {"questions": reversed(modified_ques)})

# ANSWER QUESTION
def que_answer(request):
    data = json.loads(request.body)["data"]
    if "uid" not in data:
        return redirect("login")
    answer_body = data["content"]
    created_by = ObjectId(data["uid"])
    for_question = ObjectId(data["qid"])
    answer_body = data["content"]
    answer = Answer(
        answer_body=answer_body, created_by=created_by, for_question=for_question
    )
    answer.save()
    question = QnA.objects.get(id=for_question)
    question.answers.append(answer)
    question.save()
    ans_dict = {
        "id": answer.id,
        "created_at": answer.created_at,
        "username": answer.created_by.username,
        "content": answer.answer_body,
    }
    return JsonResponse({"msg": json_util.dumps(ans_dict)})

# UPVOTE QUESTION
def upvote_que(request,que_id):
    qid = ObjectId(que_id)
    question = QnA.objects.get(id=qid)
    user = User.objects.get(id=ObjectId(request.session.get("user_id")))
    if user in question.upvotes:
        question.upvotes.remove(user)
        status = "removed"
    else:
        if user in question.downvotes:
            question.downvotes.remove(user)
        question.upvotes.append(user)
        status = "added"
    question.save()
    return JsonResponse({
            "status":status,
            "upvotes": len(question.upvotes),
            "downvotes": len(question.downvotes),
        })

# DOWNVOTE QUESTION
def downvote_que(request,que_id):
    qid = ObjectId(que_id)
    question = QnA.objects.get(id=qid)
    user = User.objects.get(id=ObjectId(request.session.get("user_id")))
    if user in question.downvotes:
        question.downvotes.remove(user)
        status = "removed"
    else:
        if user in question.upvotes:
            question.upvotes.remove(user)
        question.downvotes.append(user)
        status = "added"
    question.save()
    return JsonResponse({
            "status":status,
            "upvotes": len(question.upvotes),
            "downvotes": len(question.downvotes),
        })


# EDIT PROFILE
def editProfile(request):
    if "user_id" not in request.session:
        return redirect("login")
    if request.method=="POST":
        profileImageUrl=request.FILES.get("profilePicUrl")
        profileImage=""
        if profileImageUrl:
            upload_result = cloudinary.uploader.upload(profileImageUrl)
            profileImage = upload_result.get("secure_url")
        else :
            profileImage="ttt"
        user = User.objects.get(id=ObjectId(request.session.get("user_id")))
        user.profilePicUrl=profileImage
        if request.POST.get("username"):
            user.username=request.POST.get("username")
        if request.POST.get("email"):
            user.email=request.POST.get("email")
        if request.POST.get("bio"):
            user.bio=request.POST.get("bio")
        user.save()
        return redirect("profile",username=user.username)

    return render(request, "editProfile.html")


# POST
def post(request):
    if "user_id" not in request.session:
        return redirect("login")
    
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        tags = str(request.POST.get("tags"))
        taglist = tags.split(",")

        # Upload image to Cloudinary
        image = request.FILES.get("imageUrl")
        image_url = ""
        if image:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result.get("secure_url")
        else:
            image_url = "ttt"
        
        # Save post
        post = Post(
            title=title,
            content=content,
            posted_by=ObjectId(request.session.get("user_id")),
            tags=taglist,
            image_url=image_url
        )
        post.save()

       
        user = User.objects.get(id=ObjectId(request.session.get("user_id")))
        user.posts.append(post)
        user.save()

    posts = Post.objects()
    modified_posts = []
    if posts:
        for post in posts:
            userId = ObjectId(post.posted_by.id)
            user = User.objects.get(id=userId)
            post_dict = post.to_mongo().to_dict()
            post_dict["username"] = user.username
            post_dict["id"] = str(post.id)

            comment_dict = [Comment.objects.get(id=comment.id) for comment in post.comments]
            post_dict["comments"] = comment_dict
            
            modified_posts.append(post_dict)

    user = User.objects.get(id=ObjectId(request.session.get("user_id")))

    return render(request, "post.html", {"posts": list(reversed(modified_posts)), "user":user})


# LIKE POST
def like_post(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(id=ObjectId(post_id))
        user = User.objects.get(id=ObjectId(request.session.get("user_id")))
        if not user:
            return JsonResponse({"error": "User not authenticated"}, status=403)

        try:
            post = Post.objects.get(id=ObjectId(post_id))
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)
        liked = False       
        if user in post.likes:
            post.likes.remove(user)
        else:
            post.likes.append(user)
            liked = True

        post.save()
        return JsonResponse({
            "liked":liked,
            "like_count":len(post.likes)
        })
    return JsonResponse({"error": "Invalid request method"}, status=405)


# COMMENT POST
def comment_post(request, post_id):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        comment_body = request.POST.get("content", "").strip()
        print(comment_body)
        if not comment_body:
            return JsonResponse({"error": "Empty comment."}, status=400)

        post = Post.objects.get(id=ObjectId(post_id))
        comment = Comment(
            comment_body=comment_body,
            created_by=ObjectId(user_id),
            for_post=ObjectId(post_id),
        )
        comment.save()

        post.comments.append(comment.id)
        post.save()

        return JsonResponse({
            "comment_body": comment.comment_body,
            "created_at": datetime.strftime(comment.created_at, "%b %d, %Y"),
            "username": comment.created_by.username,
            "initial": comment.created_by.username[0].upper()
        })