from sqlalchemy import Column, String, Integer, ForeignKey
from dependencies.db import Base


class Index(Base):
    __tablename__ = 'index'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    index_name = Column(String)
