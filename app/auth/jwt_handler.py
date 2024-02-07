import time
import jwt
import os
from passlib.context import CryptContext
from dotenv import load_dotenv


load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET_KEY')
if not JWT_SECRET or not JWT_ALGORITHM or not JWT_REFRESH_SECRET_KEY:
    raise ValueError('JWT_SECRET and JWT_ALGORITHM must be set in .env file')

#  Function to create a JWT token
def create_jwt_token(id: int, email: str, role: str) -> str:
    payload = {
        "id": id,
        'email': email,
        'role': role,
        "expires": time.time() + 259200
    }
    token = jwt.encode(payload, JWT_SECRET,
                       algorithm=JWT_ALGORITHM)
    return token

#  Function to create a JWT token
def create_refresh_token(id: int, email: str, role: str) -> str:
    payload = {
        "id": id,
        'email': email,
        'role': role,
        "expires": time.time() + 259200
    }
    token = jwt.encode(payload, JWT_SECRET,
                       algorithm=JWT_ALGORITHM)    
    return token


# Function to decode a JWT token
def decode_jwt_token(token: str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[
                                   JWT_ALGORITHM])  
        return decoded_token if decoded_token['expires'] >= time.time() else None
    except Exception:
        return None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, database_hashed_password):
    return pwd_context.verify(plain_password, database_hashed_password)

