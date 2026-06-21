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
    except Exception as e:
        system_exceptions.handle_system_error(e)

    return templates.TemplateResponse(
        request,
        'petcaredashboard.html',
        context={
            "current_page": "home",
            "user": current_user,
            "pets": all_pet,
            "janji_temu": all_janji,
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

    return templates.TemplateResponse(
        request,
        'petshop.html',
        context={
            "current_page": "shop",
            "user": current_user,
            "products": products,
            "cart_map": cart_map,  # {id_produk: jumlah}
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

@router.get('/orders.html', response_class=HTMLResponse, name='orders')
async def tampilin_orders(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get all orders for the user
    orders = await order_repository.get_all_ordered_produk_by_user(db, current_user.id_user)

    # For each order, get its detail items with product name
    orders_with_items = []
    for o in (orders or []):
        details = await order_repository.get_detail_orders_by_order(db, o.id_order_produk)
        items = []
        for d in (details or []):
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
    upcoming = await booking_repository.get_booking_groomings_by_user(db, current_user.id_user)

    return templates.TemplateResponse(
        request,
        'booking.html',
        context={
            "current_page": "booking",
            "user": current_user,
            "pets": user_pets,
            "grooming_packages": packages,
            "partners": partners,
            "upcoming_bookings": upcoming,
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
    return templates.TemplateResponse(request, 'new-pet.html')



# ================================================================
#  STATIC / SEMI-STATIC PAGES  (no DB queries)
# ================================================================

@router.get('/notification', response_class=HTMLResponse, name='notification')
async def tampilin_notification(request: Request):
    return templates.TemplateResponse(
        request, 'notification.html', context={"current_page": "notification"}
    )


@router.get('/helpcenter', response_class=HTMLResponse, name='helpcenter')
async def tampilin_helpcenter(request: Request):
    return templates.TemplateResponse(
        request, 'helpcenter.html', context={"current_page": "helpcenter"}
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
