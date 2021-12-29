from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from . import models as stock_models
from . import db as stock_db
from dependencies.stocks import StocksProvider


def get_stock(user_id: int, index_id: int, ticker: str, db: Session):
    return db.query(stock_db.Stock).filter(
        stock_db.Stock.user_id == user_id,
        stock_db.Stock.index_id == index_id,
        stock_db.Stock.ticker == ticker
    ).first()


def get_stocks(user_id: int, index_id: int, db: Session):
    return db.query(stock_db.Stock).filter(
        stock_db.Stock.user_id == user_id,
        stock_db.Stock.index_id == index_id
    ).all()


def update_stock(user_id: int, stock: stock_models.Stock, db: Session, stocks_provider: StocksProvider) -> stock_models.Stock:
    if stock.weight < 0.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Weight must be positive'
        )

    try:
        stocks_provider.validate_tickers([stock.ticker])
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Unknown ticker: {stock.ticker}'
        )

    db.query(stock_db.Stock).filter(
        stock_db.Stock.user_id == user_id,
        stock_db.Stock.index_id == stock.index_id,
        stock_db.Stock.ticker == stock.ticker
    ).delete()

    if stock.weight > 0.0:
        db_stock = stock_db.Stock(user_id=user_id, index_id=stock.index_id, ticker=stock.ticker, weight=stock.weight)
        db.add(db_stock)

    db.commit()
    return stock
