from fastapi import APIRouter, Request, HTTPException, Depends, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.midtrans import snap
from app.core.database import get_db
from app.models.models import Pembayaran, User
from app.core.auth import get_current_user
from app.repositories import (
    cart_repository,
    order_repository,
    produk_repository,
)

router = APIRouter(prefix="/midtrans", tags=["Midtrans Payment"])


class CheckoutRequest(BaseModel):
    order_id: str
    total_bayar: int


@router.post("/token")
async def get_snap_token(request: CheckoutRequest):
    transaction_params = {
        "transaction_details": {
            "order_id": request.order_id,
            "gross_amount": request.total_bayar,
        },
        "credit_card": {"secure": True},
        "enabled_payments": ["qris", "gopay", "bank_transfer"],
    }
    try:
        transaction = snap.create_transaction(transaction_params)
        return {
            "status": "success",
            "token": transaction["token"],
            "redirect_url": transaction["redirect_url"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Midtrans Error: {str(e)}")


@router.post("/callback")
async def midtrans_callback(
    order_id: str = Form(...),
    payment_type: str = Form("QRIS"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"Midtrans callback received: order_id={order_id}, payment_type={payment_type}")
    """
    Called from the Snap onSuccess JS callback.
    Creates order_produk + detail_order + pembayaran from the user's DB cart.
    """
    try:
        cart = await cart_repository.get_or_create_cart(db, current_user.id_user)
        cart_items = await cart_repository.get_cart_items(db, cart.id_cart)

        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        total_harga = 0.0
        detail_data = []

        for ci in cart_items:
            p = await produk_repository.get_product_by_id(db, ci.id_produk)
            if p and p.stok >= ci.jumlah:
                subtotal = p.harga * ci.jumlah
                total_harga += subtotal
                detail_data.append((ci.id_produk, ci.jumlah, subtotal))

        if not detail_data:
            raise HTTPException(status_code=400, detail="No valid items in cart")

        # Create order
        new_order = await order_repository.create_order_produk(
            db,
            {
                "id_user": current_user.id_user,
                "total_harga": total_harga,
                "status_order": "Menunggu",
            },
        )

        # Create detail_order and reduce stock
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

        # Create pembayaran record
        pembayaran = Pembayaran(
            id_user=current_user.id_user,
            id_order_produk=new_order.id_order_produk,
            jumlah_bayar=total_harga,
            metode_pembayaran=payment_type,
            status_pembayaran="Dibayar",
        )
        db.add(pembayaran)
        await db.commit()

        # Clear cart
        await cart_repository.clear_cart(db, cart.id_cart)

        return {"status": "success", "order_id": new_order.id_order_produk}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
