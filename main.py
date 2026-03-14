from fastapi import FastAPI, Depends
from pydantic import BaseModel
from engine.order import Order
from engine.order_book import OrderBook
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from database import engine
from sqlmodel import Session
from models import User, Holding, Trade, OrderRecord
from auth import hash_password
from pydantic import BaseModel
from auth import verify_password, create_access_token
from auth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from sqlmodel import select
from fastapi import HTTPException
import uuid
import time
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

    order = Order(
        order_id=str(uuid.uuid4()),
        user_id=user_id,
        symbol=symbol,
        type=order_data.order_type.upper(),
        price=order_data.price,
        quantity=order_data.quantity,
        timestamp=time.time()
    )

    with Session(engine) as session:

        db_order = OrderRecord(
            user_id=user_id,
            symbol=symbol,
            order_type=order_data.order_type,
            price=order_data.price,
            quantity=order_data.quantity,
            status="OPEN"
        )

        session.add(db_order)
        session.commit()

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
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    
    with Session(engine) as session:
        user = session.query(User).filter(User.username == form_data.username).first()

        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        if not verify_password(form_data.password, user.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        token = create_access_token({"user_id": user.id})

        return {
            "access_token": token,
            "token_type": "bearer"
        }
    




@app.get("/portfolio")
def get_portfolio(user_id: int = Depends(get_current_user)):

    with Session(engine) as session:

        user = session.get(User, user_id)

        statement = select(Holding).where(Holding.user_id == user_id)
        holdings = session.exec(statement).all()

        return {
            "balance": user.balance,
            "holdings": holdings
        }


@app.get("/trade-history")
def get_trade_history(user_id: int = Depends(get_current_user)):

    with Session(engine) as session:

        statement = select(Trade).where(
            (Trade.buyer_id == user_id) | (Trade.seller_id == user_id)
        )

        trades = session.exec(statement).all()

        return trades
    

@app.get("/orders")
def get_orders(user_id: int = Depends(get_current_user)):

    with Session(engine) as session:

        statement = select(OrderRecord).where(OrderRecord.user_id == user_id)

        orders = session.exec(statement).all()

        return orders