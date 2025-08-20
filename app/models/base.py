from app.db import db_session

sessionBase = db_session.Base


class Base(sessionBase):
    __abstract__ = True
