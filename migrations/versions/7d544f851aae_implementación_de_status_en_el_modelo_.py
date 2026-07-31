"""Implementación de status en el modelo checklist

Revision ID: 7d544f851aae
Revises: 190ad2c5ce82
Create Date: 2025-07-20 19:00:24.212627

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "7d544f851aae"
down_revision = "190ad2c5ce82"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("objetive") as batch_op:
        batch_op.alter_column("objetive", new_column_name="objective")
    op.rename_table("objetive", "objective")

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table("objective") as batch_op:
        batch_op.alter_column("objective", new_column_name="objetive")
    op.rename_table("objective", "objetive")

    # ### end Alembic commands ###
