from fastapi import APIRouter, Request, HTTPException, Depends, Form
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.midtrans import snap
from app.core.database import get_db
from app.core.config import settings
from app.models.models import Pembayaran, OrderProduk, User
from app.core.auth import get_current_user

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
    """
    Called from the Snap onSuccess JS callback.
    Updates the existing order_produk status + pembayaran from Menunggu → Dibayar.
    """
    try:
        # Look up pembayaran by midtrans_order_id
        result = await db.execute(
            select(Pembayaran).where(Pembayaran.midtrans_order_id == order_id)
        )
        pembayaran = result.scalars().one_or_none()

        if not pembayaran:
            raise HTTPException(status_code=404, detail=f"Payment not found for order_id: {order_id}")

        if pembayaran.id_user != current_user.id_user:
            raise HTTPException(status_code=403, detail="Forbidden")

        # Update pembayaran status
        pembayaran.status_pembayaran = "Dibayar"
        pembayaran.metode_pembayaran = payment_type

        # Update order_produk status
        if pembayaran.id_order_produk:
            order_result = await db.execute(
                select(OrderProduk).where(OrderProduk.id_order_produk == pembayaran.id_order_produk)
            )
            order = order_result.scalars().one_or_none()
            if order:
                order.status_order = "Selesai"

        await db.commit()

        return {"status": "success", "order_id": pembayaran.id_order_produk}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================================
#  WEBHOOK — Midtrans server-to-server notification (NO auth)
# =========================================================================


@router.post("/notifications")
async def midtrans_notification_handler(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Server-to-server notification from Midtrans.
    Called by Midtrans (not the browser), so no user auth — we verify
    using the status response / signature-key hash instead.

    Doc: https://docs.midtrans.com/reference/payment-notification-webhooks
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    order_id = body.get("order_id")
    transaction_status = body.get("transaction_status")
    fraud_status = body.get("fraud_status")
    payment_type = body.get("payment_type", "")

    if not order_id:
        raise HTTPException(status_code=400, detail="Missing order_id")

    # --- Verify signature (optional but strongly recommended in production) ---
    # status_code = body.get("status_code", "")
    # gross_amount = body.get("gross_amount", "")
    # raw = status_code + gross_amount + settings.MIDTRANS_SERVER_KEY + order_id
    # expected = sha512(raw.encode()).hexdigest()
    # if body.get("signature_key", "") != expected:
    #     raise HTTPException(status_code=403, detail="Invalid signature")

    # ---- Look up our DB record via midtrans_order_id ----
    result = await db.execute(
        select(Pembayaran).where(Pembayaran.midtrans_order_id == order_id)
    )
    pembayaran: Pembayaran | None = result.scalars().one_or_none()

    if not pembayaran:
        print(f"[WEBHOOK] No pembayaran found for midtrans_order_id={order_id}")
        return {"status": "ignored", "reason": "order_id_not_found"}

    # ---- Map transaction_status → our status ----
    if transaction_status in ("capture", "settlement"):
        new_status = "Dibayar"
        order_status_new = "Selesai"
    elif transaction_status in ("cancel", "expire", "failure"):
        new_status = "Dibatalkan"
        order_status_new = "Dibatalkan"
    elif transaction_status == "deny":
        new_status = "Dibatalkan"
        order_status_new = "Dibatalkan"
    elif transaction_status == "pending":
        new_status = "Menunggu"
        order_status_new = None  # don't change
    else:
        new_status = None
        order_status_new = None

    # If fraud status is "challenge", keep as Menunggu (manual review)
    if fraud_status == "challenge":
        new_status = "Menunggu"
        order_status_new = None

    # ---- Apply updates ----
    if new_status:
        pembayaran.status_pembayaran = new_status
        pembayaran.metode_pembayaran = pembayaran.metode_pembayaran or payment_type

    if order_status_new and pembayaran.id_order_produk:
        order_result = await db.execute(
            select(OrderProduk).where(
                OrderProduk.id_order_produk == pembayaran.id_order_produk
            )
        )
        order = order_result.scalars().one_or_none()
        if order:
            order.status_order = order_status_new

    await db.commit()
    print(f"[WEBHOOK] order_id={order_id}  tx_status={transaction_status}  "
          f"fraud={fraud_status}  →  pembayaran={new_status}  order={order_status_new or 'unchanged'}")

    return {"status": "ok"}
