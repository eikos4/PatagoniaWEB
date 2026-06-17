"""document digital signatures

Revision ID: h1a2b3c4d5e6
Revises: g9c3d56e2b44
Create Date: 2026-06-16 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'h1a2b3c4d5e6'
down_revision = 'g9c3d56e2b44'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'document_signatures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('parte', sa.String(length=20), nullable=False),
        sa.Column('signer_name', sa.String(length=200), nullable=False),
        sa.Column('signer_email', sa.String(length=200), nullable=False),
        sa.Column('signature_data', sa.Text(), nullable=False),
        sa.Column('signed_at', sa.DateTime(), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('location_label', sa.String(length=300), nullable=True),
        sa.Column('admin_user_id', sa.Integer(), nullable=True),
        sa.Column('client_folder_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id']),
        sa.ForeignKeyConstraint(['client_folder_id'], ['client_folders.id']),
        sa.ForeignKeyConstraint(['document_id'], ['export_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id', 'parte', name='uq_document_signature_parte'),
        sa.UniqueConstraint('token'),
    )
    op.create_index(op.f('ix_document_signatures_token'), 'document_signatures', ['token'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_document_signatures_token'), table_name='document_signatures')
    op.drop_table('document_signatures')
