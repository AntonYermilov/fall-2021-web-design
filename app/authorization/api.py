from fastapi import APIRouter, Response, Depends, status
from dependency_injector.wiring import inject, Provide

from .service import register_user, login_user
from app.users.models import User
from context import Service, Context

router = APIRouter()


@router.post('/auth/register', status_code=status.HTTP_200_OK)
@inject
def register(user: User, service: Service = Depends(Provide[Context.service])):
    register_user(user, next(service.db()))
    return {'detail': f'User "{user.username}" successfully registered'}


@router.post('/auth/login', status_code=status.HTTP_200_OK, response_model=str)
@inject
def login(user: User, service: Service = Depends(Provide[Context.service])):
    token = login_user(user, next(service.db()))
    return Response(content=token, media_type='plain/text')
