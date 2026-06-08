from fastapi import APIRouter, Depends, HTTPException, status,Request,Form
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from app.exceptions import system_exceptions, user_exceptions
from app.core.database import get_db


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")