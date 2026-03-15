candles = {}

def update_candle(symbol, price, quantity, timestamp):
    minute = int(timestamp // 60)

    key = f"{symbol}_{minute}"

    if key not in candles:
        candles[key] = {
            "symbol": symbol,
            "open": price,
            "high": price,
            "low": price,
            "close": price,
            "volume": quantity,
            "time": minute
        }
    else:
        c = candles[key]
        c["high"] = max(c["high"], price)
        c["low"] = min(c["low"], price)
        c["close"] = price
        c["volume"] += quantity