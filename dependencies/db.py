from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import declarative_base

Engine = create_engine('sqlite:///app.db')
Session = scoped_session(sessionmaker(bind=Engine, autocommit=False, autoflush=False))
Base = declarative_base()
