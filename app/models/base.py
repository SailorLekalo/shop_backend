from app.db import db_session

session_base = db_session.Base


class Base(session_base):
    __abstract__ = True
