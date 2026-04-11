from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#ubah plain password ke hash
def get_password_hash(password):
    return pwd_context.hash(password)

#cek apakah input sesuai dengan password yang sudah di hash
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)