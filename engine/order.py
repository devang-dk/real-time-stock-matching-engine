import time
import uuid

class Order:
    def __init__(self, order_type: str, price: float, quantity: int):
        self.order_id = str(uuid.uuid4())
        self.type = order_type  # "BUY" or "SELL"
        self.price = price
        self.quantity = quantity
        self.timestamp = time.time()

    def __repr__(self):
        return f"{self.type} | Price: {self.price} | Qty: {self.quantity}"
