from pydantic import BaseModel


class Stock(BaseModel):
    index_id: int
    ticker: str
    weight: float
