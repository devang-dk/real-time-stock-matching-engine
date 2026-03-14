import time
import uuid

class Order:
    def __init__(self, order_id, user_id, symbol, type, price, quantity, timestamp):
        self.order_id = order_id
        self.user_id = user_id
        self.symbol = symbol
        self.type = type
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp

    def __repr__(self):
        return f"{self.type} | Price: {self.price} | Qty: {self.quantity}"
