from fastapi import APIRouter, Depends, HTTPException, status,Request,Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from app.core.database import get_db
from app.core.security import decode_access_token
from app.exceptions import system_exceptions
from app.schemas.user_schema.user_response import UserResponseOnlyId
from app.services.user.user_service import get_user_by_id


templates = Jinja2Templates(directory="app/templates")
router = APIRouter()



#test code
@router.get('/test-decode-token')
async def test_decode_from_input(data :str):
    try:
        payload = decode_access_token(data)
        return payload
    except Exception as e:
        system_exceptions.handle_expire_token(e)

@router.get("/users/get-users", response_model=UserResponseOnlyId)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
    )
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('notification.html', response_class=HTMLResponse,name='notification')
async def tampilin_notification(request: Request):
    return templates.TemplateResponse(request,'notification.html')

@router.get('helpcenter.html', response_class=HTMLResponse,name='help')
async def tampilin_helpcenter(request: Request):
    return templates.TemplateResponse(request,'helpcenter.html')

@router.get('/settings.html', response_class=HTMLResponse,name='settings')
async def tampilin_settings(request: Request):
    return templates.TemplateResponse(request,'settings.html')

@router.get('/payment.html', response_class=HTMLResponse,name='payment')
async def tampilin_payment(request: Request):
    return templates.TemplateResponse(request,'payment.html')

@router.get('/address.html', response_class=HTMLResponse,name='address')
async def tampilin_address(request: Request):
    return templates.TemplateResponse(request,'address.html')

@router.get('/favorites.html', response_class=HTMLResponse,name='favorites')
async def tampilin_favorites(request: Request):
    return templates.TemplateResponse(request,'favorites.html')

@router.get('/orders.html', response_class=HTMLResponse,name='orders')
async def tampilin_orders(request: Request):
    return templates.TemplateResponse(request,'orders.html')


@router.get('/booking.html', response_class=HTMLResponse,name='booking')
async def tampilin_booking(request: Request):
    return templates.TemplateResponse(request,'booking.html')

@router.get('/profile.html', response_class=HTMLResponse,name='profile')
async def tampilin_profile(request: Request):
    return templates.TemplateResponse(request,'profile.html')

@router.get('/notification.html', response_class=HTMLResponse,name='notification')
async def tampilin_notification(request: Request):
    return templates.TemplateResponse(request,'notification.html')


@router.get('/appointments.html', response_class=HTMLResponse,name='appointments')
async def tampilin_appointments(request: Request):
    return templates.TemplateResponse(request,'appointments.html')


@router.get('/favorites.html', response_class=HTMLResponse,name='favorites')
async def tampilin_favorites(request: Request):
    return templates.TemplateResponse(request,'favorites.html')

@router.get('/new-pet.html', response_class=HTMLResponse,name='new-pet')
async def tampilin_new_pet(request: Request):
    return templates.TemplateResponse(request,'new-pet.html')


#not a test code
@router.get('/petcaredashboard.html', response_class=HTMLResponse,name='petcaredashboard')
async def tampilin_dashboard(request: Request):
    return templates.TemplateResponse(request,'petcaredashboard.html')


@router.get('/login', response_class=HTMLResponse,name='login.html')
async def tampilin_halaman_login(request: Request):
    return templates.TemplateResponse(request,'login.html')

@router.get('/petshop.html', response_class=HTMLResponse,name='petshop')
async def tampilin_petshop(request: Request):
    return templates.TemplateResponse(request,'petshop.html')

# @router.get()
