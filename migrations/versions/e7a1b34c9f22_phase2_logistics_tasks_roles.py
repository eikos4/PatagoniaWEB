"""add phase 2 logistics tasks roles

Revision ID: e7a1b34c9f22
Revises: d4e8f92a1c33
"""
from alembic import op
import sqlalchemy as sa


revision = 'e7a1b34c9f22'
down_revision = 'd4e8f92a1c33'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('admin_users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rol', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('nombre', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('activo', sa.Boolean(), nullable=True))

    op.execute("UPDATE admin_users SET rol = 'ceo', activo = 1 WHERE rol IS NULL")

    with op.batch_alter_table('admin_users', schema=None) as batch_op:
        batch_op.alter_column('rol', nullable=False)

    with op.batch_alter_table('shipments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('numero_booking', sa.String(length=60), nullable=True))
        batch_op.add_column(sa.Column('tipo_contenedor', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('transporte_terrestre', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('agente_aduana', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('ultima_ubicacion', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('tracking_notas', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('responsable_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('fecha_zarpe', sa.DateTime(), nullable=True))
        batch_op.create_foreign_key('fk_shipments_responsable', 'admin_users', ['responsable_id'], ['id'])

    op.create_table('shipment_milestones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('shipment_id', sa.Integer(), nullable=False),
        sa.Column('etapa', sa.String(length=30), nullable=False),
        sa.Column('orden', sa.Integer(), nullable=True),
        sa.Column('completado', sa.Boolean(), nullable=True),
        sa.Column('fecha', sa.DateTime(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('updated_by_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['shipment_id'], ['shipments.id']),
        sa.ForeignKeyConstraint(['updated_by_id'], ['admin_users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('internal_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('responsable_id', sa.Integer(), nullable=True),
        sa.Column('shipment_id', sa.Integer(), nullable=True),
        sa.Column('folder_id', sa.Integer(), nullable=True),
        sa.Column('prioridad', sa.String(length=15), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=False),
        sa.Column('fecha_limite', sa.DateTime(), nullable=True),
        sa.Column('comentarios', sa.Text(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['admin_users.id']),
        sa.ForeignKeyConstraint(['folder_id'], ['client_folders.id']),
        sa.ForeignKeyConstraint(['responsable_id'], ['admin_users.id']),
        sa.ForeignKeyConstraint(['shipment_id'], ['shipments.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('internal_tasks')
    op.drop_table('shipment_milestones')
    with op.batch_alter_table('shipments', schema=None) as batch_op:
        batch_op.drop_constraint('fk_shipments_responsable', type_='foreignkey')
        batch_op.drop_column('fecha_zarpe')
        batch_op.drop_column('responsable_id')
        batch_op.drop_column('tracking_notas')
        batch_op.drop_column('ultima_ubicacion')
        batch_op.drop_column('agente_aduana')
        batch_op.drop_column('transporte_terrestre')
        batch_op.drop_column('tipo_contenedor')
        batch_op.drop_column('numero_booking')
    with op.batch_alter_table('admin_users', schema=None) as batch_op:
        batch_op.drop_column('activo')
        batch_op.drop_column('nombre')
        batch_op.drop_column('rol')
