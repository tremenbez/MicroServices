from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import httpx
import os

SEARCH_SERVICE_URL = f"http://{os.getenv('SEARCH_SERVICE_HOST')}:{os.getenv('SEARCH_SERVICE_PORT')}"
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    product_description = Column(Text)
    count_left = Column(Integer)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class SearchQuery(BaseModel):
    query: str

@app.post("/products/search/")
async def search_products(search_query: SearchQuery):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SEARCH_SERVICE_URL}/search/",
                json={"query": search_query.query}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Search service error")
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error communicating with search service: {str(e)}")

class ProductCreate(BaseModel):
    product_name: str
    product_description: str
    count_left: int

@app.get("/products/{product_id}")
def get_product(product_id: int):
    db = SessionLocal()
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/products/")
def get_all_products():
    db = SessionLocal()
    products = db.query(Product).all()
    return products

@app.post("/purchase/{product_id}")
def purchase_product(product_id: int):
    db = SessionLocal()
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.count_left <= 0:
        raise HTTPException(status_code=400, detail="Product out of stock")
    product.count_left -= 1
    product.update_time = datetime.utcnow()
    db.commit()
    return {"message": f"Successfully purchased product {product_id}"}