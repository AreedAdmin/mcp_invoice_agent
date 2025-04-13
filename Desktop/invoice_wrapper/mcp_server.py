from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from db import Session, Order, OrderLineItem
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Allow access from LLM or frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OrderData(BaseModel):
    order_id: str
    customer_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    total_qty: Optional[int] = None
    subtotal: Optional[float] = None
    vat: Optional[float] = None
    grand_total: Optional[float] = None

@app.get("/orders")
def list_orders():
    session = Session()
    return [o.__dict__ for o in session.query(Order).all()]

@app.get("/order/{order_id}")
def get_order(order_id: str):
    session = Session()
    order = session.query(Order).filter_by(order_id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order.__dict__

@app.post("/order")
def add_order(order: OrderData):
    session = Session()
    if session.query(Order).filter_by(order_id=order.order_id).first():
        raise HTTPException(status_code=400, detail="Order already exists")
    new_order = Order(**order.dict())
    session.add(new_order)
    session.commit()
    return {"message": "Order created"}

@app.patch("/order/{order_id}")
def update_order(order_id: str, order: OrderData):
    session = Session()
    db_order = session.query(Order).filter_by(order_id=order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    for k, v in order.dict(exclude_unset=True).items():
        setattr(db_order, k, v)
    session.commit()
    return {"message": "Order updated"}

@app.delete("/order/{order_id}")
def delete_order(order_id: str):
    session = Session()
    db_order = session.query(Order).filter_by(order_id=order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    session.delete(db_order)
    session.commit()
    return {"message": "Order deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)