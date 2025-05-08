import os
import time
import psycopg2
from elasticsearch import Elasticsearch
from datetime import datetime
from contextlib import closing


def get_db_connection():
    connection = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'db'),  
        dbname=os.getenv('POSTGRES_DB', 'product_db'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'secret'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )
    return connection

def get_es_connection():
    connection = Elasticsearch(
        hosts=[{
            "host": os.getenv("ELASTICSEARCH_HOST"),
            "port": int(os.getenv("ELASTICSEARCH_PORT")),
            "scheme": "http"  
        }]
    )
    return connection

def wait_for_elasticsearch(es_connection):
    while True:
        try:
            if es_connection.ping():
                print("Elasticsearch is ready!")
                break
        except Exception:
            print("Waiting for Elasticsearch...")
            time.sleep(5)

# Создать индекс products в Elasticsearch
def create_products_index(es_connection):
    if not es_connection.indices.exists(index="products"):
        index_settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "product_name": {"type": "text"},
                    "product_description": {"type": "text"},
                    "count_left": {"type": "integer"},
                    "create_time": {"type": "date"},
                    "update_time": {"type": "date"}
                }
            }
        }
        es_connection.indices.create(index="products", body=index_settings)
        print("Index 'products' created successfully")
    else:
        print("Index 'products' already exists")

# Перенести данные о продуктах из PostgreSQL в Elasticsearch
def etl_process():
    with closing(get_db_connection()) as pg_connection, closing(get_es_connection()) as es_connection:
        wait_for_elasticsearch(es_connection)
        
        # Создать индекс перед загрузкой данных
        create_products_index(es_connection)

        pg_cursor = pg_connection.cursor()

        # Получить все продукты из PostgreSQL
        select_query = "SELECT product_id, product_name, product_description, count_left, create_time, update_time FROM products"
        pg_cursor.execute(select_query)
        products = pg_cursor.fetchall()

        # Загрузить продукты в Elasticsearch
        for product in products:
            product_id, product_name, product_description, count_left, create_time, update_time = product

            # Индексировать продукт в Elasticsearch
            es_connection.index(
                index="products",
                id=product_id,
                body={
                    "product_name": product_name,
                    "product_description": product_description,
                    "count_left": count_left,
                    "create_time": create_time.isoformat(),
                    "update_time": update_time.isoformat()
                }
            )

        pg_cursor.close()

if __name__ == "__main__":
    while True:
        print(f"Syncing data at {datetime.utcnow()}...")
        etl_process()
        time.sleep(60)