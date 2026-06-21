"""ModelView for Pembayaran (split into Produk / Grooming / Janji Temu)."""
from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import ModelView, action
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload

from app.core.database import engine
from app.admin.models_proxy import (
    PembayaranProdukModel,
    PembayaranGroomingModel,
    PembayaranJanjiTemuModel,
)


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
        PembayaranProdukModel.created_at,
    ]

    def list_query(self, request: Request):
        return select(PembayaranProdukModel).where(
            PembayaranProdukModel.id_order_produk.isnot(None)
        )

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"

    @action(
        name="mark_as_completed",
        label="Tandai Dibayar",
        confirmation_message="Yakin ingin mengubah status menjadi DIBAYAR?",
        add_in_list=True,
        add_in_detail=True,
    )
    async def mark_as_completed(self, request: Request):
        pks = request.query_params.getlist("pks")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            for pk in pks:
                result = await session.execute(
                    select(PembayaranProdukModel).where(
                        PembayaranProdukModel.id_pembayaran == int(pk)
                    )
                )
                pembayaran = result.scalar_one_or_none()
                if pembayaran:
                    pembayaran.status_pembayaran = "DIBAYAR"
            await session.commit()
        return RedirectResponse(
            request.headers.get("referer", "/admin/pembayaran-produk-model/list"),
            status_code=303,
        )


class PembayaranGroomingAdmin(ModelView, model=PembayaranGroomingModel):
    name = "Pembayaran Grooming"
    name_plural = "Pembayaran Grooming"
    icon = "fa-solid fa-dog"
    category = "Daftar Pembayaran"
    category_icon = "fa-solid fa-bars"

    column_list = [
        PembayaranGroomingModel.id_pembayaran,
        "user.nama",
        PembayaranGroomingModel.id_booking_grooming,
        PembayaranGroomingModel.jumlah_bayar,
        PembayaranGroomingModel.metode_pembayaran,
        PembayaranGroomingModel.status_pembayaran,
        PembayaranGroomingModel.created_at,
    ]
    column_labels = {"user.nama": "Nama User"}

    def list_query(self, request: Request):
        return (
            select(PembayaranGroomingModel)
            .options(joinedload(PembayaranGroomingModel.user))
            .where(PembayaranGroomingModel.id_booking_grooming.isnot(None))
        )

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"

    @action(
        name="mark_as_completed",
        label="Tandai Dibayar",
        confirmation_message="Yakin ingin mengubah status menjadi DIBAYAR?",
        add_in_list=True,
        add_in_detail=True,
    )
    async def mark_as_completed(self, request: Request):
        pks = request.query_params.getlist("pks")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            for pk in pks:
                result = await session.execute(
                    select(PembayaranGroomingModel).where(
                        PembayaranGroomingModel.id_pembayaran == int(pk)
                    )
                )
                pembayaran = result.scalar_one_or_none()
                if pembayaran:
                    pembayaran.status_pembayaran = "DIBAYAR"
            await session.commit()
        return RedirectResponse(
            request.headers.get("referer", "/admin/pembayaran-grooming-model/list"),
            status_code=303,
        )

    @action(
        name="mark_as_menunggu",
        label="Tandai Menunggu",
        confirmation_message="Yakin ingin mengubah status menjadi MENUNGGU?",
        add_in_list=True,
        add_in_detail=True,
    )
    async def mark_as_menunggu(self, request: Request):
        pks = request.query_params.getlist("pks")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            for pk in pks:
                result = await session.execute(
                    select(PembayaranGroomingModel).where(
                        PembayaranGroomingModel.id_pembayaran == int(pk)
                    )
                )
                pembayaran = result.scalar_one_or_none()
                if pembayaran:
                    pembayaran.status_pembayaran = "MENUNGGU"
            await session.commit()
        return RedirectResponse(
            request.headers.get("referer", "/admin/pembayaran-grooming-model/list"),
            status_code=303,
        )


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
        PembayaranJanjiTemuModel.created_at,
    ]

    def list_query(self, request: Request):
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
        add_in_detail=True,
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
        return RedirectResponse(
            request.headers.get("referer", "/admin/pembayaran-janji-temu-model/list"),
            status_code=303,
        )
