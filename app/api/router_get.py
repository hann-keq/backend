import time

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import HTMLResponse, RedirectResponse
from app.core.templates import templates
from app.core.auth import get_current_user, google_authorize, access_token_oauth
from app.core.database import get_db
from app.core.security import decode_access_token
from app.exceptions import system_exceptions
from app.models.models import User
from app.schemas.user_schema.user_response import UserResponseOnlyId
from app.services.user.user_service import get_user_by_id
from app.core.midtrans import snap
from app.api.router_midtrans import router as midtrans_router

# ---- repository imports (used directly for read queries) ----
from app.repositories import (
    alamat_repository,
    booking_repository,
    cart_repository,
    favorit_repository,
    membership_repository,
    order_repository,
    paket_grooming,
    partner_repository,
    pet_repository,
    produk_repository,
    janji_temu_repository,
    dokter_repository,
)


router = APIRouter()


# ================================================================
#  TEST / UTILITY
# ================================================================

@router.get('/test-decode-token')
async def test_decode_from_input(data: str):
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
                detail=f"User with ID {user_id} not found",
            )
        return user
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# ================================================================
#  PUBLIC / AUTH PAGES (no login required)
# ================================================================

@router.get('/register', response_class=HTMLResponse)
async def tampilin_register(request: Request):
    return templates.TemplateResponse(
        request, 'signup.html', context={"current_page": "signup"}
    )


@router.get('/signup', response_class=HTMLResponse, name='signup')
async def tampilin_signup(request: Request):
    return templates.TemplateResponse(request, 'signup.html')


@router.get('/login', response_class=HTMLResponse, name='login')
async def tampilin_halaman_login(request: Request):
    return templates.TemplateResponse(request, 'login.html')


@router.get('/', response_class=HTMLResponse, name='petcarehome')
async def tampilin_landing(request: Request):
    return templates.TemplateResponse(request, 'petcarehome.html')


@router.get('/demo', response_class=HTMLResponse, name='demo')
async def tampilin_demo(request: Request):
    return templates.TemplateResponse(request, 'demo.html')
# ==========================================================
# auth google
@router.get('/login/google', response_class=HTMLResponse, name='login_google')
async def login_google(request: Request):
    return await google_authorize(request, callback_url='auth_callback')

@router.get('/auth/callback', response_class=HTMLResponse, name='auth_callback')
async def auth_callback(request: Request, db: AsyncSession = Depends(get_db)):
    token = await access_token_oauth(request, db)

    response = RedirectResponse(url="/petcaredashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
    )
    return response

# ================================================================
#  AUTHENTICATED PAGES — with DB queries
# ================================================================

# -----------------------------------------------------------------
# PETCARE DASHBOARD  (was already fetching data but NOT passing it)
# -----------------------------------------------------------------

@router.get('/petcaredashboard', response_class=HTMLResponse, name='petcaredashboard')
async def tampilin_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        uid = current_user.id_user
        all_pet = await pet_repository.get_all_user_pets(db, uid)
        
        all_janji = await janji_temu_repository.get_all_janji_temu_by_user(db, uid)

        # Get Grooming Bookings
        upcoming_groomings = await booking_repository.get_booking_groomings_by_user(db, uid)
        packages = await paket_grooming.get_all_paket_grooming(db)
        paket_map = {p.id_paket_grooming: p.nama_paket_grooming for p in packages}

        # Calculate next appointment for each pet
        from datetime import date, datetime
        today = date.today()
        for pet in (all_pet or []):
            pet_appointments = []
            
            # Grooming bookings
            for bg in (upcoming_groomings or []):
                if bg.id_pet == pet.id_pet and bg.status_booking.value != "Dibatalkan":
                    if bg.tanggal_booking >= today:
                        dt = datetime.combine(bg.tanggal_booking, bg.jam_booking)
                        pkg_name = paket_map.get(bg.id_paket_grooming, "Grooming")
                        pet_appointments.append((dt, f"Grooming ({pkg_name}): {bg.tanggal_booking.strftime('%d %b %Y')} @ {bg.jam_booking.strftime('%I:%M %p')}"))
            
            # Vet bookings (Janji Temu)
            for janji in (all_janji or []):
                if janji.id_pet == pet.id_pet and janji.status_janji.value != "Dibatalkan":
                    if janji.tanggal_janji >= today:
                        dt = datetime.combine(janji.tanggal_janji, janji.jam_janji)
                        pet_appointments.append((dt, f"Vet Visit: {janji.tanggal_janji.strftime('%d %b %Y')} @ {janji.jam_janji.strftime('%I:%M %p')}"))
            
            if pet_appointments:
                pet_appointments.sort(key=lambda x: x[0])
                pet.next_appointment = pet_appointments[0][1]
            else:
                pet.next_appointment = None

        orders = await order_repository.get_all_ordered_produk_by_user(db, current_user.id_user)

        orders_with_items = []
        for o in (orders or []):
            details = await order_repository.get_detail_orders_by_order(db, o.id_order_produk)
            if not details:  # ✅ skip orders with no items
                continue
            items = []
            for d in details:
                p = await produk_repository.get_product_by_id(db, d.id_produk)
                items.append({
                    "nama_produk": p.nama_produk if p else "Unknown",
                    "jumlah": d.jumlah,
                    "subtotal": d.subtotal,
                })
            orders_with_items.append({
                "order": o,
                "items": items,
                "item_count": len(items),
            })

        # Combine all reminders and limit to 5
        from datetime import datetime
        reminders_list = []

        for janji in (all_janji or []):
            if janji.status_janji.value != "Dibatalkan":
                dt = datetime.combine(janji.tanggal_janji, janji.jam_janji) if janji.tanggal_janji and janji.jam_janji else datetime.max
                reminders_list.append({
                    "type": "vet",
                    "title": janji.keluhan,
                    "date": janji.tanggal_janji,
                    "time": janji.jam_janji,
                    "dt": dt,
                })

        for bg in (upcoming_groomings or []):
            if bg.status_booking.value != "Dibatalkan":
                dt = datetime.combine(bg.tanggal_booking, bg.jam_booking) if bg.tanggal_booking and bg.jam_booking else datetime.max
                pkg_name = paket_map.get(bg.id_paket_grooming, "Grooming")
                reminders_list.append({
                    "type": "grooming",
                    "title": f"Grooming: {pkg_name}",
                    "date": bg.tanggal_booking,
                    "time": bg.jam_booking,
                    "dt": dt,
                })

        for entry in orders_with_items:
            o = entry["order"]
            dt = o.created_at if o.created_at else datetime.min
            for item in entry["items"]:
                reminders_list.append({
                    "type": "order",
                    "title": f"{item['nama_produk']} (x{item['jumlah']})",
                    "subtotal": item['subtotal'],
                    "dt": dt,
                })

        # Sort: Future reminders (vet & grooming) ascending (closest first), orders and past reminders descending (newest first)
        now = datetime.now()
        future_reminders = [r for r in reminders_list if r["type"] in ("vet", "grooming") and r["dt"] >= now]
        past_reminders = [r for r in reminders_list if r["type"] == "order" or r["dt"] < now]

        future_reminders.sort(key=lambda x: x["dt"])
        past_reminders.sort(key=lambda x: x["dt"], reverse=True)

        reminders = (future_reminders + past_reminders)[:5]

    except Exception as e:
        system_exceptions.handle_system_error(e)

    return templates.TemplateResponse(
        request,
        'petcaredashboard.html',
        context={
            "current_page": "home",
            "user": current_user,
            "pets": all_pet,
            "reminders": reminders,
            "orders": orders_with_items,
        },
    )


# -----------------------------------------------------------------
# PROFILE
# -----------------------------------------------------------------

@router.get('/profile', response_class=HTMLResponse, name='profile')
async def tampilin_profile(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pets = await pet_repository.get_all_user_pets(db, current_user.id_user)
    membership = await membership_repository.get_membership_by_user(db, current_user.id_user)

    return templates.TemplateResponse(
        request,
        'profile.html',
        context={
            "current_page": "profile",
            "user": current_user,
            "pets": pets,
            "membership": membership,
        },
    )


# -----------------------------------------------------------------
# EDIT PROFILE
# -----------------------------------------------------------------

@router.get('/editprofile', response_class=HTMLResponse, name='editprofile')
async def tampilin_editprofile(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request,
        'editprofile.html',
        context={
            "current_page": "profile",
            "user": current_user,
        },
    )


# -----------------------------------------------------------------
# ADDRESS
# -----------------------------------------------------------------

@router.get('/address.html', response_class=HTMLResponse, name='address')
async def tampilin_address(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alamat_list = await alamat_repository.get_alamats_by_user(db, current_user.id_user)
    return templates.TemplateResponse(
        request,
        'address.html',
        context={
            "current_page": "address",
            "user": current_user,
            "addresses": alamat_list,
        },
    )


# -----------------------------------------------------------------
# PET SHOP  (all products)
# -----------------------------------------------------------------

@router.get('/petshop.html', response_class=HTMLResponse, name='petshop')
async def tampilin_petshop(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    products = await produk_repository.get_all_products_except_deleted(db)
    cart = await cart_repository.get_or_create_cart(db, current_user.id_user)
    cart_items = await cart_repository.get_cart_items(db, cart.id_cart)

    # Build lookup: id_produk -> CartItem
    cart_map = {}
    for ci in cart_items:
        cart_map[ci.id_produk] = ci.jumlah
    
    # Get user's favorites
    favs = await favorit_repository.get_all_user_favorits(db, current_user.id_user)
    favorite_ids = [f.id_produk for f in favs]
    
    return templates.TemplateResponse(
        request,
        'petshop.html',
        context={
            "current_page": "shop",
            "user": current_user,
            "products": products,
            "cart_map": cart_map,  # {id_produk: jumlah}
            "favorite_ids": favorite_ids,
        },
    )


# -----------------------------------------------------------------
# FAVORITES  (user's favorited products)
# -----------------------------------------------------------------

@router.get('/favorites.html', response_class=HTMLResponse, name='favorites')
async def tampilin_favorites(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get user's favorites (Favorit rows) then resolve each product
    favs = await favorit_repository.get_all_user_favorits(db, current_user.id_user)
    fav_products = []
    for f in favs:
        p = await produk_repository.get_product_by_id(db, f.id_produk)
        if p:
            fav_products.append(p)

    return templates.TemplateResponse(
        request,
        'favorites.html',
        context={
            "current_page": "favorites",
            "user": current_user,
            "favorite_products": fav_products,
        },
    )


# -----------------------------------------------------------------
# ORDERS  (user's order history with line items)
# -----------------------------------------------------------------

@router.get('/orders', response_class=HTMLResponse, name='orders')
async def tampilin_orders(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    orders = await order_repository.get_all_ordered_produk_by_user(db, current_user.id_user)

    orders_with_items = []
    for o in (orders or []):
        details = await order_repository.get_detail_orders_by_order(db, o.id_order_produk)
        if not details:  # ✅ skip orders with no items
            continue
        items = []
        for d in details:
            p = await produk_repository.get_product_by_id(db, d.id_produk)
            items.append({
                "nama_produk": p.nama_produk if p else "Unknown",
                "jumlah": d.jumlah,
                "subtotal": d.subtotal,
            })
        orders_with_items.append({
            "order": o,
            "items": items,
            "item_count": len(items),
        })

    return templates.TemplateResponse(
        request,
        'orders.html',
        context={
            "current_page": "orders",
            "user": current_user,
            "orders_with_items": orders_with_items,
        },
    )


# -----------------------------------------------------------------
# BOOKING  (pets, packages, partners, upcoming bookings)
# -----------------------------------------------------------------

@router.get('/booking.html', response_class=HTMLResponse, name='booking')
async def tampilin_booking(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_pets = await pet_repository.get_all_user_pets(db, current_user.id_user)
    packages = await paket_grooming.get_all_paket_grooming(db)
    partners = await partner_repository.get_all_partners(db)
    upcoming_grooming = await booking_repository.get_booking_groomings_by_user(db, current_user.id_user)
    upcoming_vet = await janji_temu_repository.get_all_janji_temu_by_user(db, current_user.id_user)
    dokters = await dokter_repository.get_all_dokters(db)

    paket_map = {p.id_paket_grooming: p for p in packages}
    pet_map = {p.id_pet: p for p in user_pets}
    partner_map = {p.id_partner: p for p in partners}
    dokter_map = {d.id_dokter: d for d in dokters}

    upcoming_with_info = []

    # Add grooming bookings
    for b in (upcoming_grooming or []):
        pet_obj = pet_map.get(b.id_pet)
        paket_obj = paket_map.get(b.id_paket_grooming)
        partner_obj = partner_map.get(paket_obj.id_partner) if paket_obj else None
        
        upcoming_with_info.append({
            "type": "grooming",
            "booking": b,
            "id": b.id_booking_grooming,
            "status": b.status_booking.value,
            "nama_paket": paket_obj.nama_paket_grooming if paket_obj else "Grooming",
            "paket": paket_obj,
            "pet": pet_obj,
            "partner": partner_obj,
            "formatted_date": b.tanggal_booking.strftime("%A, %d %B %Y") if hasattr(b.tanggal_booking, "strftime") else str(b.tanggal_booking),
            "formatted_time": b.jam_booking.strftime("%I:%M %p") if hasattr(b.jam_booking, "strftime") else str(b.jam_booking),
        })

    # Add veterinary bookings
    for j in (upcoming_vet or []):
        pet_obj = pet_map.get(j.id_pet)
        dokter_obj = dokter_map.get(j.id_dokter)
        partner_obj = dokter_obj.partner if dokter_obj else None
        
        upcoming_with_info.append({
            "type": "veterinary",
            "booking": j,
            "id": j.id_janji_temu,
            "status": j.status_janji.value,
            "nama_paket": f"Konsultasi dr. {dokter_obj.nama_dokter}" if dokter_obj else "Veterinary",
            "paket": None,
            "pet": pet_obj,
            "partner": partner_obj,
            "dokter": dokter_obj,
            "formatted_date": j.tanggal_janji.strftime("%A, %d %B %Y") if hasattr(j.tanggal_janji, "strftime") else str(j.tanggal_janji),
            "formatted_time": j.jam_janji.strftime("%I:%M %p") if hasattr(j.jam_janji, "strftime") else str(j.jam_janji),
        })

    return templates.TemplateResponse(
        request,
        'booking.html',
        context={
            "current_page": "booking",
            "user": current_user,
            "pets": user_pets,
            "grooming_packages": packages,
            "partners": partners,
            "upcoming_bookings": upcoming_with_info,
            "dokters": dokters,
        },
    )


# -----------------------------------------------------------------
# APPOINTMENTS
# -----------------------------------------------------------------

@router.get('/appointments.html', response_class=HTMLResponse, name='appointments')
async def tampilin_appointments(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings = await booking_repository.get_booking_groomings_by_user(db, current_user.id_user)
    janji_list = await janji_temu_repository.get_all_janji_temu_by_user(db, current_user.id_user)

    return templates.TemplateResponse(
        request,
        'appointments.html',
        context={
            "current_page": "appointments",
            "user": current_user,
            "bookings": bookings or [],
            "janji_temu": janji_list or [],
        },
    )


# -----------------------------------------------------------------
# MEMBERSHIP
# -----------------------------------------------------------------

@router.get('/membership.html', response_class=HTMLResponse, name='membership')
async def tampilin_membership(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = await membership_repository.get_membership_by_user(db, current_user.id_user)
    return templates.TemplateResponse(
        request,
        'membership.html',
        context={
            "current_page": "membership",
            "user": current_user,
            "membership": membership,
        },
    )


# -----------------------------------------------------------------
# SETTINGS
# -----------------------------------------------------------------

@router.get('/settings', response_class=HTMLResponse, name='settings')
async def tampilin_settings(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request,
        'settings.html',
        context={
            "current_page": "settings",
            "user": current_user,
        },
    )


# -----------------------------------------------------------------
# NEW PET  (form page — no DB query needed)
# -----------------------------------------------------------------

@router.get('/new-pet.html', response_class=HTMLResponse, name='new-pet')
async def tampilin_new_pet(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    
    return templates.TemplateResponse(request,'new-pet.html',context={"user":current_user, "current_page": "new-pet"})



# ================================================================
#  STATIC / SEMI-STATIC PAGES  (no DB queries)
# ================================================================

@router.get('/notification', response_class=HTMLResponse, name='notification')
async def tampilin_notification(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        uid = current_user.id_user
        all_pet = await pet_repository.get_all_user_pets(db, uid)
        pet_map = {p.id_pet: p for p in all_pet}

        all_janji = await janji_temu_repository.get_all_janji_temu_by_user(db, uid)

        upcoming_groomings = await booking_repository.get_booking_groomings_by_user(db, uid)
        packages = await paket_grooming.get_all_paket_grooming(db)
        paket_map = {p.id_paket_grooming: p.nama_paket_grooming for p in packages}

        orders = await order_repository.get_all_ordered_produk_by_user(db, uid)
        orders_with_items = []
        for o in (orders or []):
            details = await order_repository.get_detail_orders_by_order(db, o.id_order_produk)
            if not details:
                continue
            items = []
            for d in details:
                p = await produk_repository.get_product_by_id(db, d.id_produk)
                items.append({
                    "nama_produk": p.nama_produk if p else "Unknown",
                    "jumlah": d.jumlah,
                    "subtotal": d.subtotal,
                })
            orders_with_items.append({
                "order": o,
                "items": items,
            })

        # Combine into notifications list
        notifications = []
        from datetime import datetime

        # 1. Vet appointments
        for janji in (all_janji or []):
            dt = datetime.combine(janji.tanggal_janji, janji.jam_janji) if janji.tanggal_janji and janji.jam_janji else datetime.max
            pet_obj = pet_map.get(janji.id_pet)
            pet_name = pet_obj.nama_hewan if pet_obj else "your pet"
            
            status_val = janji.status_janji.value
            is_unread = status_val == "Menunggu"
            is_urgent = status_val == "Menunggu" and (dt - datetime.now()).days <= 1

            notifications.append({
                "type": "reminder",
                "icon": "💉",
                "title": f"Vet Checkup: {janji.keluhan} for {pet_name}",
                "desc": f"Scheduled for {janji.tanggal_janji} at {janji.jam_janji}. Status: {status_val}",
                "is_unread": is_unread,
                "is_urgent": is_urgent,
                "dt": dt,
            })

        # 2. Grooming bookings
        for bg in (upcoming_groomings or []):
            dt = datetime.combine(bg.tanggal_booking, bg.jam_booking) if bg.tanggal_booking and bg.jam_booking else datetime.max
            pet_obj = pet_map.get(bg.id_pet)
            pet_name = pet_obj.nama_hewan if pet_obj else "your pet"
            pkg_name = paket_map.get(bg.id_paket_grooming, "Grooming")

            status_val = bg.status_booking.value
            is_unread = status_val == "Menunggu"
            is_urgent = status_val == "Menunggu" and (dt - datetime.now()).days <= 1

            notifications.append({
                "type": "reminder",
                "icon": "✂️",
                "title": f"{pet_name}'s grooming: {pkg_name}",
                "desc": f"Scheduled for {bg.tanggal_booking} at {bg.jam_booking}. Status: {status_val}",
                "is_unread": is_unread,
                "is_urgent": is_urgent,
                "dt": dt,
            })

        # 3. Orders / Products bought
        for entry in orders_with_items:
            o = entry["order"]
            dt = o.created_at if o.created_at else datetime.min
            status_val = o.status_order.value
            
            for item in entry["items"]:
                formatted_price = f"Rp {int(item['subtotal']):,}".replace(",", ".")
                notifications.append({
                    "type": "activity",
                    "icon": "📦",
                    "title": f"Purchased {item['nama_produk']} (x{item['jumlah']})",
                    "desc": f"Order #{o.id_order_produk} is {status_val}. Total: {formatted_price}",
                    "is_unread": False,
                    "is_urgent": False,
                    "dt": dt,
                })

        # Add a default system welcome notification
        notifications.append({
            "type": "system",
            "icon": "🐾",
            "title": "Welcome to PetCare!",
            "desc": "Check here for reminders about vaccinations, grooming schedules, and purchases.",
            "is_unread": False,
            "is_urgent": False,
            "dt": datetime.min,
        })

        # Sort notifications (unread and urgent first, then by date descending)
        notifications.sort(key=lambda x: (x["is_unread"], x["is_urgent"], x["dt"]), reverse=True)

    except Exception as e:
        system_exceptions.handle_system_error(e)

    return templates.TemplateResponse(
        request,
        'notification.html',
        context={
            "current_page": "notification",
            "user": current_user,
            "notifications": notifications,
        },
    )


@router.get('/helpcenter', response_class=HTMLResponse, name='helpcenter')
async def tampilin_helpcenter(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request, 
        'helpcenter.html', 
        context={
            "current_page": "helpcenter",
            "user": current_user,
        }
    )

@router.get('/payment.html', response_class=HTMLResponse, name='payment')
async def tampilin_payment(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request,
        'payment.html',
        context={
            "current_page": "payment",
            "user": current_user,
        },
    )


@router.get('/choosepayment.html', response_class=HTMLResponse, name='choosepayment')
async def tampilin_choosepayment(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = await cart_repository.get_or_create_cart(db, current_user.id_user)
    cart_items = await cart_repository.get_cart_items(db, cart.id_cart)

    items = []
    subtotal = 0.0
    for ci in cart_items:
        p = await produk_repository.get_product_by_id(db, ci.id_produk)
        if p:
            item_subtotal = p.harga * ci.jumlah
            subtotal += item_subtotal
            items.append({
                "nama_produk": p.nama_produk,
                "gambar": p.gambar,
                "harga": p.harga,
                "jumlah": ci.jumlah,
                "subtotal": item_subtotal,
            })

    shipping = 2.00
    total = subtotal + shipping

    order_id = f"PetCare-Shop-{int(time.time())}"
    total_real = int(total)

    transcation_params = {
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": total_real
        },
        "credit_card": {"secure": True},
        "enabled_payments": ["qris", "gopay", "bank_transfer"]
    }
    try :
        transaction = snap.create_transaction(transcation_params)
        snap_token = transaction['token']
        print(f"Snap token generated: {snap_token}")
    except Exception as e:
        snap_token = None
        raise HTTPException(status_code=400, detail=f"Midtrans Error: {str(e)}")    
    return templates.TemplateResponse(
        request,
        'choosepayment.html',
        context={
            "current_page": "shop",
            "user": current_user,
            "items": items,
            "subtotal": subtotal,
            "shipping": shipping,
            "total": total,
            "snap_token": snap_token,

        },
    )

@router.get('/berita', response_class=HTMLResponse, name='berita')
async def tampilin_berita(request: Request):
    return templates.TemplateResponse(request, 'berita.html')

# -----------------------------------------------------------------
# ORDER DETAIL (Wajib ditambahkan agar tidak 404)
# -----------------------------------------------------------------

@router.get('/orders/{id_order}', response_class=HTMLResponse, name='order_detail')
async def detail_order(
    request: Request,
    id_order: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Ambil data order dari database berdasarkan ID
    order = await order_repository.get_order_by_id(db, id_order)
    if not order or order.id_user != current_user.id_user:
        raise HTTPException(status_code=404, detail="Order tidak ditemukan")

    # 2. Ambil produk yang ada di dalam order tersebut
    details = await order_repository.get_detail_orders_by_order(db, id_order)
    items = []
    for d in (details or []):
        p = await produk_repository.get_product_by_id(db, d.id_produk)
        items.append({
            "nama_produk": p.nama_produk if p else "Unknown",
            "jumlah": d.jumlah,
            "subtotal": d.subtotal,
        })

    # 3. Lempar ke halaman order_detail.html
    return templates.TemplateResponse(
        request,
        'order_detail.html',
        context={
            "user": current_user,
            "order": order,
            "items": items,
        }
    )