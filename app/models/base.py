from app.config import database

class Base(database.Base):
    __abstract__ = True
    pass
