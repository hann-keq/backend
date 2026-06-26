"""
Standalone FastAPI app for the admin dashboard — runs on port 8002.

Replaced SQLAdmin with custom FastAPI + Jinja2 + HTMX routers under
``admin_custom/``.  Session cookie: ``admin_session`` (separate from the
main app on port 8000).
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings

# --- custom router imports ---
from app.admin_custom.auth_router import router as auth_router
from app.admin_custom.router import router as partner_router
from app.admin_custom.routers_admin import router as admin_router

# =========================================================
# STANDALONE FASTAPI APP (port 8002)
# =========================================================

admin_app = FastAPI(
    title="PetCare Admin Dashboard",
    version="1.0.0",
)

admin_app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY_GOOGLE,
    session_cookie="admin_session",
    same_site="lax",
)

admin_app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- custom routers (replace SQLAdmin) ---
admin_app.include_router(auth_router)       # /login, /logout
admin_app.include_router(admin_router)      # /dashboard-admin/users, /partners, /pets, /products, /pembayaran/*
admin_app.include_router(partner_router)    # /dashboard-admin/paket, /dokter, /janji-temu, /detail-paket


@admin_app.get("/health")
async def health():
    return {"status": "ok", "service": "admin_custom"}
