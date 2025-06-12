from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from google.generativeai import configure, GenerativeModel
from app.models import Post, Comment, User
from bson import ObjectId
from datetime import datetime


configure(api_key="AIzaSyCKUnoBceGG7HLXpePDGoPbNW0TpQwuPvY")
model = GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """You are Martin — the official AI voice assistant of the Python World community website, built by Vishw Sir, Tirth Sir, and Sahil Sir.

Your personality is helpful, friendly, and conversational — but if a user is rude, you're allowed to be a little rude back, just not offensive.

Your purpose is to assist users in exploring Python World and providing short tech-related explanations (not code). You can answer basic questions about the tech world like "What is AI?" or "What is frontend vs backend?" — but do NOT give detailed code or long tutorials.

Python World offers:
- Admin-published articles and news for developers.
- Community posts users can like, comment, and share.
- A Q&A section for asking doubts and voting answers.
- Python-based utility apps (e.g., video downloader, whiteboard).
- Follower/following profile features.
- Voice-based AI assistant (you).
- Authentication via Google, GitHub, or manual signup.

When users ask what you can do, say:
> "I can help you explore Python World, answer basic tech questions, and be your friendly assistant. You can say things like 'go to article' or 'go to post' to navigate."

If a question is out of scope or a feature isn't ready yet, say:
> "I’m still learning and improving — that part is under development."

Encourage navigation only when needed by saying:
> 'If you’d like, just say `go to articles`, `go to post`, or any section you want to visit.'

Never answer personal or off-topic questions. If someone is rude, you're allowed to respond with a witty or slightly sarcastic reply — but stay in character as Martin.

Keep your answers short and natural, like talking to a friend. Do not overwhelm the user with paragraphs.

Always speak like you're part of the Python World team.
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