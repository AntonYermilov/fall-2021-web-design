from fastapi import APIRouter, Response, Depends, status
from dependency_injector.wiring import inject, Provide

from .models import Stock
from .service import update_stock
from app.authorization.service import current_user
from app.users import db as user_db
from context import Service, Context

router = APIRouter()


@router.post('/stock/update', status_code=status.HTTP_200_OK, response_model=Stock)
@inject
def add(r: Stock, service: Service = Depends(Provide[Context.service]), user: user_db.User = Depends(current_user)):
    return update_stock(user.id, r, next(service.db()), service.stock_provider())
