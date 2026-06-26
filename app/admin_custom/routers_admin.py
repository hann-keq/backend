"""Admin-side routes — accessible only to session role 'admin'.

Covers:
  - UserAdmin          GET/POST /users         CRUD + foto + hash password
  - PartnerAdmin       GET/POST /partners      CRUD + hash password
  - PetAdmin           GET        /pets        read-only list
  - ProductAdmin       GET/POST /products      CRUD + foto + soft-delete
  - PembayaranProduk   GET/POST /pembayaran/produk     list + mark Dibayar
  - PembayaranGrooming GET/POST /pembayaran/grooming   list + mark Dibayar/Menunggu
  - PembayaranJanji    GET/POST /pembayaran/janji-temu list + mark Dibayar
"""

import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.core.security import hash_password
from app.core.templates import templates
from app.core.config import UPLOAD_ROOT
from app.models.models import (
    User,
    Partner,
    Pet,
    Produk,
    Pembayaran,
    BookingGrooming,
    JanjiTemu,
    OrderProduk,
)
from app.admin_custom.deps import require_admin

router = APIRouter(prefix="/dashboard-admin", tags=["admin_custom_admin"])

# Template helper
_T = "admin_custom"


# ---------------------------------------------------------------------------
#                                USERS
# ---------------------------------------------------------------------------

@router.get("/users", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def user_list(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.id_user.desc()))
    users = result.scalars().all()
    return templates.TemplateResponse(request, f"{_T}/users_list.html", {"request": request, "users": users})


@router.get("/users/create", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def user_create_form(request: Request):
    return templates.TemplateResponse(request, f"{_T}/users_form.html", {"request": request, "is_edit": False, "user_data": {}})


@router.post("/users/create", dependencies=[Depends(require_admin)])
async def user_create(request: Request, db: AsyncSession = Depends(get_db)):
    form = await request.form()
    nama = str(form.get("nama", "")).strip()
    email = str(form.get("email", "")).strip()
    no_telepon = str(form.get("no_telepon", "")).strip()
    password = str(form.get("password", "")).strip()
    role = str(form.get("role", "User")).strip()
    foto_file = form.get("foto")

    errors: list[str] = []
    if not nama: errors.append("Nama wajib diisi.")
    if not email: errors.append("Email wajib diisi.")
    if not password: errors.append("Password wajib diisi.")

    if errors:
        return templates.TemplateResponse(request, f"{_T}/users_form.html", {
            "request": request, "is_edit": False, "user_data": {},
            "form_errors": errors,
            "old_nama": nama, "old_email": email, "old_no": no_telepon, "old_role": role,
        }, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    foto_path = None
    if foto_file and hasattr(foto_file, 'filename') and foto_file.filename:
        upload_dir = os.path.join(UPLOAD_ROOT, "user")
        os.makedirs(upload_dir, exist_ok=True)
        clean = nama.replace(" ", "_")
        filename = f"{clean}_{foto_file.filename}"
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as buf:
            buf.write(await foto_file.read())
        foto_path = f"/static/uploads/user/{filename}"

    user = User(
        nama=nama, email=email, no_telepon=no_telepon,
        password=hash_password(password), role=role,
        foto=foto_path,
    )
    db.add(user)
    await db.commit()
    return RedirectResponse(url="/dashboard-admin/users", status_code=303)


@router.get("/users/edit/{user_id}", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def user_edit_form(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id_user == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return templates.TemplateResponse(request, f"{_T}/users_form.html", {"request": request, "is_edit": True, "user_data": user})


@router.post("/users/edit/{user_id}", dependencies=[Depends(require_admin)])
async def user_edit(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id_user == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    form = await request.form()
    user.nama = str(form.get("nama", user.nama)).strip()
    user.email = str(form.get("email", user.email)).strip()
    user.no_telepon = str(form.get("no_telepon", user.no_telepon)).strip()
    user.role = str(form.get("role", user.role.value if hasattr(user.role, 'value') else user.role)).strip()

    new_password = str(form.get("password", "")).strip()
    if new_password:
        user.password = hash_password(new_password)

    foto_file = form.get("foto")
    if foto_file and hasattr(foto_file, 'filename') and foto_file.filename:
        upload_dir = os.path.join(UPLOAD_ROOT, "user")
        os.makedirs(upload_dir, exist_ok=True)
        clean = user.nama.replace(" ", "_")
        filename = f"{clean}_{foto_file.filename}"
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as buf:
            buf.write(await foto_file.read())
        user.foto = f"/static/uploads/user/{filename}"

    await db.commit()
    return RedirectResponse(url="/dashboard-admin/users", status_code=303)


@router.post("/users/delete/{user_id}", dependencies=[Depends(require_admin)])
async def user_delete(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id_user == user_id))
    user = result.scalar_one_or_none()
    if user:
        await db.delete(user)
        await db.commit()
    return RedirectResponse(url="/dashboard-admin/users", status_code=303)


# ---------------------------------------------------------------------------
#                              PARTNERS
# ---------------------------------------------------------------------------

@router.get("/partners", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def partner_list(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Partner).order_by(Partner.id_partner.desc()))
    partners = result.scalars().all()
    return templates.TemplateResponse(request, f"{_T}/partners_list.html", {"request": request, "partners": partners})


@router.get("/partners/create", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def partner_create_form(request: Request):
    return templates.TemplateResponse(request, f"{_T}/partners_form.html", {"request": request, "is_edit": False, "partner_data": {}})


@router.post("/partners/create", dependencies=[Depends(require_admin)])
async def partner_create(request: Request, db: AsyncSession = Depends(get_db)):
    form = await request.form()
    nama = str(form.get("nama_partner", "")).strip()
    jenis = str(form.get("jenis_partner", "All")).strip()
    alamat = str(form.get("alamat", "")).strip()
    no_telepon = str(form.get("no_telepon", "")).strip()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", "")).strip()

    errors: list[str] = []
    if not nama: errors.append("Nama partner wajib diisi.")
    if not email: errors.append("Email wajib diisi.")
    if not password: errors.append("Password wajib diisi.")

    if errors:
        return templates.TemplateResponse(request, f"{_T}/partners_form.html", {
            "request": request, "is_edit": False, "partner_data": {},
            "form_errors": errors,
            "old_nama": nama, "old_jenis": jenis, "old_alamat": alamat,
            "old_telp": no_telepon, "old_email": email,
        }, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    partner = Partner(
        nama_partner=nama, jenis_partner=jenis, alamat=alamat,
        no_telepon=no_telepon, email=email or None,
        password=hash_password(password),
    )
    db.add(partner)
    await db.commit()
    return RedirectResponse(url="/dashboard-admin/partners", status_code=303)


@router.get("/partners/edit/{partner_id}", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def partner_edit_form(partner_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Partner).where(Partner.id_partner == partner_id))
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found.")
    return templates.TemplateResponse(request, f"{_T}/partners_form.html", {"request": request, "is_edit": True, "partner_data": partner})


@router.post("/partners/edit/{partner_id}", dependencies=[Depends(require_admin)])
async def partner_edit(partner_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Partner).where(Partner.id_partner == partner_id))
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found.")

    form = await request.form()
    partner.nama_partner = str(form.get("nama_partner", partner.nama_partner)).strip()
    partner.jenis_partner = str(form.get("jenis_partner", partner.jenis_partner.value if hasattr(partner.jenis_partner, 'value') else partner.jenis_partner)).strip()
    partner.alamat = str(form.get("alamat", partner.alamat)).strip()
    partner.no_telepon = str(form.get("no_telepon", partner.no_telepon)).strip()
    partner.email = str(form.get("email", partner.email or "")).strip() or None

    new_password = str(form.get("password", "")).strip()
    if new_password:
        partner.password = hash_password(new_password)

    await db.commit()
    return RedirectResponse(url="/dashboard-admin/partners", status_code=303)


@router.post("/partners/delete/{partner_id}", dependencies=[Depends(require_admin)])
async def partner_delete(partner_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Partner).where(Partner.id_partner == partner_id))
    partner = result.scalar_one_or_none()
    if partner:
        await db.delete(partner)
        await db.commit()
    return RedirectResponse(url="/dashboard-admin/partners", status_code=303)


# ---------------------------------------------------------------------------
#                               PETS
# ---------------------------------------------------------------------------

@router.get("/pets", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def pet_list(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Pet).order_by(Pet.id_pet.desc()))
    pets = result.scalars().all()
    return templates.TemplateResponse(request, f"{_T}/pets_list.html", {"request": request, "pets": pets})


# ---------------------------------------------------------------------------
#                              PRODUK
# ---------------------------------------------------------------------------

@router.get("/products", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def product_list(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Produk).where(Produk.status_produk != "DIHAPUS").order_by(Produk.id_produk.desc())
    )
    products = result.scalars().all()
    return templates.TemplateResponse(request, f"{_T}/products_list.html", {"request": request, "products": products})


@router.get("/products/create", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def product_create_form(request: Request):
    return templates.TemplateResponse(request, f"{_T}/products_form.html", {"request": request, "is_edit": False, "product_data": {}})


@router.post("/products/create", dependencies=[Depends(require_admin)])
async def product_create(request: Request, db: AsyncSession = Depends(get_db)):
    form = await request.form()
    nama = str(form.get("nama_produk", "")).strip()
    harga_raw = str(form.get("harga", "0")).strip()
    stok_raw = str(form.get("stok", "0")).strip()
    tipe = str(form.get("tipe_produk", "Makanan")).strip()
    gambar_file = form.get("gambar")

    errors: list[str] = []
    if not nama: errors.append("Nama produk wajib diisi.")
    try:
        harga = float(harga_raw)
    except ValueError:
        errors.append("Harga harus angka.")
        harga = 0
    try:
        stok = int(stok_raw)
    except ValueError:
        errors.append("Stok harus angka.")
        stok = 0

    if errors:
        return templates.TemplateResponse(request, f"{_T}/products_form.html", {
            "request": request, "is_edit": False, "product_data": {},
            "form_errors": errors,
            "old_nama": nama, "old_harga": harga_raw, "old_stok": stok_raw, "old_tipe": tipe,
        }, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    gambar_path = None
    if gambar_file and hasattr(gambar_file, 'filename') and gambar_file.filename:
        upload_dir = os.path.join(UPLOAD_ROOT, "produk")
        os.makedirs(upload_dir, exist_ok=True)
        clean = nama.replace(" ", "_")
        filename = f"{clean}_{gambar_file.filename}"
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as buf:
            buf.write(await gambar_file.read())
        gambar_path = f"/static/uploads/produk/{filename}"

    produk = Produk(
        nama_produk=nama, harga=harga, stok=stok, tipe_produk=tipe,
        gambar=gambar_path, status_produk="Tersedia",
    )
    db.add(produk)
    await db.commit()
    return RedirectResponse(url="/dashboard-admin/products", status_code=303)


@router.get("/products/edit/{product_id}", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def product_edit_form(product_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Produk).where(Produk.id_produk == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    return templates.TemplateResponse(request, f"{_T}/products_form.html", {"request": request, "is_edit": True, "product_data": product})


@router.post("/products/edit/{product_id}", dependencies=[Depends(require_admin)])
async def product_edit(product_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Produk).where(Produk.id_produk == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    form = await request.form()
    product.nama_produk = str(form.get("nama_produk", product.nama_produk)).strip()
    try:
        product.harga = float(str(form.get("harga", product.harga)).strip())
    except ValueError:
        pass
    try:
        product.stok = int(str(form.get("stok", product.stok)).strip())
    except ValueError:
        pass
    product.tipe_produk = str(form.get("tipe_produk", product.tipe_produk.value if hasattr(product.tipe_produk, 'value') else product.tipe_produk)).strip()

    gambar_file = form.get("gambar")
    if gambar_file and hasattr(gambar_file, 'filename') and gambar_file.filename:
        upload_dir = os.path.join(UPLOAD_ROOT, "produk")
        os.makedirs(upload_dir, exist_ok=True)
        clean = product.nama_produk.replace(" ", "_")
        filename = f"{clean}_{gambar_file.filename}"
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as buf:
            buf.write(await gambar_file.read())
        product.gambar = f"/static/uploads/produk/{filename}"

    await db.commit()
    return RedirectResponse(url="/dashboard-admin/products", status_code=303)


@router.post("/products/soft-delete/{product_id}", dependencies=[Depends(require_admin)])
async def product_soft_delete(product_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Produk).where(Produk.id_produk == product_id))
    product = result.scalar_one_or_none()
    if product:
        product.status_produk = "DIHAPUS"
        await db.commit()
    return RedirectResponse(url="/dashboard-admin/products", status_code=303)


@router.post("/products/restore/{product_id}", dependencies=[Depends(require_admin)])
async def product_restore(product_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Produk).where(Produk.id_produk == product_id))
    product = result.scalar_one_or_none()
    if product:
        product.status_produk = "TERSEDIA"
        await db.commit()
    return RedirectResponse(url="/dashboard-admin/products", status_code=303)


# ---------------------------------------------------------------------------
#                         PEMBAYARAN PRODUK
# ---------------------------------------------------------------------------

@router.get("/pembayaran/produk", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def pembayaran_produk_list(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Pembayaran)
        .options(joinedload(Pembayaran.user))
        .where(Pembayaran.id_order_produk.isnot(None))
        .order_by(Pembayaran.id_pembayaran.desc())
    )
    payments = result.scalars().all()
    return templates.TemplateResponse(request, f"{_T}/pembayaran_produk_list.html", {"request": request, "payments": payments})


@router.post("/pembayaran/produk/mark-dibayar/{pembayaran_id}", dependencies=[Depends(require_admin)])
async def pembayaran_produk_mark(pembayaran_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Pembayaran).where(
            Pembayaran.id_pembayaran == pembayaran_id,
            Pembayaran.id_order_produk.isnot(None),
        )
    )
    p = result.scalar_one_or_none()
    if p:
        p.status_pembayaran = "DIBAYAR"
        await db.commit()
    return RedirectResponse(url="/dashboard-admin/pembayaran/produk", status_code=303)


# ---------------------------------------------------------------------------
#                         PEMBAYARAN GROOMING
# ---------------------------------------------------------------------------

@router.get("/pembayaran/grooming", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def pembayaran_grooming_list(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Pembayaran)
        .options(joinedload(Pembayaran.user))
        .where(Pembayaran.id_booking_grooming.isnot(None))
        .order_by(Pembayaran.id_pembayaran.desc())
    )
    payments = result.scalars().all()
    return templates.TemplateResponse(request, f"{_T}/pembayaran_grooming_list.html", {"request": request, "payments": payments})


@router.post("/pembayaran/grooming/mark-dibayar/{pembayaran_id}", dependencies=[Depends(require_admin)])
async def pembayaran_grooming_mark_dibayar(pembayaran_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Pembayaran).where(
            Pembayaran.id_pembayaran == pembayaran_id,
            Pembayaran.id_booking_grooming.isnot(None),
        )
    )
    p = result.scalar_one_or_none()
    if p:
        p.status_pembayaran = "DIBAYAR"
        await db.commit()
    return RedirectResponse(url="/dashboard-admin/pembayaran/grooming", status_code=303)


@router.post("/pembayaran/grooming/mark-menunggu/{pembayaran_id}", dependencies=[Depends(require_admin)])
async def pembayaran_grooming_mark_menunggu(pembayaran_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Pembayaran).where(
            Pembayaran.id_pembayaran == pembayaran_id,
            Pembayaran.id_booking_grooming.isnot(None),
        )
    )
    p = result.scalar_one_or_none()
    if p:
        p.status_pembayaran = "MENUNGGU"
        await db.commit()
    return RedirectResponse(url="/dashboard-admin/pembayaran/grooming", status_code=303)


# ---------------------------------------------------------------------------
#                         PEMBAYARAN JANJI TEMU
# ---------------------------------------------------------------------------

@router.get("/pembayaran/janji-temu", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def pembayaran_janji_temu_list(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Pembayaran)
        .options(joinedload(Pembayaran.user))
        .where(Pembayaran.id_janji_temu.isnot(None))
        .order_by(Pembayaran.id_pembayaran.desc())
    )
    payments = result.scalars().all()
    return templates.TemplateResponse(request, f"{_T}/pembayaran_janji_list.html", {"request": request, "payments": payments})


@router.post("/pembayaran/janji-temu/mark-dibayar/{pembayaran_id}", dependencies=[Depends(require_admin)])
async def pembayaran_janji_mark(pembayaran_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Pembayaran).where(
            Pembayaran.id_pembayaran == pembayaran_id,
            Pembayaran.id_janji_temu.isnot(None),
        )
    )
    p = result.scalar_one_or_none()
    if p:
        p.status_pembayaran = "DIBAYAR"
        await db.commit()
    return RedirectResponse(url="/dashboard-admin/pembayaran/janji-temu", status_code=303)
