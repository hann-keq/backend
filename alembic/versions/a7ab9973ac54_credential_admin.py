"""credential_admin

Revision ID: a7ab9973ac54
Revises: a0f8b0c2a5a6
Create Date: 2026-06-20 17:49:00.964456

"""
from typing import Sequence, Union
from datetime import datetime, timezone
from alembic import op
import sqlalchemy as sa
from app.core.security import hash_password as pw


# revision identifiers, used by Alembic.
revision: str = 'a7ab9973ac54'
down_revision: Union[str, Sequence[str], None] = 'a0f8b0c2a5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    user_table = sa.table(
        'users',
        sa.column('id_', sa.Integer),
        sa.column('nama', sa.String),
        sa.column('email', sa.String),
        sa.column('password', sa.String),
        sa.column('no_telepon', sa.String),
        sa.column('role', sa.String),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )

    # Insert admin user
    op.bulk_insert(
        user_table,
        [
            {
                'nama': 'Admin',
                'email': 'admin@example.com',
                'password': pw('admin123'),
                'no_telepon': '081234567890',
                'role': 'admin',
                'created_at': datetime.now()
            }
        ]
    )



def downgrade() -> None:
    """Downgrade schema."""
    # Delete the admin user
    op.execute(
        sa.text("DELETE FROM users WHERE email = :email").bindparams(email='admin@example.com')
    )

