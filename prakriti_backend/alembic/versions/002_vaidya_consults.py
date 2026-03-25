"""add vaidya consults
Revision ID: 002
Revises: 001
Create Date: 2026-03-25 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_uuid = sa.Uuid()


def upgrade() -> None:
	op.create_table(
		'vaidya_consults',
		sa.Column('id', _uuid, primary_key=True, nullable=False),
		sa.Column('doctor_id', _uuid, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
		sa.Column('patient_id', _uuid, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
		sa.Column('symptoms', sa.JSON(), nullable=False),
		sa.Column('suggestion_json', sa.JSON(), nullable=True),
		sa.Column('outcome_json', sa.JSON(), nullable=True),
		sa.Column('status', sa.String(), nullable=False, server_default='suggested'),
		sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
		sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
	)
	op.create_index('ix_vaidya_consults_id', 'vaidya_consults', ['id'], unique=False)
	op.create_index('ix_vaidya_consults_doctor_id', 'vaidya_consults', ['doctor_id'], unique=False)
	op.create_index('ix_vaidya_consults_patient_id', 'vaidya_consults', ['patient_id'], unique=False)
	op.create_index('ix_vaidya_consults_status', 'vaidya_consults', ['status'], unique=False)


def downgrade() -> None:
	op.drop_index('ix_vaidya_consults_status', table_name='vaidya_consults')
	op.drop_index('ix_vaidya_consults_patient_id', table_name='vaidya_consults')
	op.drop_index('ix_vaidya_consults_doctor_id', table_name='vaidya_consults')
	op.drop_index('ix_vaidya_consults_id', table_name='vaidya_consults')
	op.drop_table('vaidya_consults')
