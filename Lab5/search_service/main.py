from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch
from pydantic import BaseModel
import os
from elasticsearch.exceptions import ConnectionError

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
ELASTICSEARCH_PORT = os.getenv("ELASTICSEARCH_PORT")
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX")

es = Elasticsearch([f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"])

app = FastAPI()

class SearchQuery(BaseModel):
    query: str

@app.post("/search/")
def search_products(search_query: SearchQuery):
    try:
        query_body = {
            "query": {
                "multi_match": {
                    "query": search_query.query,
                    "fields": ["product_name", "product_description"]
                }
            }
        }
        response = es.search(index=ELASTICSEARCH_INDEX, body=query_body)
        hits = response["hits"]["hits"]
        return [hit["_source"] for hit in hits]
    except ConnectionError:
        raise HTTPException(status_code=503, detail="Elasticsearch is not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
