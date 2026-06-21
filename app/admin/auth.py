"""Authentication backend for SQLAdmin — admin + partner login."""
from fastapi import Request
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import engine
from app.core.security import verify_password
from app.models.models import User, Partner, RoleUser


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email_input = form.get("username")
        password_input = form.get("password")

        if not email_input or not password_input:
            return False

        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            # Check users table (admin role)
            result = await session.execute(select(User).where(User.email == email_input))
            user_data = result.scalar_one_or_none()

            if user_data and verify_password(password_input, user_data.password):
                if user_data.role == RoleUser.ADMIN:
                    request.session.update({
                        "user_role": "admin",
                        "user_id": user_data.id_user,
                    })
                    return True

            # Check partners table
            result = await session.execute(
                select(Partner).where(Partner.email == email_input, Partner.email.is_not(None))
            )
            partner_data = result.scalar_one_or_none()

            if partner_data and verify_password(password_input, partner_data.password):
                request.session.update({
                    "user_role": "partner",
                    "partner_id": partner_data.id_partner,
                    "jenis_partner": partner_data.jenis_partner.value,
                })
                return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("user_role") is not None
