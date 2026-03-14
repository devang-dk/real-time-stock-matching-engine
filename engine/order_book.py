import heapq
from engine.order import Order
import time
from engine.settlement import settle_trade
from sqlmodel import Session
from database import engine
import asyncio
from websocket_manager import manager   
from market_data import update_ticker
    

class OrderBook:
    def __init__(self):
        self.buy_heap = []   
        self.sell_heap = []
        self.trades = []  
        self.order_map = {}
    def add_order(self, order: Order):
        self.order_map[order.order_id] = order
        if order.type == "BUY":
            heapq.heappush(self.buy_heap, (-order.price, order.timestamp, order))
        elif order.type == "SELL":
            heapq.heappush(self.sell_heap, (order.price, order.timestamp, order))
        self.match_orders()
    def match_orders(self):
        while self.buy_heap and self.sell_heap:

            while self.buy_heap and self.buy_heap[0][2].quantity == 0:
                heapq.heappop(self.buy_heap)

            while self.sell_heap and self.sell_heap[0][2].quantity == 0:
                heapq.heappop(self.sell_heap)

            best_buy = self.buy_heap[0][2]
            best_sell = self.sell_heap[0][2]

            # Check if match possible
            if best_buy.price >= best_sell.price:

                trade_quantity = min(best_buy.quantity, best_sell.quantity)
                trade_price = best_sell.price  # usually trade at sell price
                update_ticker(best_buy.symbol, trade_price, trade_quantity)

                print(f"Trade Executed: {trade_quantity} units at {trade_price}")

                self.trades.append({
                    "price": trade_price,
                    "quantity": trade_quantity,
                    "buyer_order_id": best_buy.order_id,
                    "seller_order_id": best_sell.order_id,
                    "timestamp": time.time()
                })

                asyncio.create_task(
                    manager.broadcast({
                        "type": "trade",
                        "symbol": best_buy.symbol,
                        "price": trade_price,
                        "quantity": trade_quantity
                    })  
                )

                asyncio.create_task(
                    manager.broadcast({
                        "type": "orderbook",
                        "symbol": best_buy.symbol
                    })
                )

                asyncio.run(
                    manager.broadcast({
                        "type": "ticker",
                        "symbol": best_buy.symbol,
                        "price": trade_price,
                        "quantity": trade_quantity
                    })
                )

                with Session(engine) as session:
                    settle_trade(
                        session,
                        buyer_id=best_buy.user_id,
                        seller_id=best_sell.user_id,
                        symbol=best_buy.symbol,
                        price=trade_price,
                        quantity=trade_quantity
                    )

                # Reduce quantities
                best_buy.quantity -= trade_quantity
                best_sell.quantity -= trade_quantity

                # Remove completed orders
                if best_buy.quantity == 0:
                    heapq.heappop(self.buy_heap)

                if best_sell.quantity == 0:
                    heapq.heappop(self.sell_heap)

            else:
                break
    def cancel_order(self, order_id):

        if order_id not in self.order_map:
            print("Order not found.")
            return

        order = self.order_map[order_id]
        order.quantity = 0   # Mark as inactive

        print(f"Order {order_id} cancelled.")

    def show_order_book(self):

        print("\nCurrent BUY Orders:")
        for _, _, order in self.buy_heap:
            if order.quantity > 0:
                print(order)

        print("\nCurrent SELL Orders:")
        for _, _, order in self.sell_heap:
            if order.quantity > 0:
                print(order)
