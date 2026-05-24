from fastapi import HTTPException
from jose import JWTError,ExpiredSignatureError

def handle_jwt_error(e: JWTError):
    print(f'JWT error: {e}')
    raise HTTPException(status_code=401,detail='Invalid token or token expired')

def handle_system_error(e: Exception):
    print(f'System error: {e}')
    raise HTTPException(status_code=500,detail='Internal server error')

def handle_expire_token(e: ExpiredSignatureError):
    print(f'Token expired: {e}')
    raise HTTPException(status_code=401,detail='Token expired, please login again')
