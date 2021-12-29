import numpy as np
import plotly.graph_objs as go
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Tuple

from . import models as index_models
from . import db as index_db
from app.stock import models as stock_models
from app.stock import db as stock_db
from app.stock.service import get_stocks
from dependencies.stocks import StocksProvider


def get_index(user_id: int, index_id: int, db: Session):
    return db.query(index_db.Index).filter(index_db.Index.user_id == user_id, index_db.Index.id == index_id).first()


def add_index(user_id: int, index_name: str, db: Session) -> index_models.Index:
    db_index = index_db.Index(user_id=user_id, index_name=index_name)
    db.add(db_index)
    db.commit()
    db.refresh(db_index)
    return index_models.Index(index_id=db_index.id, index_name=db_index.index_name)


def del_index(user_id: int, index_id: int, db: Session) -> index_models.Index:
    db_index = get_index(user_id, index_id, db)
    if db_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Stock index with id {index_id} does not exist'
        )

    db.query(index_db.Index).filter(index_db.Index.user_id == user_id, index_db.Index.id == index_id).delete()
    db.commit()
    return index_models.Index(index_id=db_index.id, index_name=db_index.index_name)


def index_info(user_id: int, index_id: int, db: Session) -> index_models.IndexInfo:
    db_index = get_index(user_id, index_id, db)
    db_stocks = get_stocks(user_id, index_id, db)
    return index_models.IndexInfo(
        index=index_models.Index(
            index_id=db_index.id,
            index_name=db_index.index_name
        ),
        stocks=[
            stock_models.Stock(
                index_id=index_id,
                ticker=stock.ticker,
                weight=stock.weight
            ) for stock in db_stocks
        ]
    )


def list_indexes(user_id: int, db: Session) -> list[index_models.Index]:
    db_indexes = db.query(index_db.Index).filter(index_db.Index.user_id == user_id).all()
    return [index_models.Index(index_id=index.id, index_name=index.index_name) for index in db_indexes]


def historical_index_price(db_stocks: list[stock_db.Stock], period: str, stocks_provider: StocksProvider) -> Tuple[list[str], np.ndarray]:
    tickers = [stock.ticker for stock in db_stocks]
    prices = stocks_provider.get_historical_price(tickers, period)
    total_weight = sum(stock.weight for stock in db_stocks)

    x = [date.strftime('%Y-%m-%d %H:%M:%S') for date in prices.index]
    y = sum(prices[stock.ticker] * stock.weight for stock in db_stocks).to_numpy() / total_weight
    return x, y


def visualize_indexes(user_id, index_ids: list[int], period: str, normalize: bool, db: Session, stocks_provider: StocksProvider) -> str:
    available_periods = '1mo,3mo,6mo,1y,2y,5y,10y'.split(',')
    if period not in available_periods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Available period values: {available_periods}'
        )

    indexes = []
    for index_id in index_ids:
        db_index = get_index(user_id, index_id, db)
        if db_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Stock index with id {index_id} does not exist'
            )

        db_stocks = get_stocks(user_id, index_id, db)
        if not db_stocks:
            continue

        dates, prices = historical_index_price(db_stocks, period, stocks_provider)
        indexes.append({
            'title': db_index.index_name,
            'x': dates,
            'y': prices
        })

    if not indexes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='All requested indexes are empty'
        )

    fig = go.Figure()
    for index in indexes:
        x, y, title = index['x'], index['y'], index['title']
        divisor = y[0] if normalize else 1.0
        fig.add_trace(go.Scatter(x=index['x'], y=index['y'] / divisor, name=title))

    return fig.to_html()
