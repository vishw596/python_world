from calendar import c
from django.shortcuts import render, redirect
from app.models import *
# HOME PAGE
def index(request):

    users = User.objects.count()
    posts = Post.objects.count()
    comments = Comment.objects.count()
    questions = QnA.objects.count()
    utilities = Utility.objects.count()
    answers = Answer.objects.count()
    articles = Article.objects.count()
    return render(request, "index.html",{"users":users,"posts":posts,"comments":comments,"questions":questions,"utilities":utilities,"answers":answers,"articles":articles})


def notificationSetting(request):

    if "user_id" not in request.session:
        return redirect("login")

    user = User.objects.get(id=request.session["user_id"])

    if request.method == "POST":
        user.notifications=request.POST.get("notifications")
        user.newsletter=request.POST.get("newsletter")

        if user.notifications=="True":
            user.notifications=True
        else:
            user.notifications=False

        if user.newsletter=="True":
            user.newsletter=True
        else:
            user.newsletter=False

        user.save()


    return render(request, "notificationSetting.html",{"user":user})

def custom_404(request,exception):
    return render(request, 'custom_404.html',status=404)