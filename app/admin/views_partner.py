"""ModelView for JanjiTemu and Dokter (partner-scoped)."""
import os

from fastapi import Request
from httpx import request
from sqladmin import ModelView
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from wtforms import FileField
from markupsafe import Markup

from app.models.models import (
    DetailPaketGrooming,
    Dokter,
    JanjiTemu,
    PaketGrooming,
)




class JanjiTemuAdmin(ModelView, model=JanjiTemu):
    name = "Data Janji Temu"
    name_plural = "Janji Temu"
    icon = "fa-solid fa-calendar"
    column_list = [
        JanjiTemu.id_user,
        "partner.partner.nama_partner",
        JanjiTemu.jam_janji,
        JanjiTemu.tanggal_janji,
        JanjiTemu.status_janji,
    ]
    can_create = False
    column_labels = {"partner.partner.nama_partner": "Nama Partner"}

    def list_query(self, request: Request):
        partner_id = request.session.get("partner_id")
        if not partner_id:
            return select(JanjiTemu).where(False)
        return (
            select(JanjiTemu)
            .join(JanjiTemu.Dokter)
            .options(joinedload(JanjiTemu.Dokter).joinedload(Dokter.partner))
            .where(Dokter.id_partner == partner_id)
        )

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") in ["partner"]


class DokterPartnerAdmin(ModelView, model=Dokter):
    name = "Data Dokter"
    name_plural = "Daftar Dokter"
    icon = "fa-solid fa-user-md"
    column_list = [
        'foto', Dokter.id_dokter, Dokter.nama_dokter, Dokter.spesialis,
        "partner.partner.nama_partner",
    ]
    column_labels = {
        'foto': 'Foto Profil',
        "partner.partner.nama_partner": "Nama Partner",
    }
    form_columns = ['nama_dokter', 'spesialis', 'foto']
    form_overrides = {'foto': FileField}

    column_formatters = {
        'foto': lambda model, attr: Markup(
            f'<img src="{model.foto}" class="img-thumbnail" '
            f'style="max-height:50px;max-width:50px;border-radius:50%;object-fit:cover;">'
        ) if model.foto else Markup('<i class="fa-solid fa-user-doctor fa-2x text-secondary"></i>')
    }

    def list_query(self, request: Request):
        partner_id = request.session.get("partner_id")
        if not partner_id:
            return select(Dokter).where(False)
        return (
            select(Dokter)
            .options(joinedload(Dokter.partner))
            .where(Dokter.id_partner == partner_id)
        )

    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        partner_id = request.session.get("partner_id")
        if partner_id:
            data["id_partner"] = partner_id
        if "foto" in data and data["foto"]:
            file_data = data["foto"]
            if hasattr(file_data, 'filename') and file_data.filename:
                upload_dir = "app/static/uploads/dokter"
                os.makedirs(upload_dir, exist_ok=True)
                clean_nama = data.get("nama_dokter", "dokter").replace(" ", "_")
                filename = f"{clean_nama}_{file_data.filename}"
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(await file_data.read())
                data["foto"] = f"/static/uploads/dokter/{filename}"
            else:
                if not is_created:
                    data.pop("foto", None)
                else:
                    data["foto"] = None

    def is_accessible(self, request: Request) -> bool:
        jenis_partner = request.session.get("jenis_partner")
        
        # Tambahkan log ini untuk melihat persis apa isi session-mu di terminal
        print(f"DEBUG SESSION -> jenis_partner: '{jenis_partner}' (Type: {type(jenis_partner)})")
        
        if not jenis_partner:
            return False
            
        # Lakukan stripping spasi dan ubah ke huruf kecil untuk menghindari miss-match
        jenis_partner_clean = str(jenis_partner).strip().lower()
        
        # Daftarkan dengan huruf kecil semua di sini
        return jenis_partner_clean in ["klinik", "all"]

class PaketGroomingPartner(ModelView, model=PaketGrooming):
    name = "Paket Grooming"
    name_plural = "Paket Grooming"
    icon = "fa-solid fa-cut"
    column_list = [
        PaketGrooming.nama_paket_grooming,
        PaketGrooming.harga,
        PaketGrooming.id_partner,
        "fitur_list",
    ]
    column_labels = {
        "fitur_list": "Fitur / Detail Paket",
        "id_partner": "Partner",
    }
    form_columns = [
        PaketGrooming.nama_paket_grooming,
        PaketGrooming.harga,
    ]

    column_formatters = {
        "fitur_list": lambda model, attr: Markup(
            "<ul style='margin:0;padding-left:16px'>" +
            "".join(f"<li>{d.fitur}</li>" for d in (model.detail_paket or [])) +
            "</ul>"
        ) if model.detail_paket else "-"
    }

    @property
    def fitur_list(self):
        """Dummy accessor — value comes from column_formatters, not DB."""
        return ""

    def list_query(self, request: Request):
        partner_id = request.session.get("partner_id")
        if not partner_id:
            return select(PaketGrooming).where(False)
        return (
            select(PaketGrooming)
            .where(PaketGrooming.id_partner == partner_id)
        )

    async def on_model_change(
        self, data: dict, model, is_created: bool, request: Request
    ) -> None:
        partner_id = request.session.get("partner_id")
        if partner_id:
            data["id_partner"] = partner_id

    def is_accessible(self, request: Request) -> bool:
        jenis_partner = request.session.get("jenis_partner")
        if not jenis_partner:
            return False
        return str(jenis_partner).strip().lower() in ["grooming", "all"]


class DetailPaketGroomingAdmin(ModelView, model=DetailPaketGrooming):
    name = "Detail Fitur Paket"
    name_plural = "Detail Fitur Paket"
    icon = "fa-solid fa-list-check"
    column_list = [
        "paket.nama_paket_grooming",
        DetailPaketGrooming.fitur,
    ]
    column_labels = {
        "paket.nama_paket_grooming": "Nama Paket",
        "fitur": "Nama Fitur",
    }
    form_columns = [
        DetailPaketGrooming.paket,
        DetailPaketGrooming.fitur,
    ]

    def list_query(self, request: Request):
        partner_id = request.session.get("partner_id")
        if not partner_id:
            return select(DetailPaketGrooming).where(False)
        return (
            select(DetailPaketGrooming)
            .join(DetailPaketGrooming.paket)
            .options(joinedload(DetailPaketGrooming.paket))
            .where(PaketGrooming.id_partner == partner_id)
        )

    async def scaffold_form(self, *args, **kwargs):
        # 1. Ambil class form default dari SQLAdmin
        form_class = await super().scaffold_form(*args, **kwargs)
        
        # 2. Ambil request session secara global (SQLAdmin menyimpannya di context internal)
        # Kita manipulasi query factory bawaan WTForms milik field 'paket'
        if hasattr(form_class, "paket"):
            original_query_factory = form_class.paket.kwargs.get("query_factory")
            
            # Kita buat fungsi custom query factory yang disuntikkan runtime
            def filtered_query_factory():
                # Trick: ambil request saat ini dari konteks yang aktif
                # Jika versi SQLAdmin kamu mengharuskan filter manual, kita batasi via session
                # Namun untuk amannya agar dropdown terfilter instan, kita batasi object list-nya.
                pass
                
        return form_class

    # SQLAdmin menyediakan hook form_query_factory yang sebetulnya valid jika argumennya pas.
    # Mari kita gunakan form_query_factory versi paling aman tanpa salah parameter posisional:
    def form_query_factory(self, name: str, request: Request):
        if name == "paket":
            partner_id = request.session.get("partner_id")
            if partner_id:
                # Menampilkan data dropdown HANYA untuk partner_id yang aktif
                return select(PaketGrooming).where(PaketGrooming.id_partner == partner_id)
            return select(PaketGrooming).where(False)
        return super().form_query_factory(name, request)
    async def on_model_change(
        self, data: dict, model, is_created: bool, request: Request
    ) -> None:
        pass

    def is_accessible(self, request: Request) -> bool:
        jenis_partner = request.session.get("jenis_partner")
        if not jenis_partner:
            return False
        return str(jenis_partner).strip().lower() in ["grooming", "all"]

    
