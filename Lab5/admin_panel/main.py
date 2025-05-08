from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

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

class ProductCreate(BaseModel):
    product_name: str
    product_description: str
    count_left: int

class ProductUpdate(BaseModel):
    product_name: str = None
    product_description: str = None
    count_left: int = None

@app.post("/products/")
def create_product(product: ProductCreate):
    db = SessionLocal()
    new_product = Product(
        product_name=product.product_name,
        product_description=product.product_description,
        count_left=product.count_left
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.put("/products/{product_id}")
def update_product(product_id: int, product_update: ProductUpdate):
    db = SessionLocal()
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product_update.product_name:
        product.product_name = product_update.product_name
    if product_update.product_description:
        product.product_description = product_update.product_description
    if product_update.count_left is not None:
        product.count_left = product_update.count_left
    product.update_time = datetime.utcnow()
    db.commit()
    return {"message": f"Product {product_id} updated successfully"}