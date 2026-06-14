"""add orders module

Revision ID: b7c2e91f4d10
Revises: 5a15fce74aea
Create Date: 2026-06-13 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b7c2e91f4d10'
down_revision = '5a15fce74aea'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero', sa.String(length=30), nullable=False),
        sa.Column('quotation_id', sa.Integer(), nullable=True),
        sa.Column('folder_id', sa.Integer(), nullable=True),
        sa.Column('cliente_nombre', sa.String(length=120), nullable=False),
        sa.Column('cliente_empresa', sa.String(length=120), nullable=True),
        sa.Column('cliente_email', sa.String(length=120), nullable=True),
        sa.Column('cliente_telefono', sa.String(length=30), nullable=True),
        sa.Column('cliente_pais', sa.String(length=80), nullable=True),
        sa.Column('estado', sa.String(length=25), nullable=False),
        sa.Column('moneda', sa.String(length=5), nullable=False),
        sa.Column('incoterm', sa.String(length=20), nullable=True),
        sa.Column('descuento_pct', sa.Float(), nullable=True),
        sa.Column('anticipo_monto', sa.Float(), nullable=True),
        sa.Column('subtotal', sa.Float(), nullable=True),
        sa.Column('total', sa.Float(), nullable=True),
        sa.Column('condiciones', sa.Text(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('fecha_pedido', sa.DateTime(), nullable=True),
        sa.Column('fecha_entrega_estimada', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['admin_users.id']),
        sa.ForeignKeyConstraint(['folder_id'], ['client_folders.id']),
        sa.ForeignKeyConstraint(['quotation_id'], ['quotations.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero')
    )
    op.create_table('order_lines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('descripcion', sa.String(length=255), nullable=False),
        sa.Column('cantidad', sa.Float(), nullable=False),
        sa.Column('unidad', sa.String(length=20), nullable=True),
        sa.Column('precio_unitario', sa.Float(), nullable=False),
        sa.Column('orden', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('order_lines')
    op.drop_table('orders')
