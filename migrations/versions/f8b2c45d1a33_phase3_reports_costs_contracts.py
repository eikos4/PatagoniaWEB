"""add phase 3 reports costs contracts templates audit

Revision ID: f8b2c45d1a33
Revises: e7a1b34c9f22
"""
from alembic import op
import sqlalchemy as sa


revision = 'f8b2c45d1a33'
down_revision = 'e7a1b34c9f22'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('shipment_costs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('shipment_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=30), nullable=False),
        sa.Column('concepto', sa.String(length=200), nullable=False),
        sa.Column('monto', sa.Float(), nullable=False),
        sa.Column('moneda', sa.String(length=5), nullable=False),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['admin_users.id']),
        sa.ForeignKeyConstraint(['shipment_id'], ['shipments.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('contracts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero', sa.String(length=30), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('folder_id', sa.Integer(), nullable=True),
        sa.Column('country_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('responsable_id', sa.Integer(), nullable=True),
        sa.Column('estado', sa.String(length=20), nullable=False),
        sa.Column('fecha_inicio', sa.DateTime(), nullable=True),
        sa.Column('fecha_fin', sa.DateTime(), nullable=True),
        sa.Column('renovacion_auto', sa.Boolean(), nullable=True),
        sa.Column('condiciones', sa.Text(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('stored_filename', sa.String(length=255), nullable=True),
        sa.Column('content_type', sa.String(length=120), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id']),
        sa.ForeignKeyConstraint(['created_by_id'], ['admin_users.id']),
        sa.ForeignKeyConstraint(['folder_id'], ['client_folders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['responsable_id'], ['admin_users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero')
    )

    op.create_table('document_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('tipo', sa.String(length=30), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('stored_filename', sa.String(length=255), nullable=True),
        sa.Column('content_type', sa.String(length=120), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=True),
        sa.Column('uploaded_by_id', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['admin_users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('accion', sa.String(length=30), nullable=False),
        sa.Column('entidad_tipo', sa.String(length=30), nullable=False),
        sa.Column('entidad_id', sa.Integer(), nullable=True),
        sa.Column('entidad_ref', sa.String(length=120), nullable=True),
        sa.Column('detalle', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['admin_users.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('activity_logs')
    op.drop_table('document_templates')
    op.drop_table('contracts')
    op.drop_table('shipment_costs')
