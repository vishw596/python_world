from mongoengine import signals
from app.models import Article
from app.esclient import es

index_name = "articles"

def article_save_handler(sender, document, **kwargs):
    try:
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

        es.index(
            index=index_name,
            id=str(document.id),
            body={
                "title": document.title or "",
                "description": document.description or "",
                "content": document.content or "",
                "topic": document.topic or "",
                "source": document.source or "",
            },
        )
    except Exception as e:
        print(f"Elasticsearch Article indexing error: {e}")

def article_delete_handler(sender, document, **kwargs):
    try:
        es.delete(index=index_name, id=str(document.id), ignore=[404])
    except Exception as e:
        print(f"Elasticsearch Article delete error: {e}")

signals.post_save.connect(article_save_handler, sender=Article)
signals.post_delete.connect(article_delete_handler, sender=Article)
