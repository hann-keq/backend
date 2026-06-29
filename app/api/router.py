from fastapi import APIRouter, Depends, HTTPException, status, Request, Form,UploadFile,File
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.core.templates import templates
from app.core.database import get_db
from app.core.security import create_access_token
from app.core.auth import get_current_user
from app.core.config import UPLOAD_ROOT
from app.core.midtrans import snap
import os
import time
from app.models.models import User
from app.schemas.cart_schema.schema import CartSyncRequest
from app.services.pet.pet_service import add_pet
from app.exceptions import system_exceptions
from app.schemas.pet_schema.pet_create import PetCreate
from app.schemas.user_schema.user_create import UserCreate
from app.services.alamat import service as alamat_service
from app.schemas.alamat_schema import schema as alamat_schema

from app.services.user.user_service import create_new_user, login_user
from app.services.favorite import service as favorite_service

from app.schemas.booking_schema.schema import BookingCreate
from app.schemas.janji_schema.schema import JanjiTemuCreate


from app.repositories import (
    alamat_repository,
    booking_repository,
    cart_repository,
    favorit_repository,
    membership_repository,
    order_repository,
    pet_repository,
    produk_repository,
    user_repository,
    janji_temu_repository,
)

from app.schemas.booking_schema.schema import BookingCreate
from app.schemas.janji_schema.schema import JanjiTemuCreate
from app.schemas.membership_schema.schema import MembershipCreate


router = APIRouter()


# ================================================================
#  AUTH
# ================================================================

@router.post("/register", response_class=HTMLResponse)
async def sign_up(
    request: Request,
    nama: str = Form(...),
    email: str = Form(...),
    no_telepon: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        new_user = UserCreate(
            nama=nama,
            email=email,
            no_telepon=no_telepon,
            password=password,
            confirm_password=confirm_password,
        )
        user = await create_new_user(db, new_user)
        if user:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception:
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={
                "request": request,
                "error": "Email already registered",
                "nama": nama,
                "email": email,
                "no_telepon": no_telepon,
            },
            status_code=400,
        )


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    form_data = {"email": email, "password": password}
    user = await login_user(db, form_data)

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Invalid email or password"},
        )

    access_token = create_access_token(data={"sub": str(user.id_user)})
    response = RedirectResponse(url="/petcaredashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


# ================================================================
#  PETS
# ================================================================

@router.post("/pets/add", response_class=HTMLResponse)
async def add_user_new_pet(
    request: Request,
    pet_name: str = Form(...),
    jenis_hewan: str = Form(...),
    umur: int = Form(...),
    berat: int = Form(...),
    gender: str = Form(...),
    foto_hewan: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        file_url = None
        if foto_hewan and foto_hewan.filename:
            upload_dir = os.path.join(UPLOAD_ROOT, "pets")
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, foto_hewan.filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await foto_hewan.read())
            file_url = f"/static/uploads/pets/{foto_hewan.filename}"
        
        pet_data = PetCreate(
            nama_hewan=pet_name,
            jenis_hewan=jenis_hewan,
            umur=umur,
            berat=berat,
            gender_hewan=gender,
            foto=file_url,
        )
        referer = request.headers.get("Referer", "")
        origin_page = "/profile" if "profile" in referer else "/petcaredashboard"
        await add_pet(db, current_user.id_user, pet_data)
        return RedirectResponse(url=origin_page, status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"Error adding pet: {e}")
        system_exceptions.handle_system_error(e)


@router.post("/pets/edit", response_class=HTMLResponse)
async def edit_pet(
    request: Request,
    pet_id: int = Form(...),
    pet_name: str = Form(...),
    jenis_hewan: str = Form(...),
    umur: int = Form(...),
    berat: int = Form(...),
    gender: str = Form(...),
    pet_gambar: UploadFile = File(None),
    existing_foto: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        existing = await pet_repository.get_pet_by_id(db, pet_id)
        if not existing or existing.id_user != current_user.id_user:
            raise HTTPException(status_code=404, detail="Pet not found")

        update_dict = {
            "nama_hewan": pet_name,
            "jenis_hewan": jenis_hewan,
            "umur": umur,
            "berat": berat,
            "gender_hewan": gender,
        }

        if pet_gambar and pet_gambar.filename:
            upload_dir = os.path.join(UPLOAD_ROOT, "pets")
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, pet_gambar.filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await pet_gambar.read())
            update_dict["foto"] = f"/static/uploads/pets/{pet_gambar.filename}"
        elif existing_foto:
            update_dict["foto"] = existing_foto  # keep existing photo

        await pet_repository.update_pet(db, pet_id, update_dict)
        return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


@router.post("/pets/delete", response_class=HTMLResponse)
async def delete_pet(
    request: Request,
    pet_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        existing = await pet_repository.get_pet_by_id(db, pet_id)
        if not existing or existing.id_user != current_user.id_user:
            raise HTTPException(status_code=404, detail="Pet not found")
        await pet_repository.delete_pet(db, pet_id)
        return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


# ================================================================
#  ADDRESS
# ================================================================

@router.post("/address/add", response_class=HTMLResponse)
async def add_user_new_address(
    alamat: str = Form(...),
    kota: str = Form(...),
    provinsi: str = Form(...),
    kode_pos: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        new_alamat = alamat_schema.AlamatCreate(
            alamat=alamat,
            kota=kota,
            provinsi=provinsi,
            kode_pos=kode_pos,
        )
        await alamat_service.create_new_alamat(db, new_alamat, current_user.id_user)
        return RedirectResponse(url="/address.html", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


@router.post("/address/edit", response_class=HTMLResponse)
async def edit_address(
    alamat_id: int = Form(...),
    alamat: str = Form(...),
    kota: str = Form(...),
    provinsi: str = Form(...),
    kode_pos: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        existing = await alamat_repository.get_alamat_by_id(db, alamat_id)
        if not existing or existing.id_user != current_user.id_user:
            raise HTTPException(status_code=404, detail="Address not found")
        await alamat_repository.update_alamat(
            db, alamat_id, {"alamat": alamat, "kota": kota, "provinsi": provinsi, "kode_pos": kode_pos}
        )
        return RedirectResponse(url="/address.html", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


@router.post("/address/delete", response_class=HTMLResponse)
async def delete_address(
    alamat_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        existing = await alamat_repository.get_alamat_by_id(db, alamat_id)
        if not existing or existing.id_user != current_user.id_user:
            raise HTTPException(status_code=404, detail="Address not found")
        await alamat_repository.delete_alamat(db, alamat_id)
        return RedirectResponse(url="/address.html", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


# ================================================================
#  PROFILE
# ================================================================

@router.post("/profile/edit", response_class=HTMLResponse)
async def edit_profile(
    request: Request,
    nama: str = Form(...),
    email: str = Form(...),
    no_telepon: str = Form(...),
    foto: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Check for email conflict
        existing = await user_repository.get_user_by_email(db, email)
        if existing and existing.id_user != current_user.id_user:
            return templates.TemplateResponse(
                request=request,
                name="editprofile.html",
                context={
                    "request": request,
                    "user": current_user,
                    "error": "Email already used by another account",
                },
            )
        
        update_dict = {"nama": nama, "email": email, "no_telepon": no_telepon}
        if foto and foto.filename:
            upload_dir = os.path.join(UPLOAD_ROOT, "user")
            os.makedirs(upload_dir, exist_ok=True)
            filename = f"user_{current_user.id_user}_{foto.filename}"
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await foto.read())
            update_dict["foto"] = f"/static/uploads/user/{filename}"

        await user_repository.update_user(
            db, current_user.id_user, update_dict
        )
        return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


# ================================================================
#  CART — server-backed, per user, NOT localStorage
# ================================================================

@router.post("/cart/add", response_class=HTMLResponse)
async def cart_add(
    request: Request,
    id_produk: int = Form(...),
    jumlah: int = Form(1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart = await cart_repository.get_or_create_cart(db, current_user.id_user)
        await cart_repository.add_item(db, cart.id_cart, id_produk, jumlah)
        return RedirectResponse(url="/petshop.html", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


@router.post("/cart/update", response_class=HTMLResponse)
async def cart_update(
    request: Request,
    id_produk: int = Form(...),
    jumlah: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart = await cart_repository.get_or_create_cart(db, current_user.id_user)
        await cart_repository.update_item_qty(db, cart.id_cart, id_produk, jumlah)
        return RedirectResponse(url="/petshop.html", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


@router.post("/cart/remove")
async def cart_remove(
    request: Request,
    id_produk: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart = await cart_repository.get_or_create_cart(db, current_user.id_user)
        await cart_repository.remove_item(db, cart.id_cart, id_produk)
        return RedirectResponse(url="/petshop.html", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


# ================================================================
#  CART SYNC  (client-side localStorage batch checkout)
# ================================================================

@router.post("/api/cart/sync")
async def cart_sync(
    payload: CartSyncRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Batch checkout from client-side cart (localStorage).

    Accepts a JSON array of {id_produk, jumlah}, validates stock,
    creates order_produk + detail_order rows in one transaction,
    clears the server-side cart, and generates a Midtrans Snap token
    so the client can open the Snap popup directly.
    """
    if not payload.items:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "message": "Cart is empty."},
        )

    cart = await cart_repository.get_or_create_cart(db, current_user.id_user)

    # ---------- validate stock & compute totals ----------
    total_harga = 0.0
    detail_rows: list[tuple[int, int, float]] = []  # (id_produk, jumlah, subtotal)

    for item in payload.items:
        produk = await produk_repository.get_product_by_id(db, item.id_produk)
        if not produk:
            return JSONResponse(
                status_code=404,
                content={"ok": False, "message": f"Product {item.id_produk} not found."},
            )
        if produk.stok is None or produk.stok < item.jumlah:
            return JSONResponse(
                status_code=409,
                content={
                    "ok": False,
                    "message": (
                        f"Insufficient stock for '{produk.nama_produk}'."
                        f" Available: {produk.stok or 0}, requested: {item.jumlah}."
                    ),
                },
            )
        subtotal = produk.harga * item.jumlah
        total_harga += subtotal
        detail_rows.append((item.id_produk, item.jumlah, subtotal))

    # ---------- create order + detail_order in DB ----------
    midtrans_order_id = f"PetCare-Shop-{int(time.time())}-{current_user.id_user}"

    new_order = await order_repository.create_order_produk(
        db,
        {
            "id_user": current_user.id_user,
            "total_harga": total_harga,
            "status_order": "Menunggu",
            "midtrans_order_id": midtrans_order_id,
        },
    )

    for id_produk, jumlah, subtotal in detail_rows:
        await order_repository.create_detail_order(
            db,
            {
                "id_order_produk": new_order.id_order_produk,
                "id_produk": id_produk,
                "jumlah": jumlah,
                "subtotal": subtotal,
            },
        )
        await produk_repository.reduce_stock_product_by_id_product(db, id_produk, jumlah)

    # ---------- create pembayaran record with status Menunggu ----------
    from app.models.models import Pembayaran
    pembayaran = Pembayaran(
        id_user=current_user.id_user,
        id_order_produk=new_order.id_order_produk,
        jumlah_bayar=total_harga,
        metode_pembayaran="QRIS",
        status_pembayaran="Menunggu",
        midtrans_order_id=midtrans_order_id,
    )
    db.add(pembayaran)
    await db.commit()

    # ---------- clear server-side cart ----------
    await cart_repository.clear_cart(db, cart.id_cart)

    # ---------- generate Midtrans Snap token ----------
    total_real = int(total_harga)
    transaction_params = {
        "transaction_details": {
            "order_id": midtrans_order_id,
            "gross_amount": total_real,
        },
        "credit_card": {"secure": True},
        "enabled_payments": ["qris", "gopay", "bank_transfer"],
    }
    snap_token = None
    try:
        transaction = snap.create_transaction(transaction_params)
        snap_token = transaction["token"]
    except Exception as e:
        print(f"Midtrans token error: {e}")

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "order_id": new_order.id_order_produk,
            "total": total_harga,
            "snap_token": snap_token,
        },
    )


# ================================================================
#  FAVORITES
# ================================================================


# ================================================================
#  FAVORITES
# ================================================================

@router.post("/favorites/toggle", response_class=HTMLResponse)
async def toggle_favorite(
    request: Request,
    id_produk: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await favorite_service.toggle_favorit(db, current_user.id_user, id_produk)
        referer = request.headers.get("Referer", "/favorites.html")
        return RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


# ================================================================
#  ORDERS  (checkout from petshop cart)
# ================================================================

@router.post("/orders/create", response_class=HTMLResponse)
async def create_order(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Checkout: reads cart_items from DB, creates order_produk + detail_order, then clears cart."""
    import json

    try:
        cart = await cart_repository.get_or_create_cart(db, current_user.id_user)
        cart_items = await cart_repository.get_cart_items(db, cart.id_cart)

        if not cart_items:
            return RedirectResponse(url="/petshop.html", status_code=status.HTTP_303_SEE_OTHER)

        total_harga = 0.0
        detail_data = []

        for ci in cart_items:
            produk = await produk_repository.get_product_by_id(db, ci.id_produk)
            if not produk or produk.stok < ci.jumlah:
                continue  # skip unavailable products
            subtotal = produk.harga * ci.jumlah
            total_harga += subtotal
            detail_data.append((ci.id_produk, ci.jumlah, subtotal))

        if not detail_data:
            return RedirectResponse(url="/petshop.html", status_code=status.HTTP_303_SEE_OTHER)

        new_order = await order_repository.create_order_produk(
            db,
            {
                "id_user": current_user.id_user,
                "total_harga": total_harga,
                "status_order": "Menunggu",
            },
        )

        for id_produk, jumlah, subtotal in detail_data:
            await order_repository.create_detail_order(
                db,
                {
                    "id_order_produk": new_order.id_order_produk,
                    "id_produk": id_produk,
                    "jumlah": jumlah,
                    "subtotal": subtotal,
                },
            )
            await produk_repository.reduce_stock_product_by_id_product(db, id_produk, jumlah)

        # Clear the cart after successful order
        await cart_repository.clear_cart(db, cart.id_cart)

        return RedirectResponse(url="/orders.html", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


# ================================================================
#  BOOKING GROOMING
# ================================================================

@router.post("/bookings/create", response_class=HTMLResponse)
async def create_booking(
    id_pet: int = Form(...),
    id_paket_grooming: int = Form(...),
    tanggal_booking: str = Form(...),
    jam_booking: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        from datetime import date, time

        booking_data = BookingCreate(
            id_pet=id_pet,
            id_paket_grooming=id_paket_grooming,
            tanggal_booking=date.fromisoformat(tanggal_booking),
            jam_booking=time.fromisoformat(jam_booking),
        )
        booking_dict = booking_data.model_dump()
        booking_dict["id_user"] = current_user.id_user
        booking_dict["status_booking"] = "Menunggu"
        await booking_repository.create_booking_grooming(db, booking_dict)

        return RedirectResponse(url="/booking.html", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


@router.post("/bookings/cancel", response_class=HTMLResponse)
async def cancel_booking(
    booking_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        existing = await booking_repository.get_booking_grooming_by_id(db, booking_id)
        if not existing or existing.id_user != current_user.id_user:
            raise HTTPException(status_code=404, detail="Booking not found")
        await booking_repository.update_booking_grooming(db, booking_id, "Dibatalkan")
        return RedirectResponse(url="/booking.html", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


# ================================================================
#  JANJI TEMU  (vet appointments)
# ================================================================

@router.post("/janji-temu/create", response_class=HTMLResponse)
async def create_janji_temu(
    id_pet: int = Form(...),
    id_dokter: int = Form(...),
    tanggal_janji: str = Form(...),
    jam_janji: str = Form(...),
    keluhan: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        from datetime import date, time

        janji_data = JanjiTemuCreate(
            id_pet=id_pet,
            id_dokter=id_dokter,
            tanggal_janji=date.fromisoformat(tanggal_janji),
            jam_janji=time.fromisoformat(jam_janji),
            keluhan=keluhan,
        )
        janji_dict = janji_data.model_dump()
        janji_dict["id_user"] = current_user.id_user
        janji_dict["status_janji"] = "Menunggu"
        await janji_temu_repository.create_janji_temu(db, janji_dict)

        return RedirectResponse(url="/booking.html", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


@router.post("/janji-temu/cancel", response_class=HTMLResponse)
async def cancel_janji_temu(
    janji_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        existing = await janji_temu_repository.get_janji_temu_by_id(db, janji_id)
        if not existing or existing.id_user != current_user.id_user:
            raise HTTPException(status_code=404, detail="Janji Temu not found")
        await janji_temu_repository.update_status_janji_temu(db, janji_id, "Dibatalkan")
        return RedirectResponse(url="/booking.html", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


# ================================================================
#  MEMBERSHIP
# ================================================================

@router.post("/membership/select", response_class=HTMLResponse)
async def select_membership(
    tipe_membership: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        from datetime import date, timedelta

        today = date.today()
        existing = await membership_repository.get_membership_by_user(db, current_user.id_user)
        if existing:
            # update existing
            await membership_repository.update_membership_dates(
                db,
                existing.id_membership,
                {
                    "tipe_membership": tipe_membership,
                    "tanggal_berlaku": today,
                    "tanggal_kedaluarsa": today + timedelta(days=30),
                },
            )
        else:
            await membership_repository.create_membership(
                db,
                {
                    "id_user": current_user.id_user,
                    "tipe_membership": tipe_membership,
                    "tanggal_berlaku": today,
                    "tanggal_kedaluarsa": today + timedelta(days=30),
                },
            )
        return RedirectResponse(url="/membership.html", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


@router.post("/membership/cancel", response_class=HTMLResponse)
async def cancel_membership(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        existing = await membership_repository.get_membership_by_user(db, current_user.id_user)
        if existing:
            # downgrade to Basic
            await membership_repository.update_membership_dates(
                db,
                existing.id_membership,
                {"tipe_membership": "Basic"},
            )
        return RedirectResponse(url="/membership.html", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        system_exceptions.handle_system_error(e)


# ================================================================
#  PRODUCT  (admin-facing, kept for completeness)
# ================================================================

# No trailing imports needed

@router.post("/checkout", response_class=HTMLResponse)
async def checkout(
    metode_pembayaran: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.models.models import Pembayaran

        cart = await cart_repository.get_or_create_cart(db, current_user.id_user)
        cart_items = await cart_repository.get_cart_items(db, cart.id_cart)

        if not cart_items:
            return RedirectResponse(url="/petshop.html", status_code=status.HTTP_303_SEE_OTHER)

        total_harga = 0.0
        detail_data = []

        for ci in cart_items:
            p = await produk_repository.get_product_by_id(db, ci.id_produk)
            if p and p.stok >= ci.jumlah:
                subtotal = p.harga * ci.jumlah
                total_harga += subtotal
                detail_data.append((ci.id_produk, ci.jumlah, subtotal))

        if not detail_data:
            return RedirectResponse(url="/petshop.html", status_code=status.HTTP_303_SEE_OTHER)

        total_harga += 2.00  # shipping

        new_order = await order_repository.create_order_produk(db, {
            'id_user': current_user.id_user,
            'total_harga': total_harga,
            'status_order': 'Menunggu',
        })

        for id_produk, jumlah, subtotal in detail_data:
            await order_repository.create_detail_order(db, {
                'id_order_produk': new_order.id_order_produk,
                'id_produk': id_produk,
                'jumlah': jumlah,
                'subtotal': subtotal,
            })
            await produk_repository.reduce_stock_product_by_id_product(db, id_produk, jumlah)

        pembayaran = Pembayaran(
            id_user=current_user.id_user,
            id_order_produk=new_order.id_order_produk,
            jumlah_bayar=total_harga,
            metode_pembayaran=metode_pembayaran,
            status_pembayaran='Dibayar',
        )
        db.add(pembayaran)
        await db.commit()

        await cart_repository.clear_cart(db, cart.id_cart)

        return RedirectResponse(url="/choosepayment.html", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        system_exceptions.handle_system_error(e)



