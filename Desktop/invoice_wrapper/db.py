from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(String(64), primary_key=True)
    customer_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    total_qty = Column(Integer)
    subtotal = Column(Float)
    vat = Column(Float)
    grand_total = Column(Float)

class OrderLineItem(Base):
    __tablename__ = 'order_line_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(64))
    product_id = Column(String(64))
    title = Column(String(255))
    product_qty = Column(Integer)
    line_total = Column(Float)

# Use environment variables for Docker-based deployment
db_user = os.getenv("DB_USER", "invoice_user")
db_pass = os.getenv("DB_PASS", "invoice_pass")
db_host = os.getenv("DB_HOST", "localhost")
db_name = os.getenv("DB_NAME", "invoice_db")

DATABASE_URL = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)