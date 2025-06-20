from django.db import models # type: ignore
from django.contrib.auth.models import User
from mongoengine import StringField,ObjectIdField,IntField,Document,ListField,ReferenceField,DateTimeField,EmailField,BooleanField,DateField
from django.utils import timezone
from datetime import date

class User(Document):
    username = StringField(unique=True)
    password = StringField(max_length=128)
    email = EmailField(required=True,unique=True)
    bio = StringField(default="hey there i'm using social media platform")
    followings = ListField(ReferenceField('User'))
    followers = ListField(ReferenceField('User'))
    profilePicUrl = StringField(default="https://res.cloudinary.com/dei7arqb7/image/upload/v1749276806/s38levwhxowaxacwwszy.webp")
    posts = ListField(ReferenceField('Post'))
    questions = ListField(ReferenceField('QnA'))
    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)
    is_active = BooleanField(default=True)
    auth_provider = StringField(choices=["github","google","x","facebook","manual"],default="manual",required=True)
    meta = {'collection': 'users'}
    notifications=BooleanField(default=True)
    newsletter=BooleanField(default=True)

class Post(Document):
    image_url = StringField(required=False)
    title = StringField(required=False)
    content = StringField()
    posted_by = ReferenceField('User', required=True)  
    likes = ListField(ReferenceField('User'))  
    comments = ListField(ReferenceField('Comment'))  
    report_post = ListField(StringField())  
    tags = ListField(StringField())
    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)
    meta = {'collection': 'posts'}  

class QnA(Document):
    title = StringField(required=False)
    content = StringField()
    posted_by = ReferenceField('User', required=True)  
    views = IntField(default=0)
    upvotes = ListField(ReferenceField('User'))
    downvotes =  ListField(ReferenceField('User'))
    answers = ListField(ReferenceField('Answer'))
    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)
    meta = {'collection': 'questions'} 

class Comment(Document):
    comment_body = StringField(required=True)
    created_by = ReferenceField('User', required=True, reverse_delete_rule=2)  
    for_post = ReferenceField('Post', required=True, reverse_delete_rule=2)  
    created_at = DateTimeField(default=timezone.now)  

    def __str__(self):
        return self.comment_body[:30] 

    meta = {'collection': 'comments'}
class Answer(Document):
    answer_body = StringField(required=True)
    created_by = ReferenceField('User', required=True, reverse_delete_rule=2)  
    for_question = ReferenceField('QnA', required=True, reverse_delete_rule=2)  
    created_at = DateTimeField(default=timezone.now)  

    def __str__(self):
        return self.comment_body[:30] 

    meta = {'collection': 'answers'}

class Contact(Document):
    name = StringField(max_length=122, default="NULL")
    email = StringField(max_length=122, default="NULL")
    contact = StringField(max_length=10, default="NULL")
    desc = StringField(max_length=1000, default="NULL")

    def __str__(self):
        return self.name

    meta = {'collection': 'contacts'}


class Article(Document):
    title = StringField(max_length=1000, default="")
    description = StringField(max_length=10000, default="")
    content = StringField(default="")
    topic = StringField(max_length=50)
    imageUrl = StringField(max_length=100)
    source = StringField(max_length=100)
    no_of_views=IntField(default=0)
    created_at = DateTimeField(default=timezone.now) 


class Utility(Document):
    icon = StringField(max_length=100)
    name = StringField(max_length=40, default="NULL")
    desc = StringField(max_length=200, default="NULL")
    url = StringField(max_length=200, default="NULL")
    downloads = IntField(default=0)
    
    