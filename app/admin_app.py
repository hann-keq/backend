"""
Standalone FastAPI app for the SQLAdmin dashboard — runs on port 8002.
Same database engine as the main app (port 8000), no shared state needed.
"""
import os

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from sqladmin import Admin, ModelView, action
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload
from wtforms import FileField
from markupsafe import Markup
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import engine
from app.models.models import (
    Dokter, Pembayaran, Pet, JanjiTemu, User, Partner, RoleUser, Produk,
)
from app.core.security import hash_password, verify_password


# =========================================================
# PROXY MODELS — split pembayaran by FK
# =========================================================
class PembayaranProdukModel(Pembayaran):
    pass

class PembayaranGroomingModel(Pembayaran):
    pass

class PembayaranJanjiTemuModel(Pembayaran):
    pass


# =========================================================
# MODEL VIEWS
# =========================================================

class PembayaranProdukAdmin(ModelView, model=PembayaranProdukModel):
    name = "Pembayaran Produk"
    name_plural = "Pembayaran Produk"
    icon = "fa-solid fa-box"
    category = "Daftar Pembayaran"
    category_icon = "fa-solid fa-bars"

    column_list = [
        PembayaranProdukModel.id_pembayaran,
        PembayaranProdukModel.id_user,
        PembayaranProdukModel.id_order_produk,
        PembayaranProdukModel.jumlah_bayar,
        PembayaranProdukModel.metode_pembayaran,
        PembayaranProdukModel.status_pembayaran,
        PembayaranProdukModel.created_at,
    ]

    def list_query(self, request: Request):
        return select(PembayaranProdukModel).where(
            PembayaranProdukModel.id_order_produk.isnot(None)
        )

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"

    @action(
        name="mark_as_completed",
        label="Tandai Dibayar",
        confirmation_message="Yakin ingin mengubah status menjadi DIBAYAR?",
        add_in_list=True,
        add_in_detail=True,
    )
    async def mark_as_completed(self, request: Request):
        pks = request.query_params.getlist("pks")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            for pk in pks:
                result = await session.execute(
                    select(PembayaranProdukModel).where(
                        PembayaranProdukModel.id_pembayaran == int(pk)
                    )
                )
                pembayaran = result.scalar_one_or_none()
                if pembayaran:
                    pembayaran.status_pembayaran = "DIBAYAR"
            await session.commit()
        return RedirectResponse(request.headers.get("referer", "/admin/pembayaran-produk-model/list"), status_code=303)


class PembayaranGroomingAdmin(ModelView, model=PembayaranGroomingModel):
    name = "Pembayaran Grooming"
    name_plural = "Pembayaran Grooming"
    icon = "fa-solid fa-dog"
    category = "Daftar Pembayaran"
    category_icon = "fa-solid fa-bars"

    column_list = [
        PembayaranGroomingModel.id_pembayaran,
        "user.nama",
        PembayaranGroomingModel.id_booking_grooming,
        PembayaranGroomingModel.jumlah_bayar,
        PembayaranGroomingModel.metode_pembayaran,
        PembayaranGroomingModel.status_pembayaran,
        PembayaranGroomingModel.created_at,
    ]
    column_labels = {"user.nama": "Nama User"}

    def list_query(self, request: Request):
        return select(PembayaranGroomingModel).options(
            joinedload(PembayaranGroomingModel.user)
        ).where(PembayaranGroomingModel.id_booking_grooming.isnot(None))

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"

    @action(
        name="mark_as_completed",
        label="Tandai Dibayar",
        confirmation_message="Yakin ingin mengubah status menjadi DIBAYAR?",
        add_in_list=True,
        add_in_detail=True,
    )
    async def mark_as_completed(self, request: Request):
        pks = request.query_params.getlist("pks")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            for pk in pks:
                result = await session.execute(
                    select(PembayaranGroomingModel).where(
                        PembayaranGroomingModel.id_pembayaran == int(pk)
                    )
                )
                pembayaran = result.scalar_one_or_none()
                if pembayaran:
                    pembayaran.status_pembayaran = "DIBAYAR"
            await session.commit()
        return RedirectResponse(request.headers.get("referer", "/admin/pembayaran-grooming-model/list"), status_code=303)

    @action(
        name="mark_as_menunggu",
        label="Tandai Menunggu",
        confirmation_message="Yakin ingin mengubah status menjadi MENUNGGU?",
        add_in_list=True,
        add_in_detail=True,
    )
    async def mark_as_menunggu(self, request: Request):
        pks = request.query_params.getlist("pks")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            for pk in pks:
                result = await session.execute(
                    select(PembayaranGroomingModel).where(
                        PembayaranGroomingModel.id_pembayaran == int(pk)
                    )
                )
                pembayaran = result.scalar_one_or_none()
                if pembayaran:
                    pembayaran.status_pembayaran = "MENUNGGU"
            await session.commit()
        return RedirectResponse(request.headers.get("referer", "/admin/pembayaran-grooming-model/list"), status_code=303)


class PembayaranJanjiTemuAdmin(ModelView, model=PembayaranJanjiTemuModel):
    name = "Pembayaran Janji Temu"
    name_plural = "Pembayaran Janji Temu"
    icon = "fa-solid fa-calendar-check"
    category = "Daftar Pembayaran"
    category_icon = "fa-solid fa-bars"
    page_size = 50

    column_list = [
        PembayaranJanjiTemuModel.id_pembayaran,
        PembayaranJanjiTemuModel.id_user,
        PembayaranJanjiTemuModel.id_janji_temu,
        PembayaranJanjiTemuModel.jumlah_bayar,
        PembayaranJanjiTemuModel.metode_pembayaran,
        PembayaranJanjiTemuModel.status_pembayaran,
        PembayaranJanjiTemuModel.created_at,
    ]

    def list_query(self, request: Request):
        return select(PembayaranJanjiTemuModel).where(
            PembayaranJanjiTemuModel.id_janji_temu.isnot(None)
        )

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"

    @action(
        name="mark_as_completed",
        label="Tandai Dibayar",
        confirmation_message="Yakin ingin mengubah status menjadi DIBAYAR?",
        add_in_list=True,
        add_in_detail=True,
    )
    async def mark_as_completed(self, request: Request):
        pks = request.query_params.getlist("pks")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            for pk in pks:
                result = await session.execute(
                    select(PembayaranJanjiTemuModel).where(
                        PembayaranJanjiTemuModel.id_pembayaran == int(pk)
                    )
                )
                pembayaran = result.scalar_one_or_none()
                if pembayaran:
                    pembayaran.status_pembayaran = "DIBAYAR"
            await session.commit()
        return RedirectResponse(request.headers.get("referer", "/admin/pembayaran-janji-temu-model/list"), status_code=303)


class UserAdmin(ModelView, model=User):
    name = "Data User/Admin"
    name_plural = "Kelola User & Admin"
    icon = "fa-solid fa-users"
    column_list = [User.id_user, User.nama, User.email, User.role]
    form_columns = ["nama", "email", "no_telepon", "password", "role"]

    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        if "password" in data and data["password"]:
            data["password"] = hash_password(data["password"])

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"


class PartnerAdmin(ModelView, model=Partner):
    name = "Data Partner"
    name_plural = "Kelola Partner"
    icon = "fa-solid fa-handshake"
    column_list = [Partner.id_partner, Partner.nama_partner, Partner.jenis_partner, Partner.email]
    form_columns = ["nama_partner", "jenis_partner", "alamat", "no_telepon", "email", "password"]

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"


class PetAdmin(ModelView, model=Pet):
    name = "Data Hewan"
    name_plural = "Daftar Hewan"
    icon = "fa-solid fa-paw"
    column_list = [Pet.id_pet, Pet.nama_hewan, Pet.jenis_hewan, Pet.id_user]

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"


class ProductAdmin(ModelView, model=Produk):
    name = "Data Produk"
    name_plural = "Daftar Produk"
    icon = "fa-solid fa-box-open"
    column_list = [Produk.id_produk, Produk.nama_produk, Produk.harga, Produk.stok]

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"


class JanjiTemuAdmin(ModelView, model=JanjiTemu):
    name = "Data Janji Temu"
    name_plural = "Janji Temu"
    icon = "fa-solid fa-calendar"
    column_list = [
        JanjiTemu.id_user,
        "partner.partner.nama_partner",
        JanjiTemu.jam_janji,
        JanjiTemu.tanggal_janji,
        JanjiTemu.status_janji,
    ]
    column_labels = {"partner.partner.nama_partner": "Nama Partner"}

    def list_query(self, request: Request):
        partner_id = request.session.get("partner_id")
        if not partner_id:
            return select(JanjiTemu).where(False)
        return (
            select(JanjiTemu)
            .join(JanjiTemu.Dokter)
            .options(joinedload(JanjiTemu.Dokter).joinedload(Dokter.partner))
            .where(Dokter.id_partner == partner_id)
        )

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") in ["partner"]


class DokterPartnerAdmin(ModelView, model=Dokter):
    name = "Data Dokter"
    name_plural = "Daftar Dokter"
    icon = "fa-solid fa-user-md"
    column_list = [
        'foto', Dokter.id_dokter, Dokter.nama_dokter, Dokter.spesialis,
        "partner.partner.nama_partner",
    ]
    column_labels = {
        'foto': 'Foto Profil',
        "partner.partner.nama_partner": "Nama Partner",
    }
    form_columns = ['nama_dokter', 'spesialis', 'foto']
    form_overrides = {'foto': FileField}

    column_formatters = {
        'foto': lambda model, attr: Markup(
            f'<img src="{model.foto}" class="img-thumbnail" '
            f'style="max-height:50px;max-width:50px;border-radius:50%;object-fit:cover;">'
        ) if model.foto else Markup('<i class="fa-solid fa-user-doctor fa-2x text-secondary"></i>')
    }

    def list_query(self, request: Request):
        partner_id = request.session.get("partner_id")
        if not partner_id:
            return select(Dokter).where(False)
        return (
            select(Dokter)
            .options(joinedload(Dokter.partner))
            .where(Dokter.id_partner == partner_id)
        )

    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        partner_id = request.session.get("partner_id")
        if partner_id:
            data["id_partner"] = partner_id
        if "foto" in data and data["foto"]:
            file_data = data["foto"]
            if hasattr(file_data, 'filename') and file_data.filename:
                upload_dir = "app/static/uploads/dokter"
                os.makedirs(upload_dir, exist_ok=True)
                clean_nama = data.get("nama_dokter", "dokter").replace(" ", "_")
                filename = f"{clean_nama}_{file_data.filename}"
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(await file_data.read())
                data["foto"] = f"/static/uploads/dokter/{filename}"
            else:
                if not is_created:
                    data.pop("foto", None)
                else:
                    data["foto"] = None

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") in ["partner"]


# =========================================================
# AUTHENTICATION BACKEND
# =========================================================

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email_input = form.get("username")
        password_input = form.get("password")

        if not email_input or not password_input:
            return False

        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            # Check users table (admin)
            result = await session.execute(select(User).where(User.email == email_input))
            user_data = result.scalar_one_or_none()

            if user_data and verify_password(password_input, user_data.password):
                if user_data.role == RoleUser.ADMIN:
                    request.session.update({"user_role": "admin", "user_id": user_data.id_user})
                    return True

            # Check partners table
            result = await session.execute(
                select(Partner).where(Partner.email == email_input, Partner.email.is_not(None))
            )
            partner_data = result.scalar_one_or_none()

            if partner_data and verify_password(password_input, partner_data.password):
                request.session.update({"user_role": "partner", "partner_id": partner_data.id_partner})
                return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("user_role") is not None


# =========================================================
# STANDALONE FASTAPI APP (port 8002)
# =========================================================

admin_app = FastAPI(
    title="PetCare Admin Dashboard",
    version="1.0.0",
)

# SessionMiddleware on this standalone app
admin_app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY_GOOGLE,
    session_cookie="admin_session",
    same_site="lax",
)

auth_backend = AdminAuth(secret_key=settings.SECRET_KEY_GOOGLE)

admin = Admin(
    app=admin_app,
    engine=engine,
    title="PetCare Dashboard",
    base_url="/admin",
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

# Health check
@admin_app.get("/health")
async def health():
    return {"status": "ok", "service": "admin"}
