from fastapi import HTTPException

def handle_user_not_found(detail_message = None):
    raise HTTPException(status_code=404,detail=detail_message or 'User not found')

def handle_email_already_registered():
    raise HTTPException(status_code=400,detail='Email already registered')

def handle_password_mismatch():
    raise HTTPException(status_code=400,detail='Password and confirm password do not match')

def handle_invalid_email_or_password():
    raise HTTPException(status_code=401,detail='Invalid email or password')

def handle_admin_not_found(exception: Exception = None,detail_message = None):
    print(f'Admin not found: {exception or 'No details'}')
    raise HTTPException(status_code=404,detail=detail_message or 'Admin not found')