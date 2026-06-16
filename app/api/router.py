from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status,Request,Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token
from app.core.auth import get_current_user

from app.models.models import User
from app.services.pet.pet_service import add_pet
from app.exceptions import user_exceptions, system_exceptions
from app.schemas.pet_schema.pet_create import PetCreate
from app.schemas.pet_schema.pet_response import PetResponse
from app.schemas.user_schema.user_create import UserCreate
from app.schemas.user_schema.user_response import UserResponse, UserResponseOnlyId
from app.schemas.product_schema.schema import ProductCreate,ProductResponse
from sqlalchemy import select
from app.services.product import product_service
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from app.services.alamat import service as alamat_service
from app.schemas.alamat_schema import schema as alamat_schema

from app.services.user.user_service import create_new_user, login_user, login_admin,create_new_admin,get_user_by_id
from app.services.user import user_service
templates = Jinja2Templates(directory="app/templates")
router = APIRouter()




@router.post("/register", response_class=HTMLResponse)
async def sign_up(
    request: Request,
    nama: str = Form(...),
    email: str = Form(...),
    no_telepon: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    
    db:AsyncSession = Depends(get_db)):
    try:
        new_user = UserCreate(
            nama=nama,
            email=email,
            no_telepon=no_telepon,
            password=password,
            confirm_password=confirm_password
        )
        user = await create_new_user(db, new_user)
        if user:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    except:
            return templates.TemplateResponse(
                request=request, 
                name='signup.html', 
                context={
                    "request": request, 
                    "error": "Email already registered", # Kirim pesan ke Jinja
                    "nama": nama,                         # Data input dikembalikan biar ga ngetik ulang
                    "email": email,
                    "no_telepon": no_telepon
                },
                status_code=400 # Browser tetap membaca ini sebagai error 400 Bad Request
            )
    




@router.post('/login', response_class=HTMLResponse)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    form_data = {"email": email, "password": password}
    user = await login_user(db, form_data)

    if not user:
        return templates.TemplateResponse(request = request,name='login.html', context={"error":"Invalid email or password"})

    # 1. BUAT ACCESS TOKEN KAMU SEPERTI BIASA
    access_token = create_access_token(data={"sub": str(user.id_user)})

    # 2. BIKIN RESPONS REDIRECT
    response = RedirectResponse(url="/petcaredashboard", status_code=status.HTTP_303_SEE_OTHER)
    
    # 3. TITIPKAN TOKEN KE COOKIE BROWSER (Mirip $_SESSION di PHP)
    # httponly=True bikin token aman dari serangan XSS Javascript jahat
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    
    return response




@router.post('/pets/add', response_class=HTMLResponse)
async def add_user_new_pet(
      request: Request,
      
      pet_name: str = Form(...),
      jenis_hewan:str = Form(...),
      umur:int = Form(...),
      berat:int = Form(...),
      gender:str = Form(...),
      db:AsyncSession = Depends(get_db), 
      user_id: int = Depends(get_current_user)):
    try: 
        pet_data = PetCreate(
            nama_hewan=pet_name,
            jenis_hewan=jenis_hewan,
            umur=umur,
            berat=berat,
            gender_hewan=gender,


        )
        referer = request.headers.get("Referer")
        print(f'Referer: {referer}')
        
        print(f'User id = {user_id.id_user}')
        pet = await add_pet(db,user_id.id_user,pet_data)
        print(f'Pet added: {pet}')
        if "profile" in referer:
            origin_page = "/profile"
        elif "petcaredashboard" in referer:
            origin_page = "/petcaredashboard"
        print (f'Origin page: {origin_page}')
        return RedirectResponse(url=origin_page, status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)

@router.post('/address/add', response_class=HTMLResponse)
async def add_user_new_address(
    alamat : alamat_schema.AlamatCreate = Depends(),
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
  try:
       await alamat_service.create_new_alamat(db, alamat, user.id_user)
       return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
  except Exception as e:
        system_exceptions.handle_system_error(e)



    