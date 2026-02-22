import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = "https://ronndev.duckdns.org";

function App() {
  const [orderType, setOrderType] = useState("buy");
  const [price, setPrice] = useState("");
  const [quantity, setQuantity] = useState("");
  const [orderBook, setOrderBook] = useState({
    buy_orders: [],
    sell_orders: []
  });
  const [trades, setTrades] = useState([]);

  const fetchOrderBook = async () => {
  try {
    const response = await axios.get(`${API_BASE}/order-book`);
    console.log(response.data);   // ADD THIS LINE
    setOrderBook(response.data);
  } catch (error) {
    console.error("Error fetching order book", error);
  }
};

  const fetchTrades = async () => {
    try {
      const response = await axios.get(`${API_BASE}/trades`);
      console.log("Trades:", trades);
      setTrades(response.data);
    } catch (error) {
      console.error("Error fetching trades", error);
    }
  };

  const placeOrder = async () => {
    try {
      await axios.post(`${API_BASE}/place-order`, {
        order_type: orderType,
        price: Number(price),
        quantity: Number(quantity),
      });
      setPrice("");
      setQuantity("");
      fetchOrderBook();
      fetchTrades();
    } catch (error) {
      alert("Failed to place order");
    }
  };

  useEffect(() => {
    fetchOrderBook();
    fetchTrades();
    const interval = setInterval(() => {
      fetchOrderBook();
      fetchTrades();
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      <h1>Real-Time Stock Matching Engine</h1>

      <div className="order-form">
        <h2>Place Order</h2>
        <select value={orderType} onChange={(e) => setOrderType(e.target.value)}>
          <option value="buy">Buy</option>
          <option value="sell">Sell</option>
        </select>

        <input
          type="number"
          placeholder="Price"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
        />

        <input
          type="number"
          placeholder="Quantity"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />

        <button onClick={placeOrder}>Submit Order</button>
      </div>

      <div className="sections">
        <div>
          <h2>Buy Orders</h2>
          {orderBook.buy_orders?.map((order, index) => (
            <p key={index}>Price: {order.price} | Qty: {order.quantity}</p>
          ))}
        </div>

        <div>
          <h2>Sell Orders</h2>
          {orderBook.buy_orders?.map((order, index) => (
            <p key={index}>Price: {order.price} | Qty: {order.quantity}</p>
          ))}
        </div>
      </div>

      <div>
        <h2>Recent Trades</h2>
        {trades.map((trade, index) => (
          <p key={index}>
            Price: {trade.price} | Quantity: {trade.quantity}
          </p>
        ))}
      </div>
    </div>
  );
}

export default App;