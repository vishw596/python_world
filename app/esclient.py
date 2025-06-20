# Create client once, reuse it

from django.conf import settings
from elasticsearch import Elasticsearch
import os

es = Elasticsearch(
    "https://34.10.231.119:9200",
    http_auth=(settings.ES_USERNAME, settings.ES_PASSWORD),
    verify_certs=False,
   
      # or True if using valid SSL certs
) 