"""Proxy models to split pembayaran table by FK type."""
from app.models.models import Pembayaran


class PembayaranProdukModel(Pembayaran):
    pass


class PembayaranGroomingModel(Pembayaran):
    pass


class PembayaranJanjiTemuModel(Pembayaran):
    pass
