market_data = {}

def update_ticker(symbol, price, quantity):

    if symbol not in market_data:
        market_data[symbol] = {
            "last_price": price,
            "volume": 0
        }

    market_data[symbol]["last_price"] = price
    market_data[symbol]["volume"] += quantity


def get_ticker(symbol):
    return market_data.get(symbol, {
        "last_price": None,
        "volume": 0
    })