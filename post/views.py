from django.shortcuts import render
from app.models import *
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from threading import Thread
from bson import ObjectId
from datetime import datetime
from cloudinary.uploader import upload
import cloudinary

# POST
def post(request):
    if "user_id" not in request.session:
        return redirect("login")
    
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        tags = request.POST.get("post_type")
        # tags = tags.split(",")

        image = request.FILES.get("imageUrl")
        image_url = ""

        if image:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result.get("secure_url")

        post = Post(
            title=title,
            content=content,
            posted_by=ObjectId(request.session.get("user_id")),
            tags=tags,
            image_url=image_url
        )
        post.save()

        user = User.objects.get(id=ObjectId(request.session.get("user_id")))
        user.posts.append(post)
        user.save()

    posts = Post.objects().order_by("-created_at")
    post_type = 'all'
    user = User.objects.get(id=request.session.get("user_id"))

    return render(request, "post.html", {"posts": posts, "user":user, "selected_filter": post_type})

def postFilter(request):
    if "user_id" not in request.session:
        return redirect("login")
    
    post_type = "all"  # default filter

    if request.method == "POST":
        post_type = request.POST.get("filterBtn", "all")

        if post_type == "new":
            posts = Post.objects().order_by("-created_at").limit(10)
        elif post_type == "mostLiked":
            posts = Post.objects().order_by("-likes").limit(10)
        elif post_type == "mostShared":
            posts = Post.objects().order_by("-comments").limit(10)
        else:
            post_type = "all"
            posts = Post.objects().order_by("-created_at")
    else:
        posts = Post.objects().order_by("-created_at")

    user = User.objects.get(id=ObjectId(request.session.get("user_id")))

    return render(request, "post.html", {
        "posts": posts,
        "user": user,
        "selected_filter": post_type  # Used to highlight active button
    })

# LIKE POST
def like_post(request, post_id): 

    if request.method == "POST":
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

        
        if liked and post.posted_by.email and post.posted_by.notifications:
            subject = "🎉 Someone liked your post on Python World!"
            from_email = "your_email@gmail.com"
            to_email = [post.posted_by.email]

            print(f"Sending email to: {to_email}")

            # Beautiful HTML email template
            html_content = f"""
            <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python World Notification</title>
</head>
<body style="margin: 0; padding: 20px; font-family: Arial, Helvetica, sans-serif; background-color: #f8fafc; color: #1e293b; line-height: 1.6;">
    <!-- Main Container -->
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;">
        <!-- Header -->
        <tr>
            <td style="background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); padding: 40px 30px; text-align: center; color: white;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="width: 100%;">
                    <tr>
                        <td style="text-align: center;">
                            <!-- Logo -->
                            <div style="font-size: 28px; font-weight: bold; margin-bottom: 8px;">
                                <span style="color: #ffffff;">Python</span>
                                <span style="color:rgb(16, 185, 86);"> World</span>
                            </div>
                            <!-- Tagline -->
                            <p style="margin: 0; font-size: 16px; opacity: 0.9;">Where Python Meets the World</p>
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
                                Hi <span style="color: #10b981; font-weight: bold;">{post.posted_by.username}</span>,
                            </p>
                            
                            <!-- Notification Content -->
                            <div style="background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%); border-left: 4px solid #3b82f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                <p style="margin: 0; font-size: 16px; color: #1e293b;">
                                    <strong style="color: #7c3aed;">Someone</strong> liked your post titled: 
                                    <br><span style="color: #3b82f6; font-weight: bold; font-style: italic; font-size: 17px;">" {post.title}"</span>
                                </p>
                            </div>
                            
                            <!-- Encouragement Text -->
                            <p style="margin: 20px 0; color: #64748b; font-size: 15px; text-align: center;">
                                Your content is making an impact in the Python community! 🎉
                            </p>
                            
                            <!-- CTA Button -->
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="pythonworld.mooo.com/profile/{user.username}" style="display: inline-block; background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); color: white; padding: 14px 28px; border-radius: 25px; text-decoration: none; font-weight: bold; font-size: 16px; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);">
                                    View Your Post →
                                </a>
                            </div>
                        </td>
                    </tr>
                </table>
                
                <!-- Divider -->
                <div style="height: 1px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 30px 0;"></div>
                
                <!-- Additional Content -->
                <div style="text-align: center; margin: 30px 0;">
                    <div style="background-color: #f1f5f9; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;">
                        <p style="margin: 0 0 12px 0; color: #475569; font-size: 16px; font-weight: bold;">
                            🚀 Keep Growing Your Python Skills!
                        </p>
                        <p style="margin: 0; color: #64748b; font-size: 14px;">
                            Keep sharing your knowledge and connecting with fellow developers!
                        </p>
                    </div>
                </div>
                
                <!-- Stats Section -->
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="width: 100%; margin: 20px 0;">
                    <tr>
                        <td style="width: 33.33%; text-align: center; padding: 15px; background-color: #fef3c7; border-radius: 8px;">
                            <div style="font-size: 24px; margin-bottom: 5px;">{len(post.likes)}</div>
                            <div style="font-size: 12px; color: #92400e;">LIKES</div>
                        </td>
                        <td style="width: 33.33%; text-align: center; padding: 15px;">
                            <div style="font-size: 24px; margin-bottom: 5px;">{len(post.comments)}</div>
                            <div style="font-size: 12px; color:rgb(28, 73, 146);">COMMENTS</div>
                        </td>
                        <td style="width: 33.33%; text-align: center; padding: 15px; background-color: #dcfce7; border-radius: 8px;">
                            <div style="font-size: 24px; margin-bottom: 5px;">4</div>
                            <div style="font-size: 12px; color: #166534;">SHARES</div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <!-- Footer -->
        <tr>
            <td style="background-color: #1e293b; padding: 30px; text-align: center; color: #94a3b8;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="width: 100%;">
                    <tr>
                        <td style="text-align: center;">
                            <!-- Social Links -->
                            <div style="margin-bottom: 20px;">
                                <a href="#" style="display: inline-block; width: 40px; height: 40px; background-color: #374151; border-radius: 50%; text-decoration: none; margin: 0 8px; line-height: 40px; color: #9ca3af;">📧</a>
                                <a href="#" style="display: inline-block; width: 40px; height: 40px; background-color: #374151; border-radius: 50%; text-decoration: none; margin: 0 8px; line-height: 40px; color: #9ca3af;">🐦</a>
                                <a href="#" style="display: inline-block; width: 40px; height: 40px; background-color: #374151; border-radius: 50%; text-decoration: none; margin: 0 8px; line-height: 40px; color: #9ca3af;">X</a>
                            </div>
                            
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
                                <a href="#" style="color: #9ca3af; text-decoration: underline;">Update Preferences</a>
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
            text_content = f"""
            Hi {post.posted_by.username},

            Someone liked your post titled: "{post.title}"

            Your content is making an impact in the Python community!

            Check it out on your profile!

            ---
            This is an automatic notification from Python World.
            © 2025 Python World. All rights reserved.
            """

            try:
                send_email_async(subject, text_content, html_content, from_email, to_email, post)
            except Exception as e:
                print(f"Failed to send email: {str(e)}")

        

        return JsonResponse({
            "liked": liked,
            "like_count": len(post.likes)
        })
    
    return JsonResponse({"error": "Invalid request method"}, status=405)

# COMMENT POST
def comment_post(request, post_id):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        user = User.objects.get(id=ObjectId(request.session.get("user_id")))
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


        if post.posted_by.notifications:

                        subject = "🎉 Someone commented on your post on Python World!"
                        from_email = "your_email@gmail.com"
                        to_email = [post.posted_by.email]

                        print(f"Sending email to: {to_email}")

                            # Beautiful HTML email template
                        html_content = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Python World Comment Notification</title>
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
                                                Hi <span style="color: #10b981; font-weight: bold;">{post.posted_by.username}</span>,
                                            </p>
                                            
                                            <!-- Notification Content -->
                                            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left: 4px solid #f59e0b; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                                <p style="margin: 0; font-size: 16px; color: #1e293b;">
                                                    <strong style="color: #7c3aed;">Someone</strong> commented on your post titled: 
                                                    <br><span style="color: #1e40af; font-weight: bold; font-style: italic; font-size: 17px;">"{post.title}"</span>
                                                </p>
                                            </div>
                                            
                                            <!-- Encouragement Text -->
                                            <p style="margin: 20px 0; color: #64748b; font-size: 15px; text-align: center;">
                                                Your content is making an impact in the Python community! 🐍
                                            </p>
                                            
                                            <!-- CTA Button -->
                                            <div style="text-align: center; margin: 30px 0;">
                                                <a href="pythonworld.mooo.com/profile/{user.username}" style="display: inline-block; background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%); color: white; padding: 14px 28px; border-radius: 25px; text-decoration: none; font-weight: bold; font-size: 16px; box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);">
                                                    View Comment →
                                                </a>
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Divider -->
                                <div style="height: 1px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 30px 0;"></div>
                                
                                <!-- Engagement Section -->
                                <div style="text-align: center; margin: 30px 0;">
                                    <div style="background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%); padding: 20px; border-radius: 12px; border: 1px solid #c4b5fd;">
                                        <p style="margin: 0 0 12px 0; color: #581c87; font-size: 16px; font-weight: bold;">
                                            💭 New Comment Alert!
                                        </p>
                                        <p style="margin: 0; color: #64748b; font-size: 14px;">
                                            Someone found your post interesting enough to leave a comment. Keep the conversation going!
                                        </p>
                                    </div>
                                </div>
                                
                            
                                
                                <!-- Tips Section -->
                                <div style="background-color: #f1f5f9; padding: 20px; border-radius: 10px; border: 1px solid #cbd5e1; margin: 20px 0;">
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="width: 100%;">
                                        <tr>
                                            <td style="width: 60px; text-align: center; vertical-align: top; padding-right: 15px;">
                                                <div style="font-size: 32px;">💡</div>
                                            </td>
                                            <td style="vertical-align: top;">
                                                <p style="margin: 0 0 8px 0; color: #1e293b; font-size: 14px; font-weight: bold;">
                                                    Pro Tip: Engage Back!
                                                </p>
                                                <p style="margin: 0; color: #64748b; font-size: 13px;">
                                                    Responding to comments helps build a stronger community and increases your post visibility.
                                                </p>
                                            </td>
                                        </tr>
                                    </table>
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
                                            <div style="margin-bottom: 20px;">
                                                <a href="#" style="display: inline-block; width: 40px; height: 40px; background-color: #374151; border-radius: 50%; text-decoration: none; margin: 0 8px; line-height: 40px; color: #9ca3af;">📧</a>
                                                <a href="#" style="display: inline-block; width: 40px; height: 40px; background-color: #374151; border-radius: 50%; text-decoration: none; margin: 0 8px; line-height: 40px; color: #9ca3af;">🐦</a>
                                                <a href="#" style="display: inline-block; width: 40px; height: 40px; background-color: #374151; border-radius: 50%; text-decoration: none; margin: 0 8px; line-height: 40px; color: #9ca3af;">X</a>
                                            </div>
                                            
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
                                                <a href="#" style="color: #9ca3af; text-decoration: underline;">Update Preferences</a> |
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
                        text_content = f"""
                        Hi {post.posted_by.username},
                        Someone commented on your post titled: "{post.title}"
                        Your content is making an impact in the Python community!
                        Check it out on your profile!
                        ---
                        This is an automatic notification from Python World.
                        © 2025 Python World. All rights reserved.
                        """
                        try:
                            send_email_async(subject, text_content, html_content, from_email, to_email, post)

                        except Exception as e:
                            print(f"Failed to send email: {str(e)}")

        # Send back basic comment data
        return JsonResponse({
            "comment_body": comment.comment_body,
            "created_at": datetime.strftime(comment.created_at, "%b %d, %Y"),
            "username": comment.created_by.username,
            "initial": comment.created_by.username[0].upper()
        })

# FEED PAGE
def feed(request):
    if "user_id" not in request.session:
        return redirect("login")
    
    return redirect("post")

# SEND MAIL ASYNC
def send_email(subject, text_content, html_content, from_email, to_email, post):
    try:
        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        print(f"Email sent successfully to {post.posted_by.email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def send_email_async(subject, text_content, html_content, from_email, to_email, post):
    Thread(target=send_email, args=(subject, text_content, html_content, from_email, to_email, post)).start()

from django.http import JsonResponse
from app.esclient import es  # adjust path if needed

def search_post(request):
    try:
        query = request.GET.get("query")
        if not query:
            return HttpResponse("Query is required!")           
        index_name = "posts"
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "content", "tags", "posted_by"],
                    "fuzziness": "AUTO"
                }
            }
        }

        response = es.search(index=index_name, body=body)
        hits = response.get("hits", {}).get("hits", [])

        results = []
        for hit in hits:
            source = hit["_source"]
            source["id"] = hit["_id"]  # include ID
            results.append(source)

        return JsonResponse({"results": results}, safe=False)
    
    except Exception as e:
        print("Search Error:", e)
        return JsonResponse({"error": "Something went wrong"}, status=500)
