from django.shortcuts import render, redirect
from app.models import *

# SERVICE PAGE
def utils(request):

    if "user_id" not in request.session:
        return redirect("login")

    utilities = Utility.objects.all()
    user = User.objects.get(id=request.session["user_id"])
        
    return render(request, "utils.html", {'utilities': utilities,'user':user})

def increaseDownloads(request, utility_id):
    if "user_id" not in request.session:
        return redirect("login")
    
    if request.method == "POST":
        utility = Utility.objects.get(id=utility_id)
        utility.downloads += 1
        utility.save()
    return redirect("utils")