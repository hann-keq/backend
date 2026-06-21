"""ModelView for User, Partner, Pet."""
import os

from fastapi import Request
from sqladmin import ModelView
from wtforms import FileField
from markupsafe import Markup

from app.core.security import hash_password
from app.models.models import User, Partner, Pet


class UserAdmin(ModelView, model=User):
    name = "Data User/Admin"
    name_plural = "Kelola User & Admin"
    icon = "fa-solid fa-users"
    column_list = [User.id_user, 'foto', User.nama, User.email, User.role]
    column_labels = {'foto': 'Foto Profil'}
    form_columns = ["nama", "email", "no_telepon", "password", "role", 'foto']
    form_overrides = {'foto': FileField}

    column_formatters = {
        'foto': lambda model, attr: Markup(
            f'<img src="{model.foto}" class="img-thumbnail" '
            f'style="max-height:50px;max-width:50px;object-fit:cover;">'
        ) if model.foto else Markup('<i class="fa-solid fa-user fa-2x text-secondary"></i>')
    }

    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        if "password" in data and data["password"]:
            data["password"] = hash_password(data["password"])
        if "foto" in data and data["foto"]:
            file_data = data["foto"]
            if hasattr(file_data, 'filename') and file_data.filename:
                upload_dir = "app/static/uploads/user"
                os.makedirs(upload_dir, exist_ok=True)
                clean_nama = data.get("nama", "user").replace(" ", "_")
                filename = f"{clean_nama}_{file_data.filename}"
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(await file_data.read())
                data["foto"] = f"/static/uploads/user/{filename}"
            else:
                if not is_created:
                    data.pop("foto", None)
                else:
                    data["foto"] = None

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"


class PartnerAdmin(ModelView, model=Partner):
    name = "Data Partner"
    name_plural = "Kelola Partner"
    icon = "fa-solid fa-handshake"
    column_list = [Partner.id_partner, Partner.nama_partner, Partner.jenis_partner, Partner.email]
    form_columns = ["nama_partner", "jenis_partner", "alamat", "no_telepon", "email", "password"]

    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        if "password" in data and data["password"]:
            data["password"] = hash_password(data["password"])

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"


class PetAdmin(ModelView, model=Pet):
    name = "Data Hewan"
    name_plural = "Daftar Hewan"
    icon = "fa-solid fa-paw"
    column_list = [Pet.id_pet, Pet.nama_hewan, Pet.jenis_hewan, Pet.id_user]

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("user_role") == "admin"
