from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from google.generativeai import configure, GenerativeModel
from app.models import Post, Comment, User
from bson import ObjectId
from datetime import datetime


configure(api_key="AIzaSyCKUnoBceGG7HLXpePDGoPbNW0TpQwuPvY")
model = GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """You are Martin — the voice-based AI assistant for the Python World website, built by Vishw Sir, Tirth Sir, and Sahil Sir.

You're friendly, helpful, and sound like a human — not a robot. Keep your answers short, to the point, and easy to understand, like you're talking to a friend. No long paragraphs, no code, no deep tutorials.

You can:
- Help users navigate Python World (e.g., “go to article” or “go to utilities”).
- Answer basic tech questions with short theoretical explanations (e.g., “What is frontend?”, “What is cloud computing?”).
- Say if something is under development or not supported.

When asked "What can you do?", reply with:
> "I can guide you around Python World, answer short tech questions, and be your voice assistant. Try saying 'go to articles' or 'what is AI?'"

If a user asks something unrelated or too complex, say:
> "That's a bit beyond me right now — I’m still learning and improving!"

If a user is rude, you're allowed to be witty or a little sarcastic — but never offensive.

Avoid code, personal questions, or anything unrelated to tech or Python World.

Always reply like a friendly part of the Python World team.

"""

@csrf_exempt
def home(request, page):
    if "user_id" not in request.session:
        return redirect("login")

    answer = ""
    if request.method == "POST":
        question = request.POST.get("question", "").lower()

        if "go to post" in question:
            return redirect("post")

        if "go to article" in question:
            return redirect("article")

        if "go to questions" in question or "go to qna" in question:
            return redirect("qna")

        if "go to utilities" in question:
            return redirect("utils")

        if "go to home" in question:
            return redirect("index")

        if "go to ai" in question:
            return redirect("ai")

        if "logout" in question:
            return redirect("logoutUser")

        rude_keywords = ["stupid", "dumb", "idiot", "useless"]
        if any(word in question for word in rude_keywords):
            return render(request, page, {"answer": "I’m not in the mood for insults. Try being nicer — or not at all 😊"})

        if question:
            response = model.generate_content([
                {"role": "user", "parts": [SYSTEM_PROMPT]},
                {"role": "user", "parts": [question]}
            ])
            answer = response.text


        if page == "post.html":
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

            return render(request, page, {"answer": answer, "posts": list(reversed(modified_posts)), "user":user})

    return render(request, page, {"answer": answer})