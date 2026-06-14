"""add shipments module

Revision ID: c8f3a12b5e21
Revises: b7c2e91f4d10
Create Date: 2026-06-14 00:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c8f3a12b5e21'
down_revision = 'b7c2e91f4d10'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('shipments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero', sa.String(length=30), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('folder_id', sa.Integer(), nullable=True),
        sa.Column('cliente_nombre', sa.String(length=120), nullable=False),
        sa.Column('cliente_empresa', sa.String(length=120), nullable=True),
        sa.Column('estado', sa.String(length=25), nullable=False),
        sa.Column('puerto_origen', sa.String(length=80), nullable=True),
        sa.Column('puerto_destino', sa.String(length=80), nullable=True),
        sa.Column('naviera', sa.String(length=120), nullable=True),
        sa.Column('numero_contenedor', sa.String(length=40), nullable=True),
        sa.Column('numero_bl', sa.String(length=60), nullable=True),
        sa.Column('tipo_carga', sa.String(length=30), nullable=True),
        sa.Column('temperatura', sa.String(length=40), nullable=True),
        sa.Column('etd', sa.DateTime(), nullable=True),
        sa.Column('eta', sa.DateTime(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('fecha_embarque', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['admin_users.id']),
        sa.ForeignKeyConstraint(['folder_id'], ['client_folders.id']),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero')
    )


def downgrade():
    op.drop_table('shipments')
