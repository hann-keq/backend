"""Schemas for client-side cart batch sync."""
from pydantic import BaseModel, conint


class CartItemPayload(BaseModel):
    """A single item sent from the client's localStorage cart."""
    id_produk: int
    jumlah: conint(gt=0)  # positive quantity only


class CartSyncRequest(BaseModel):
    """Full payload the client sends when clicking Checkout."""
    items: list[CartItemPayload]
