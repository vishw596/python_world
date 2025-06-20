from django.core.management.base import BaseCommand
from elasticsearch import helpers
from mongoengine import connect
from app.models import QnA
from django.conf import settings
from app.esclient import es


class Command(BaseCommand):
    help = "Index QnA from MongoDB to Elasticsearch"

    def handle(self, *args, **kwargs):
        connect(host=settings.MONGO_URI)
        index_name = "qna"

        if not es.indices.exists(index=index_name):
            es.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "title": {"type": "text"},
                            "content": {"type": "text"},
                            "posted_by":{"type":"text"}
                        }
                    }
                },
            )

        actions = []
        for qna in QnA.objects:
            actions.append(
                {
                    "_index": index_name,
                    "_id": str(qna.id),
                    "_source": {
                        "title": qna.title or "",
                        "content": qna.content or "",
                        "posted_by":qna.posted_by.username
                        
                    },
                }
            )

        if actions:
            helpers.bulk(es, actions)
            print(f"Indexed {len(actions)} QnAs to Elasticsearch.")
        else:
            print("No QnAs found to index.")
