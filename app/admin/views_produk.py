"""ModelView for Produk."""
import os

from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import ModelView, action
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from wtforms import FileField
from markupsafe import Markup

from app.core.database import engine
from app.models.models import Produk


class ProductAdmin(ModelView, model=Produk):
    name = "Data Produk"
    name_plural = "Daftar Produk"
    icon = "fa-solid fa-box-open"
    column_list = [
        Produk.id_produk, 'gambar', 'nama_produk',
        Produk.harga, Produk.stok, Produk.status_produk,
    ]
    can_delete = False
    column_labels = {
        'gambar': 'Foto Produk',
        'nama_produk': 'Nama Produk',
    }

    def format_currency(self, model, name):
        value = getattr(model, name)
        if value is not None:
            formatted = f"{value:,.0f}".replace(",", ".")
            return f"Rp {formatted}"
        return "Rp 0,00"

    form_columns = ['nama_produk', 'gambar', 'harga', 'stok', "tipe_produk"]
    form_overrides = {'gambar': FileField}

    column_formatters = {
        'gambar': lambda model, attr: Markup(
            f'<img src="{model.gambar}" class="img-thumbnail" '
            f'style="max-height:50px;max-width:50px;object-fit:cover;">'
        ) if model.gambar else Markup('<i class="fa-solid fa-box-open fa-2x text-secondary"></i>'),
        'harga': lambda model, attr: Markup(
            f'<span>{ProductAdmin.format_currency(None, model, "harga")}</span>'
        ),
    }

    @action(
        name="mark_as_dihapus",
        label="Hapus",
        confirmation_message="Yakin ingin menghapus produk ini?",
        add_in_list=True,
        add_in_detail=True,
    )
    async def mark_as_dihapus(self, request: Request):
        pks_param = request.query_params.getlist("pks")
        id_list = []
        if pks_param:
            id_list = [int(x) for x in pks_param[0].split(",") if x.strip()]
        if id_list:
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            async with async_session() as session:
                stmt = (
                    update(Produk)
                    .where(Produk.id_produk.in_(id_list))
                    .values(status_produk="DIHAPUS")
                )
                await session.execute(stmt)
                await session.commit()
        return RedirectResponse(
            request.headers.get("referer", "/admin/product-model/list"),
            status_code=303,
        )

    @action(
        name="mark_as_tersedia",
        label="Tandai Tersedia",
        confirmation_message="Yakin ingin mengembalikan produk ini?",
        add_in_list=True,
        add_in_detail=True,
    )
    async def mark_as_tersedia(self, request: Request):
        pks_param = request.query_params.getlist("pks")
        id_list = []
        if pks_param:
            id_list = [int(x) for x in pks_param[0].split(",") if x.strip()]
        if id_list:
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            async with async_session() as session:
                stmt = (
                    update(Produk)
                    .where(Produk.id_produk.in_(id_list))
                    .values(status_produk="TERSEDIA")
                )
                await session.execute(stmt)
                await session.commit()
        return RedirectResponse(
            request.headers.get("referer", "/admin/product-model/list"),
            status_code=303,
        )

    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        if "gambar" in data and data["gambar"]:
            file_data = data["gambar"]
            if 'gambar' in data and hasattr(file_data, 'filename') and file_data.filename:
                upload_dir = "app/static/uploads/produk"
                os.makedirs(upload_dir, exist_ok=True)
                clean_nama = data.get("nama_produk", "produk").replace(" ", "_")
                filename = f"{clean_nama}_{file_data.filename}"
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(await file_data.read())
                data["gambar"] = f"/static/uploads/produk/{filename}"

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"
