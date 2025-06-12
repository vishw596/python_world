from mongoengine import signals
from app.models import QnA
from app.esclient import es

index_name = "qna"

def qna_save_handler(sender, document, **kwargs):
    try:
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

        es.index(
            index=index_name,
            id=str(document.id),
            body={
                "title": document.title or "",
                "content": document.content or "",
                "posted_by":document.posted_by.username
            },
        )
    except Exception as e:
        print(f"Elasticsearch QnA indexing error: {e}")

def qna_delete_handler(sender, document, **kwargs):
    try:
        es.delete(index=index_name, id=str(document.id), ignore=[404])
    except Exception as e:
        print(f"Elasticsearch QnA delete error: {e}")

signals.post_save.connect(qna_save_handler, sender=QnA)
signals.post_delete.connect(qna_delete_handler, sender=QnA)
