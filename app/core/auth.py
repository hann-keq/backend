from jose import ExpiredSignatureError, JWTError  # 🟢 Tambahkan JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, Request, status
from app.core.security import decode_access_token
from app.repositories.user_repository import get_user_by_id
from app.core.database import get_db
from app.exceptions import user_exceptions, system_exceptions

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    token = None

    # 1. Cek token dari HTTP Header Bearer (Buat Mobile API / Postman / Insomnia)
    authorization: str = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    else:
        # 2. Jika di header kosong, ambil token dari Cookies browser (Buat Jinja HTML Form)
        token = request.cookies.get("access_token")

    # Jika di dua tempat tersebut tokennya tidak ada, langsung hadang 401
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )

    # 🟢 BERSIHKAN TOKEN: Jaga-jaga kalau string "Bearer " ikut tersimpan di cookie browser
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")

    try:
        # 3. Proses Decode Token JWT
        payload = decode_access_token(token)
        user_id: str = payload.get('sub')
        
        if not payload or not user_id:
            raise HTTPException(status_code=401, detail='Invalid token')
        
        # 4. Ambil data User dari Database
        user = await get_user_by_id(db, int(user_id))    
        if not user:
            user_exceptions.handle_user_not_found(detail_message='User not found')
            
        return user

    except ExpiredSignatureError as e:
        system_exceptions.handle_expire_token(e)
        
    # 🟢 KUNCI UTAMA: Tangkap format JWT rusak (seperti error "Not enough segments") di sini
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token format is invalid or corrupted. Please login again."
        )
        
    except Exception as e:
        # Menjaga jika ada crash tidak terduga lainnya (misal error konversi int(user_id))
        system_exceptions.handle_system_error(e)