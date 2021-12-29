from fastapi import APIRouter, Depends, status
from fastapi.responses import HTMLResponse
from dependency_injector.wiring import inject, Provide

from .models import Index, IndexInfo, IndexAddRequest, IndexDelRequest, IndexInfoRequest, VisIndexRequest
from .service import add_index, del_index, index_info, list_indexes, visualize_indexes
from app.authorization.service import current_user
from app.users import db as user_db
from context import Service, Context

router = APIRouter()


@router.post('/index/add', status_code=status.HTTP_200_OK, response_model=Index)
@inject
def add(r: IndexAddRequest, service: Service = Depends(Provide[Context.service]), user: user_db.User = Depends(current_user)):
    return add_index(user.id, r.index_name, next(service.db()))


@router.post('/index/delete', status_code=status.HTTP_200_OK, response_model=Index)
@inject
def delete(r: IndexDelRequest, service: Service = Depends(Provide[Context.service]), user: user_db.User = Depends(current_user)):
    return del_index(user.id, r.index_id, next(service.db()))


@router.post('/index/info', status_code=status.HTTP_200_OK, response_model=IndexInfo)
@inject
def info(r: IndexInfoRequest, service: Service = Depends(Provide[Context.service]), user: user_db.User = Depends(current_user)):
    return index_info(user.id, r.index_id, next(service.db()))


@router.get('/indexes/list', status_code=status.HTTP_200_OK, response_model=list[Index])
@inject
def list(service: Service = Depends(Provide[Context.service]), user: user_db.User = Depends(current_user)):
    return list_indexes(user.id, next(service.db()))


@router.post('/indexes/visualize', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
@inject
def visualize(r: VisIndexRequest, service: Service = Depends(Provide[Context.service]), user: user_db.User = Depends(current_user)):
    return visualize_indexes(user.id, r.index_ids, r.period, r.normalize, next(service.db()), service.stock_provider())
