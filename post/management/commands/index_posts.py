from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch, helpers
from mongoengine import connect
from app.models import Post 
from django.conf import settings
from app.esclient import es
class Command(BaseCommand):
    help = "Index posts from MongoDB to Elasticsearch"

    def handle(self, *args, **kwargs):
        # Connect to MongoDB
        connect(host=settings.MONGO_URI)
        

        # Define Elasticsearch index name
        index_name = "posts"

        # (Optional) create index with mappings
        if not es.indices.exists(index=index_name):
            es.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                                    "title": {"type": "text"},
                                    "content": {"type": "text"},
                                    "tags": {"type": "keyword"},
                                    "posted_by":{"type":"text"}
                                }
                            }
                        },
                    )

        # Index existing posts
        actions = []
        for post in Post.objects:
            actions.append(
                {
                    "_index": index_name,
                    "_id": str(post.id),
                    "_source": {
                        "title": post.title or "",
                        "content": post.content or "",
                        "tags": post.tags or [],
                        "posted_by":post.posted_by.username
                    },
                }
            )

        if actions:
            helpers.bulk(es, actions)
            print(f"Indexed {len(actions)} posts to Elasticsearch.")
        else:
            print("No posts found to index.")
