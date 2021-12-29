from sqlalchemy.orm import Session

from app.users import db as user_db


def get_user_by_username(username: str, db: Session):
    return db.query(user_db.User).filter(user_db.User.username == username).first()
