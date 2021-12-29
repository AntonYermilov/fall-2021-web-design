import os
from typing import Iterator
from sqlalchemy.orm import Session

from dependency_injector import containers, providers
from dependencies import db, stocks


class Service:
    @staticmethod
    def db() -> Iterator[Session]:
        session = db.Session()
        try:
            yield session
        finally:
            session.close()

    @staticmethod
    def stock_provider() -> stocks.StocksProvider:
        return stocks.StocksProvider()


class Secrets:
    def __init__(self, jwt_secret: str, jwt_algo: str):
        self._jwt_secret = jwt_secret
        self._jwt_algo = jwt_algo

    @property
    def jwt_secret(self):
        return self._jwt_secret

    @property
    def jwt_algo(self):
        return self._jwt_algo


class Context(containers.DeclarativeContainer):
    service = providers.Factory(
        Service
    )
    secrets = providers.Factory(
        Secrets,
        jwt_secret=os.getenv('JWT_SECRET'),
        jwt_algo=os.getenv('JWT_ALGORITHM')
    )
