from pydantic import BaseModel

from app.stock.models import Stock


class Index(BaseModel):
    index_id: int
    index_name: str


class IndexInfo(BaseModel):
    index: Index
    stocks: list[Stock]


class IndexAddRequest(BaseModel):
    index_name: str


class IndexDelRequest(BaseModel):
    index_id: int


class IndexInfoRequest(BaseModel):
    index_id: int


class VisIndexRequest(BaseModel):
    index_ids: list[int]
    period: str = '1y'
    normalize: bool = False
