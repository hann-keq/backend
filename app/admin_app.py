"""
Standalone FastAPI app for the SQLAdmin dashboard — runs on port 8002.
Same database engine as the main app (port 8000), no shared state needed.

Split into:
  app/admin/auth.py           — AdminAuth backend
  app/admin/models_proxy.py   — Proxy models for pembayaran
  app/admin/views_pembayaran.py — Pembayaran views
  app/admin/views_user.py     — User, Partner, Pet views
  app/admin/views_produk.py   — Produk view
  app/admin/views_partner.py  — JanjiTemu, Dokter views
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqladmin import Admin

from app.core.config import settings
from app.core.database import engine

from app.admin.auth import AdminAuth
from app.admin.views_pembayaran import (
    PembayaranProdukAdmin,
    PembayaranGroomingAdmin,
    PembayaranJanjiTemuAdmin,
)
from app.admin.views_user import UserAdmin, PartnerAdmin, PetAdmin
from app.admin.views_produk import ProductAdmin
from app.admin.views_partner import JanjiTemuAdmin, DokterPartnerAdmin,PaketGroomingPartner


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

auth_backend = AdminAuth(secret_key=settings.SECRET_KEY_GOOGLE)

admin = Admin(
    app=admin_app,
    engine=engine,
    title="PetCare Dashboard",
    base_url="/",
    authentication_backend=auth_backend,
)

admin.add_view(UserAdmin)
admin.add_view(PartnerAdmin)
admin.add_view(PetAdmin)
admin.add_view(JanjiTemuAdmin)
admin.add_view(ProductAdmin)
admin.add_view(PembayaranProdukAdmin)
admin.add_view(PembayaranGroomingAdmin)
admin.add_view(PembayaranJanjiTemuAdmin)
admin.add_view(DokterPartnerAdmin)
admin.add_view(PaketGroomingPartner)

@admin_app.get("/health")
async def health():
    return {"status": "ok", "service": "admin"}
