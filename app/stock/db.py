from sqlalchemy import Column, String, Integer, Float, ForeignKey, UniqueConstraint
from dependencies.db import Base


class Stock(Base):
    __tablename__ = 'stock'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    index_id = Column(Integer, ForeignKey('index.id'))
    ticker = Column(String)
    weight = Column(Float)

    __table_args__ = (
        UniqueConstraint('index_id', 'ticker', name='_index_ticker_uc'),
    )
