"""renombrar columna type a task_type en tabla task

Revision ID: a1b2c3d4e5f6
Revises: 8a91f5a9a98c
Create Date: 2026-07-31

La columna `type` sombrea el builtin de Python. Se renombra a
`task_type` por claridad y para evitar errores de estilo.
"""

from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "8a91f5a9a98c"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("task") as batch_op:
        batch_op.alter_column("type", new_column_name="task_type")


def downgrade():
    with op.batch_alter_table("task") as batch_op:
        batch_op.alter_column("task_type", new_column_name="type")
