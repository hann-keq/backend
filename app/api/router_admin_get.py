from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse
from app.core.templates import templates
from app.exceptions import system_exceptions, user_exceptions
from app.core.database import get_db


router = APIRouter()