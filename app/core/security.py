from datetime import datetime, timedelta , timezone
from jose import jwt

import bcrypt
from app.core.config import settings



#hash password
def hash_password(password):
    password_byte = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_byte,salt)
    return hashed_password.decode('utf-8')
#verify password
def verify_password(plain_password,hashed_password):
    plain_password_byte = plain_password.encode('utf-8')
    hashed_password_byte = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password_byte,hashed_password_byte)

#create access token for 1 hour
def create_access_token(data: dict):
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp' : expires})
    if 'user_id' in to_encode:
        to_encode['sub'] = str(to_encode['user_id'])
    encode_jwt = jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    return encode_jwt

#create refresh token for 90 days in order not to ask user to login again after access token expired
def create_refresh_token(data:dict):
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE)
    to_encode.update({'exp': expires})
    if 'user_id' in to_encode:
        to_encode['sub'] = str(to_encode['user_id'])
    encode = jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    return encode

#decode access token
def decode_access_token(token:str):
    payload = jwt.decode(token,settings.SECRET_KEY,algorithms=settings.ALGORITHM)
    return payload


#decode refresh token to get new access token without asking user to login again
def decode_refresh_token(token:str):
    payload = jwt.decode(token,settings.SECRET_KEY,algorithms=settings.ALGORITHM)
    return payload

