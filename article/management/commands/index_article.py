from django.core.management.base import BaseCommand
from elasticsearch import helpers
from mongoengine import connect
from app.models import Article
from django.conf import settings
from app.esclient import es

class Command(BaseCommand):
    help = "Index Articles from MongoDB to Elasticsearch"

    def handle(self, *args, **kwargs):
        connect(host=settings.MONGO_URI)
        index_name = "articles"

        if not es.indices.exists(index=index_name):
            es.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "title": {"type": "text"},
                            "description": {"type": "text"},
                            "content": {"type": "text"},
                            "topic": {"type": "keyword"},
                            "source": {"type": "keyword"},
                        }
                    }
                },
            )

        actions = []
        for article in Article.objects:
            actions.append(
                {
                    "_index": index_name,
                    "_id": str(article.id),
                    "_source": {
                        "title": article.title or "",
                        "description": article.description or "",
                        "content": article.content or "",
                        "topic": article.topic or "",
                        "source": article.source or "",
                    },
                }
            )

        if actions:
            helpers.bulk(es, actions)
            print(f"Indexed {len(actions)} articles to Elasticsearch.")
        else:
            print("No articles found to index.")
