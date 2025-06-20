# MESSAGES AND SHORTCUT IMPORT
from django.contrib import messages
from django.shortcuts import render, redirect
from ai.views import SYSTEM_PROMPT
from app.models import *
from bson.objectid import ObjectId
from google.generativeai import configure, GenerativeModel
from app.esclient import es
from django.http import JsonResponse,HttpResponse

# ARTICLE PAGE


def article(request):

    if "user_id" not in request.session:
        return redirect("login")

    all_articles = Article.objects()

    user = User.objects.get(id=request.session["user_id"])

    popular = Article.objects().order_by("-no_of_views")[:5]

    return render(
        request,
        "article.html",
        {"articles": all_articles, "user": user, "popular": popular},
    )


def see_article(request, article_id):

    if "user_id" not in request.session:
        return redirect("login")
    try:
        article = Article.objects.get(id=ObjectId(article_id))
        article.no_of_views += 1
        article.save()

    except Article.DoesNotExist:
        return render(request, "404.html", status=404)

    if request.method == "POST":
        print("reached here")
        configure(api_key="AIzaSyCKUnoBceGG7HLXpePDGoPbNW0TpQwuPvY")
        model = GenerativeModel("gemini-1.5-flash")

        summary = ""

        SYSTEM_PROMPT = "Summarize the following article in 100 or less words :"

        response = model.generate_content(
            [
                {"role": "user", "parts": [SYSTEM_PROMPT]},
                {"role": "user", "parts": [article.content]},
            ]
        )
        summary = response.text
        print(summary)

        return render(
            request, "see_article.html", {"article": article, "summary": summary}
        )

    return render(request, "see_article.html", {"article": article})





def search_article(request):
    try:
        query = request.GET.get("query")
        if not query:
            return HttpResponse("Query is required!")
        print(query)
        index_name = "articles"
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "description", "content", "topic", "source"],
                    "fuzziness": "AUTO",
                }
            }
        }

        response = es.search(index=index_name, body=body)
        hits = response.get("hits", {}).get("hits", [])
        results = []
        for hit in hits:
            source = hit["_source"]
            source["id"] = hit["_id"]  # Add ID to the response
            results.append(source)
        
        return JsonResponse({"results": results}, safe=False)

    except Exception as e:
        print("Error:", e)
        return JsonResponse({"error": "Something went wrong!"}, status=500)

def article_filter(request):
    try:
        filter_value = request.GET.get("filter")
        if not filter_value:
            return HttpResponse("filter is required!")

        # Elasticsearch query to get IDs
        index_name = "articles"
        body = {
            "query": {
                "multi_match": {
                    "query": filter_value,
                    "fields": ["topic"],
                    "fuzziness": "AUTO",
                }
            }
        }

        response = es.search(index=index_name, body=body)
        hits = response.get("hits", {}).get("hits", [])
        article_ids = [hit["_id"] for hit in hits]

        # Fetch articles from MongoDB using MongoEngine
        articles = Article.objects(id__in=article_ids)
        popular = Article.objects().order_by("-no_of_views")[:5]
        return render(request, "article.html", {"articles": articles,"popular":popular})

    except Exception as e:
        print("Error:", e)
        return HttpResponse("Something went wrong")
