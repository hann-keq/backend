"""Login/logout routes for admin_custom — mirrors AdminAuth.login()."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import engine
from app.core.security import verify_password
from app.core.templates import templates
from app.models.models import User, Partner, RoleUser

router = APIRouter(tags=["admin_auth"])

_T = "admin_custom"


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, f"{_T}/login.html", {"request": request})


@router.post("/login")
async def login(request: Request):
    form = await request.form()
    email = str(form.get("username", "")).strip()
    password = str(form.get("password", ""))
    error = "Email atau password salah."

    if not email or not password:
        return templates.TemplateResponse(request, 
            f"{_T}/login.html", {"request": request, "error": "Email dan password wajib diisi.", "email": email},
            status_code=401,
        )

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # 1. Check users table (admin role)
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user and verify_password(password, user.password) and user.role == RoleUser.ADMIN:
            request.session.update({
                "user_role": "admin",
                "user_id": user.id_user,
            })
            return RedirectResponse(url="/dashboard-admin/users", status_code=303)

        # 2. Check partners table
        result = await session.execute(
            select(Partner).where(Partner.email == email, Partner.email.is_not(None))
        )
        partner = result.scalar_one_or_none()
        if partner and verify_password(password, partner.password):
            request.session.update({
                "user_role": "partner",
                "partner_id": partner.id_partner,
                "jenis_partner": partner.jenis_partner.value,
            })
            return RedirectResponse(url="/dashboard-admin/paket", status_code=303)

    return templates.TemplateResponse(request, 
        f"{_T}/login.html", {"request": request, "error": error, "email": email},
        status_code=401,
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
