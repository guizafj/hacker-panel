"""empty message

Revision ID: 363a1ea577a7
Revises: 798bbef16e5e
Create Date: 2026-03-11 11:39:31.185518

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "363a1ea577a7"
down_revision = "798bbef16e5e"
branch_labels = None
depends_on = None


def upgrade():
    # La tabla ya puede existir renombrada desde 7d544f851aae (objetive -> objective).
    # En ese caso solo hay que reconciliar el esquema: añadir `status` y quitar `completed`.
    # Si existe `objetive` sin renombrar, se descarta.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("objective")}

    if "status" not in columns:
        op.add_column(
            "objective", sa.Column("status", sa.String(length=64), nullable=True)
        )
    if "completed" in columns:
        with op.batch_alter_table("objective") as batch_op:
            batch_op.drop_column("completed")

    if "objetive" in inspector.get_table_names():
        op.drop_table("objetive")


def downgrade():
    # Revierte al esquema previo (objective con `completed` y sin `status`),
    # coherente con el estado que deja 7d544f851aae.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("objective")}

    if "completed" not in columns:
        op.add_column("objective", sa.Column("completed", sa.Boolean(), nullable=True))
    if "status" in columns:
        with op.batch_alter_table("objective") as batch_op:
            batch_op.drop_column("status")
