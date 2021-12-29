from fastapi import FastAPI, Request

from app import authorization, index, stock, users
from app.authorization.api import router as auth_router
from app.index.api import router as index_router
from app.stock.api import router as stock_router

from context import Context
from dependencies.db import Engine, Base


Base.metadata.create_all(bind=Engine)

context = Context()
context.wire(packages=[authorization])
context.wire(packages=[index])
context.wire(packages=[stock])
context.wire(packages=[users])

app = FastAPI()
app.include_router(auth_router)
app.include_router(index_router)
app.include_router(stock_router)
