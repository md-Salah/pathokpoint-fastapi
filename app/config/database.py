from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from app.config.settings import settings

engine = create_engine(settings.DATABASE_URL, echo=False)
Base = declarative_base()

# Create tables
def create_tables():
    Base.metadata.create_all(engine)

# Drop tables
def drop_tables():
    Base.metadata.drop_all(engine)

# get DB Session
def get_db():
    with Session(engine) as db:
        yield db



        
        