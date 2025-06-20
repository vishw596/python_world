from mongoengine import signals
from app.models import Post
from app.esclient import es

index_name = "posts"


def post_save_handler(sender, document, **kwargs):
    try:
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
        es.index(
            index=index_name,
            id=str(document.id),
            body={
                "title": document.title or "",
                "content": document.content or "",
                "tags": document.tags or [],
                "posted_by":document.posted_by.username
            },
        )
    except Exception as e:
        # Log error here instead of failing silently or crashing
        print(f"Elasticsearch indexing error: {e}")


def post_delete_handler(sender, document, **kwargs):
    try:
        es.delete(index=index_name, id=str(document.id), ignore=[404])
    except Exception as e:
        print(f"Elasticsearch delete error: {e}")


# Connect signals as before
signals.post_save.connect(post_save_handler, sender=Post)
signals.post_delete.connect(post_delete_handler, sender=Post)
