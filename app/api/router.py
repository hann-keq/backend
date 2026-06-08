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


from app.services.user.user_service import create_new_user, login_user, login_admin,create_new_admin,get_user_by_id
from app.services.user import user_service
templates = Jinja2Templates(directory="app/templates")
router = APIRouter()




@router.post("/register/", response_model=UserResponse)
async def sign_up(new_user : UserCreate, db:AsyncSession = Depends(get_db)):
    return await create_new_user(db, new_user)





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
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password"})

    # 1. BUAT ACCESS TOKEN KAMU SEPERTI BIASA
    access_token = create_access_token(data={"sub": str(user.id_user)})

    # 2. BIKIN RESPONS REDIRECT
    response = RedirectResponse(url="/petcaredashboard.html", status_code=status.HTTP_303_SEE_OTHER)
    
    # 3. TITIPKAN TOKEN KE COOKIE BROWSER (Mirip $_SESSION di PHP)
    # httponly=True bikin token aman dari serangan XSS Javascript jahat
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    
    return response




@router.post('/users/pets/add', response_class=HTMLResponse)
async def add_user_new_pet(pet_data: PetCreate, db:AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user)):
    try: 
        print(f'User id = {user_id.id_user}')
        pet = await add_pet(db,user_id.id_user,pet_data)
        print(f'Pet added: {pet}')
        return pet
    except Exception as e:
        system_exceptions.handle_system_error(e)





    