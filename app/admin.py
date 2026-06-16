from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import Admin, ModelView,action
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import engine
from app.models.models import Pembayaran, Pet, JanjiTemu, User, Partner, RoleUser,Produk
# --- SUDAH DISESUAIKAN DENGAN NAMA FUNGSI ASLI KAMU ---
from app.core.security import hash_password, verify_password  

# =========================================================
# 1. MANAGEMENT VIEW (UNTUK ADMIN UTAMA)
# =========================================================
# 1. BUAT PROXY/SUBCLASS DARI MODEL ASLI
# Ini trik agar SQLAdmin menganggapnya sebagai 3 model yang berbeda
class PembayaranProdukModel(Pembayaran):
    pass

class PembayaranGroomingModel(Pembayaran):
    pass

class PembayaranJanjiTemuModel(Pembayaran):
    pass


# 2. SEKARANG DAFTARKAN KELAS BARU INI KE MODELVIEW MASING-MASING
# --- SUB-MENU 1: PEMBAYARAN PRODUK ---
# --- SUB-MENU 1: PEMBAYARAN PRODUK ---
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
        PembayaranProdukModel.created_at
    ]

    # Menggunakan kueri select formal SQLAlchemy agar filter asinkron berjalan sempurna
    def list_query(self, request: Request):
        print("Mendapatkan query untuk Pembayaran Produk")
        return select(PembayaranProdukModel).where(
            PembayaranProdukModel.id_order_produk.isnot(None)
        )

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"


# --- SUB-MENU 2: PEMBAYARAN GROOMING ---
class PembayaranGroomingAdmin(ModelView, model=PembayaranGroomingModel):
    name = "Pembayaran Grooming"
    name_plural = "Pembayaran Grooming"
    icon = "fa-solid fa-dog"
    category = "Daftar Pembayaran"
    category_icon = "fa-solid fa-bars"

    column_list = [
        PembayaranGroomingModel.id_pembayaran,
        PembayaranGroomingModel.id_user,
        PembayaranGroomingModel.id_booking_grooming,
        PembayaranGroomingModel.jumlah_bayar,
        PembayaranGroomingModel.metode_pembayaran,
        PembayaranGroomingModel.status_pembayaran,
        PembayaranGroomingModel.created_at
    ]

    def list_query(self,request: Request):
        print("Mendapatkan query untuk Pembayaran Grooming")
        return select(PembayaranGroomingModel).where(
            PembayaranGroomingModel.id_booking_grooming.isnot(None)
        )

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"


# --- SUB-MENU 3: PEMBAYARAN JANJI TEMU ---
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
        PembayaranJanjiTemuModel.created_at
    ]

    def list_query(self, request: Request):
        print("Mendapatkan query untuk Pembayaran Janji Temu")
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

        referer = request.headers.get("referer", "/admin/pembayaran-janji-temu-model/list")
        return RedirectResponse(referer, status_code=303)

class UserAdmin(ModelView, model=User):
    name = "Data User/Admin"
    name_plural = "Kelola User & Admin"
    icon = "fa-solid fa-users"
    column_list = [User.id_user, User.nama, User.email, User.role]
    form_columns = ["nama", "email", "no_telepon", "password", "role"]

    # Otomatis hash password saat Admin bikin/edit akun baru dari dashboard
    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        if "password" in data and data["password"]:
            data["password"] = hash_password(data["password"]) # <-- Pakai hash_password

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
# =========================================================
# 2. VIEW DASHBOARD KHUSUS PARTNER (HANYA JANJI TEMU)
# =========================================================
class JanjiTemuAdmin(ModelView, model=JanjiTemu):
    name = "Data Janji Temu"
    name_plural = "Janji Temu"
    icon = "fa-solid fa-calendar"
    column_list = [JanjiTemu.id_user, JanjiTemu.jam_janji, JanjiTemu.tanggal_janji, JanjiTemu.status_janji]

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") in ["partner"]


# =========================================================
# 3. SISTEM LOGIN DASHBOARD (VERIFIKASI BCYRP)
# =========================================================
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email_input = form.get("username")  # Mengambil input dari box 'Username'
        password_input = form.get("password")

        if not email_input or not password_input:
            return False

        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # --- JALUR 1: CEK DATA DI TABEL USERS (UNTUK ADMIN) ---
            user_query = await session.execute(select(User).where(User.email == email_input))
            user_data = user_query.scalar_one_or_none()

            # Memanggil fungsi verify_password buatanmu sendiri
            if user_data and verify_password(password_input, user_data.password):
                if user_data.role == RoleUser.ADMIN:  
                    request.session.update({"user_role": "admin", "user_id": user_data.id_user})
                    return True

            # --- JALUR 2: CEK DATA DI TABEL PARTNERS (UNTUK PARTNER) ---
            partner_query = await session.execute(
                select(Partner).where(Partner.email == email_input, Partner.email.is_not(None))
            )
            partner_data = partner_query.scalar_one_or_none()

            if partner_data and verify_password(password_input, partner_data.password):
                request.session.update({"user_role": "partner", "partner_id": partner_data.id_partner})
                return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("user_role") is not None


authentication_backend = AdminAuth(secret_key="rahasia_tugas_kuliah_sem4")

def init_admin(app):
    admin = Admin(
        app=app, 
        engine=engine, 
        
        title="PetCare Dashboard", 
        
        base_url="/admin", 
        authentication_backend=authentication_backend
    )
    admin.add_view(UserAdmin)
    admin.add_view(PartnerAdmin)
    admin.add_view(PetAdmin)
    admin.add_view(JanjiTemuAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(PembayaranProdukAdmin)
    admin.add_view(PembayaranGroomingAdmin)
    admin.add_view(PembayaranJanjiTemuAdmin)