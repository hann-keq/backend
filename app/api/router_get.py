from fastapi import APIRouter, Depends, HTTPException, status,Request,Form
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
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


#not a test code
@router.get('/petcaredashboard.html', response_class=HTMLResponse)
async def tampilin_dashboard(request: Request):
    return templates.TemplateResponse(request,'petcaredashboard.html')


@router.get('/login', response_class=HTMLResponse)
async def tampilin_halaman_login(request: Request):
    return templates.TemplateResponse(request,'login.html')

@router.get('/petshop.html', response_class=HTMLResponse)
async def tampilin_petshop(request: Request):
    return templates.TemplateResponse(request,'petshop.html')
