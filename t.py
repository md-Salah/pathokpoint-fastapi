# import app.auth.jwt_handler as auth_service
# from uuid import uuid4
# import time

# token = auth_service.create_jwt_token(uuid4(), 'admin')
# print(token)
# time.sleep(4)

# token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijc0YTBlNDVjLTY2ZDUtNGQ1NS1iOTY4LTg3Y2EzNWQwYjA1NyIsInJvbGUiOiJhZG1pbiIsImV4cGlyZXMiOjE3MDgzNTAyMDAuNzk3NjA0fQ.Mn5X5_-e2Syf8Kq_k5eXcQy8-i1-6wDzs7cDEXOfOy4'

# print(auth_service.verify_token(token)) 
# # InvalidSignatureError: Signature verification failed
# # ExpiredSignatureError: Token has expired


from app.config.settings import settings

# settings = get_settings()

# print(settings.DATABASE_URL)