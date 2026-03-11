from fastapi import FastAPI, Depends
from pydantic import BaseModel
from engine.order import Order
from engine.order_book import OrderBook
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from database import engine
from sqlmodel import Session
from models import User
from auth import hash_password
from pydantic import BaseModel
from auth import verify_password, create_access_token
from auth import get_current_user
import models


app = FastAPI(
    title="Real-Time Stock Order Matching Engine",
    version="1.0.0"
)

SQLModel.metadata.create_all(engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
order_books = {}


class OrderRequest(BaseModel):
    symbol: str
    order_type: str
    price: float
    quantity: int


@app.post("/place-order")
def place_order(order_data: OrderRequest, user_id: int = Depends(get_current_user)):
    symbol = order_data.symbol.upper()
    if symbol not in order_books:
        order_books[symbol] = OrderBook()
    order = Order(order_data.order_type.upper(), order_data.price, order_data.quantity)
    order_books[symbol].add_order(order)
    return {
        "message": "Order placed",
        "order_id": order.order_id
    }


@app.post("/cancel-order/{order_id}")
def cancel_order(order_id: str):
    order_book.cancel_order(order_id)
    return {"message": "Cancel attempted"}


@app.get("/order-book")
def get_order_book(symbol: str):
    symbol = symbol.upper()

    if symbol not in order_books:
        return {"buy_orders": [], "sell_orders": []}

    order_book = order_books[symbol]

    return {
        "buy_orders": [
            {"price": o.price, "quantity": o.quantity}
            for _, _, o in order_book.buy_heap
            if o.quantity > 0
        ],
        "sell_orders": [
            {"price": o.price, "quantity": o.quantity}
            for _, _, o in order_book.sell_heap
            if o.quantity > 0
        ]
    }


@app.get("/trades")
def get_trades(symbol: str):
    symbol = symbol.upper()

    if symbol not in order_books:
        return []

    return order_books[symbol].trades

@app.get("/")
def health_check():
    return {"status": "Stock Matching Engine Running"}

@app.get("/")
def health():
    return {"status": "Stock Matching Engine Running"}



class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


@app.post("/register")
def register_user(user_data: RegisterRequest):
    with Session(engine) as session:

        user = User(
            username=user_data.username,
            email=user_data.email,
            password=hash_password(user_data.password)
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return {"message": "User registered successfully"}



class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/login")
def login(user_data: LoginRequest):

    with Session(engine) as session:

        user = session.query(User).filter(User.email == user_data.email).first()

        if not user:
            return {"error": "User not found"}

        if not verify_password(user_data.password, user.password):
            return {"error": "Invalid password"}

        token = create_access_token({"user_id": user.id})

        return {"access_token": token}
