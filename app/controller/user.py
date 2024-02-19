from sqlalchemy.orm import Session

from app.models.user import User
import app.pydantic_schema.user as user_schema


def is_user_exist(db: Session, email: str):
    return db.query(User).filter(
        User.email == email,
    ).first()

def create_user(db: Session, user: user_schema.CreateUser) -> user_schema.ReadUser:
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
