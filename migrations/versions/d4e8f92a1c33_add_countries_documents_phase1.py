"""add countries, requirements and export documents

Revision ID: d4e8f92a1c33
Revises: c8f3a12b5e21
Create Date: 2026-06-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd4e8f92a1c33'
down_revision = 'c8f3a12b5e21'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('countries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=80), nullable=False),
        sa.Column('codigo', sa.String(length=5), nullable=False),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo'),
        sa.UniqueConstraint('nombre')
    )
    op.create_table('country_requirements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('country_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('tipo', sa.String(length=30), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('obligatorio', sa.Boolean(), nullable=True),
        sa.Column('orden', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('export_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('tipo', sa.String(length=30), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=False),
        sa.Column('folder_id', sa.Integer(), nullable=True),
        sa.Column('shipment_id', sa.Integer(), nullable=True),
        sa.Column('country_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('stored_filename', sa.String(length=255), nullable=True),
        sa.Column('content_type', sa.String(length=120), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=True),
        sa.Column('fecha_vencimiento', sa.DateTime(), nullable=True),
        sa.Column('comentarios', sa.Text(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('uploaded_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id']),
        sa.ForeignKeyConstraint(['folder_id'], ['client_folders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['shipment_id'], ['shipments.id']),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['admin_users.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('export_documents')
    op.drop_table('country_requirements')
    op.drop_table('countries')
