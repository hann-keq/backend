from fastapi import APIRouter, Depends, HTTPException, status,Request,Form
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from app.core.auth import get_current_user
from app.core.security import create_access_token
from app.exceptions import system_exceptions, user_exceptions
from app.schemas.product_schema.schema import ProductCreate
from app.schemas.user_schema.user_create import AdminCreate, AdminLogin, UserLogin
from app.services.product import product_service
from app.services.user import user_service
from app.core.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post('/admin/add-product', response_class=HTMLResponse)
async def add_product(request: Request, product_data: ProductCreate = Depends(ProductCreate.as_form),
                    db: AsyncSession = Depends(get_db),
                    admin_data = Depends(get_current_user)):
    try:
        # Implement logic to add product using product_data and admin_data
        print('bersiap verisikasi admin')
        print(f'admin data: {admin_data.id_user}')
        verify_admin = await user_service.get_current_admin_by_id(admin_data.id_user, db)
        if not verify_admin:
            return user_exceptions.handle_admin_not_found(detail_message='Admin tidak ditemukan')
        print('lolos verifikasi')
        add_product = await product_service.add_product(db, product_data)
        print('lolos add product')
        respionse = HTMLResponse(content="Product added successfully")
        return respionse
    except Exception as e:
        system_exceptions.handle_system_error(e)

@router.post('/admin/login',response_class=HTMLResponse)
async def admin_login(request: Request, admin_login_data: AdminLogin = Depends(AdminLogin.as_form),db:AsyncSession = Depends(get_db) ):
    try:
        admin = await user_service.login_admin(db,admin_login_data)
        if not admin:
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password"})
        access_token = create_access_token(data={"sub": str(admin.id_user)})
        response = HTMLResponse(content="Login successful")
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    except Exception as e:
        system_exceptions.handle_system_error(e)

@router.post('/admin/register', response_class=HTMLResponse)
async def register_admin(admin_data: AdminCreate, db:AsyncSession = Depends(get_db)):
    try:
        admin = await user_service.create_new_admin(db, admin_data)
        return admin
    except Exception as e:
        system_exceptions.handle_system_error(e)

@router.post('/admin/add-partner', response_class=HTMLResponse)
async def add_partner(partner_data: dict, db: AsyncSession = Depends(get_db), admin_data: dict = Depends(get_current_user)):
    try:
        verify_admin = await user_service.get_current_admin_by_id(admin_data, db)
        if not verify_admin:
            return user_exceptions.handle_admin_not_found(detail_message='Admin tidak ditemukan')
        add_partner = await product_service.add_partner(db, partner_data)
        return add_partner
    except Exception as e:
        system_exceptions.handle_system_error(e)