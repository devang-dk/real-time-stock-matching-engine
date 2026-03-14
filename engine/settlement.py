from sqlmodel import Session, select
from models import User, Holding, Trade


def settle_trade(session: Session, buyer_id, seller_id, symbol, price, quantity):

    buyer = session.get(User, buyer_id)
    seller = session.get(User, seller_id)

    trade_value = price * quantity

    # update balances
    buyer.balance -= trade_value
    seller.balance += trade_value

    # buyer holdings
    statement = select(Holding).where(
        Holding.user_id == buyer_id,
        Holding.symbol == symbol
    )

    buyer_holding = session.exec(statement).first()

    if buyer_holding:
        buyer_holding.quantity += quantity
    else:
        buyer_holding = Holding(
            user_id=buyer_id,
            symbol=symbol,
            quantity=quantity
        )
        session.add(buyer_holding)

    # seller holdings
    statement = select(Holding).where(
        Holding.user_id == seller_id,
        Holding.symbol == symbol
    )

    seller_holding = session.exec(statement).first()

    if seller_holding:
        seller_holding.quantity -= quantity

    # record trade
    trade = Trade(
        buyer_id=buyer_id,
        seller_id=seller_id,
        symbol=symbol,
        price=price,
        quantity=quantity
    )

    session.add(trade)

    session.commit()