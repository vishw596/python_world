from django.urls import path
from app import views

urlpatterns = [
    # BASIC OPERATIONS
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('login', views.loginUser, name='login'),
    path('signup', views.signupUser, name='signup'),
    path('logout', views.logoutUser, name='logoutUser'), 
    path('post',views.post,name='post'),
    path('post/<str:post_id>/like/', views.like_post, name='like_post'),
    path('post/<str:post_id>/comment/', views.comment_post, name='comment_post'),
    path("editProfile/",views.editProfile,name="editProfile"),
    path("profile/<str:username>",views.profile,name="profile"),
    path("feed",views.feed,name="feed"),
    path("followUnfollow/<str:username>",views.followUnfollow,name="followUnfollow"),

    # NAVBAR
    path('article',views.article, name='article'),
    path('qna/',views.qna,name='qna'),
    path('qna/ans/',views.que_answer,name="ans"),
    path('qna/<str:que_id>/upvote/',views.upvote_que,name='upvote_question'),
    path('qna/<str:que_id>/downvote/',views.downvote_que,name='downvote_question'),
    path('utils',views.utils, name='utils'),
  
    # FORGOT PASSWORD
    path('forgotpass',views.forgotpass,name="forgotpass"),
]