"""
URL configuration for Python_World project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from customAuth import views as auth
from app import views as home
from post import views as post
from userProfile import views as user
from article import views as article
from qna import views as qna
from utils import views as utils
from ai import views as ai

urlpatterns = [

    # ADMIN
    path('admin/', admin.site.urls),
    
    # HOME
    path('', home.index, name='index'),
    path('index', home.index, name='index'),
    path('notificationSetting', home.notificationSetting, name='notificationSetting'),

    # AUTHENTICATION

    path('login', auth.loginUser, name='login'),
    path('signup', auth.signupUser, name='signup'),

    path('logout', auth.logoutUser, name='logoutUser'), 

    path("google-login/",auth.google_login,name="google"),
    path("google-callback/",auth.google_callback),
    path("github-login/",auth.github_login,name="github"),
    path("github-callback/",auth.github_callback),
    path("x-login/",auth.x_login,name="x"),
    path("x-callback/",auth.x_callback,name="x-callback"),

    path('forgotpass',auth.forgotpass,name="forgotpass"),

    # POST
    path('post',post.post,name='post'),
    path('post/<str:post_id>/like/', post.like_post, name='like_post'),
    path('post/<str:post_id>/comment/', post.comment_post, name='comment_post'),
    path("feed",post.feed,name="feed"),
    path('search/post/',post.search_post,name='search_post'),
    path('postFilter', post.postFilter, name='postFilter'),

    # PROFILE
    path("editProfile/",user.editProfile,name="editProfile"),
    path("profile/<str:username>",user.profile,name="profile"),
    path("followUnfollow/<str:username>",user.followUnfollow,name="followUnfollow"),

    # ARTICLE
    path('article/', article.article, name='article'),
    path('article/<str:article_id>', article.see_article, name='see_article'),
    path('search/article',article.search_article,name='search_article'),
    path('filter/article',article.article_filter,name='filter_article'),

    # QNA
    path('qna/',qna.qna,name='qna'),
    path('qna/ans/',qna.que_answer,name="ans"),
    path('qna/<str:que_id>/upvote/',qna.upvote_que,name='upvote_question'),
    path('qna/<str:que_id>/downvote/',qna.downvote_que,name='downvote_question'),
    path('search/qna/',qna.search_qna,name='search_qna'),


    # UTILS
    path('utils',utils.utils, name='utils'),
    path('utils/<str:utility_id>/', utils.increaseDownloads, name='increaseDownloads'),

    # AI
    path('ai',ai.home,name='ai'),
    path('ai/<str:page>',ai.home,name='ai'),

]
handler404 = 'app.views.custom_404'
