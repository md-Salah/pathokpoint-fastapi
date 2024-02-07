from sqlmodel import create_engine, Session, SQLModel

DATABASE_URI = 'sqlite:///test_db.db'

engine = create_engine(DATABASE_URI, connect_args={"check_same_thread": False})

# Create tables
def create_tables():
    SQLModel.metadata.create_all(engine)

# Drop tables
def drop_tables():
    SQLModel.metadata.drop_all(engine)

# get DB Session
def get_db():
    with Session(engine) as db:
        yield db

        
        