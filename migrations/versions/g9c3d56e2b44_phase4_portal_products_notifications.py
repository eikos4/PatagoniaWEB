"""add phase 4 products crm portal notifications

Revision ID: g9c3d56e2b44
Revises: f8b2c45d1a33
"""
from alembic import op
import sqlalchemy as sa


revision = 'g9c3d56e2b44'
down_revision = 'f8b2c45d1a33'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('formato_venta', sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column('peso_caja_kg', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('caja_largo_cm', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('caja_ancho_cm', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('caja_alto_cm', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('temperatura', sa.String(length=60), nullable=True))
        batch_op.add_column(sa.Column('vida_util_dias', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('paises_permitidos', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('certificaciones', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('imagen_filename', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('ficha_stored', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('ficha_original', sa.String(length=255), nullable=True))

    with op.batch_alter_table('client_folders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ciudad', sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column('tipo_cliente', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('condiciones_comerciales', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('ejecutivo_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('portal_activo', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('portal_email', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('portal_password_hash', sa.String(length=255), nullable=True))
        batch_op.create_foreign_key('fk_client_folders_ejecutivo', 'admin_users', ['ejecutivo_id'], ['id'])

    op.create_table('notification_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=30), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=True),
        sa.Column('destinatario', sa.String(length=120), nullable=False),
        sa.Column('canal', sa.String(length=20), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=False),
        sa.Column('error_detalle', sa.Text(), nullable=True),
        sa.Column('folder_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['folder_id'], ['client_folders.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('notification_logs')
    with op.batch_alter_table('client_folders', schema=None) as batch_op:
        batch_op.drop_constraint('fk_client_folders_ejecutivo', type_='foreignkey')
        batch_op.drop_column('portal_password_hash')
        batch_op.drop_column('portal_email')
        batch_op.drop_column('portal_activo')
        batch_op.drop_column('ejecutivo_id')
        batch_op.drop_column('condiciones_comerciales')
        batch_op.drop_column('tipo_cliente')
        batch_op.drop_column('ciudad')
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('ficha_original')
        batch_op.drop_column('ficha_stored')
        batch_op.drop_column('imagen_filename')
        batch_op.drop_column('certificaciones')
        batch_op.drop_column('paises_permitidos')
        batch_op.drop_column('vida_util_dias')
        batch_op.drop_column('temperatura')
        batch_op.drop_column('caja_alto_cm')
        batch_op.drop_column('caja_ancho_cm')
        batch_op.drop_column('caja_largo_cm')
        batch_op.drop_column('peso_caja_kg')
        batch_op.drop_column('formato_venta')
