"""add content_hash and updated_at to file models

Revision ID: 8a91f5a9a98c
Revises: 363a1ea577a7
Create Date: 2026-01-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8a91f5a9a98c"
down_revision = "363a1ea577a7"
branch_labels = None
depends_on = None


def upgrade():
    # SQLite no soporta ALTER COLUMN directo.
    # batch_alter_table crea una tabla temporal, copia datos y renombra.
    # IMPORTANTE: no declaramos UniqueConstraint aquí porque file_path
    # ya existe en la tabla y la unicidad se mantiene desde la creación original.
    # Solo añadimos las columnas nuevas.

    with op.batch_alter_table("theory", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("content_hash", sa.String(length=32), nullable=True)
        )
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=True))

    with op.batch_alter_table("write_ups", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("content_hash", sa.String(length=32), nullable=True)
        )
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=True))

    with op.batch_alter_table("scripts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("content_hash", sa.String(length=32), nullable=True)
        )
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table("scripts", schema=None) as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("content_hash")

    with op.batch_alter_table("write_ups", schema=None) as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("content_hash")

    with op.batch_alter_table("theory", schema=None) as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("content_hash")
