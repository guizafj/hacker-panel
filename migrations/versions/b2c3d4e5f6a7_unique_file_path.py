"""añadir unique constraint file_path a theory, write_ups y scripts

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-31

Los modelos declaran UniqueConstraint sobre file_path, pero ninguna
migración previa lo creaba. Se añade para que el esquema creado por
`flask db upgrade` coincida con los modelos.
"""

from alembic import op

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("theory") as batch_op:
        batch_op.create_unique_constraint("uq_theory_file_path", ["file_path"])
    with op.batch_alter_table("write_ups") as batch_op:
        batch_op.create_unique_constraint("uq_writeups_file_path", ["file_path"])
    with op.batch_alter_table("scripts") as batch_op:
        batch_op.create_unique_constraint("uq_scripts_file_path", ["file_path"])


def downgrade():
    with op.batch_alter_table("theory") as batch_op:
        batch_op.drop_constraint("uq_theory_file_path", type_="unique")
    with op.batch_alter_table("write_ups") as batch_op:
        batch_op.drop_constraint("uq_writeups_file_path", type_="unique")
    with op.batch_alter_table("scripts") as batch_op:
        batch_op.drop_constraint("uq_scripts_file_path", type_="unique")
