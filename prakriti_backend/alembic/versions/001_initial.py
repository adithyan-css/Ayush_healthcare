"""initial
Revision ID: 001
Revises:
Create Date: 2026-03-24 10:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_uuid = sa.Uuid()


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', _uuid, primary_key=True, nullable=False),
        sa.Column('firebase_uid', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False, server_default='patient'),
        sa.Column('language', sa.String(), nullable=False, server_default='en'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_firebase_uid', 'users', ['firebase_uid'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    op.create_table(
        'prakriti_profiles',
        sa.Column('id', _uuid, primary_key=True, nullable=False),
        sa.Column('user_id', _uuid, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vata_score', sa.Float(), nullable=False),
        sa.Column('pitta_score', sa.Float(), nullable=False),
        sa.Column('kapha_score', sa.Float(), nullable=False),
        sa.Column('dominant_dosha', sa.String(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0'),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_prakriti_profiles_id', 'prakriti_profiles', ['id'], unique=False)
    op.create_index('ix_prakriti_profiles_user_id', 'prakriti_profiles', ['user_id'], unique=False)
    op.create_index('ix_prakriti_profiles_dominant_dosha', 'prakriti_profiles', ['dominant_dosha'], unique=False)

    op.create_table(
        'recommendation_sessions',
        sa.Column('id', _uuid, primary_key=True, nullable=False),
        sa.Column('user_id', _uuid, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('symptoms', sa.JSON(), nullable=False),
        sa.Column('free_text', sa.String(), nullable=True),
        sa.Column('season', sa.String(), nullable=False),
        sa.Column('response_json', sa.JSON(), nullable=False),
        sa.Column('prevention_plan', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_recommendation_sessions_id', 'recommendation_sessions', ['id'], unique=False)
    op.create_index('ix_recommendation_sessions_user_id', 'recommendation_sessions', ['user_id'], unique=False)
    op.create_index('ix_recommendation_sessions_season', 'recommendation_sessions', ['season'], unique=False)

    op.create_table(
        'district_risks',
        sa.Column('id', _uuid, primary_key=True, nullable=False),
        sa.Column('state_code', sa.String(), nullable=False),
        sa.Column('state_name', sa.String(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(), nullable=False),
        sa.Column('top_condition', sa.String(), nullable=False),
        sa.Column('trend', sa.String(), nullable=False),
        sa.Column('monthly_cases', sa.JSON(), nullable=False),
        sa.Column('seasons_map', sa.JSON(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_district_risks_id', 'district_risks', ['id'], unique=False)
    op.create_index('ix_district_risks_state_code', 'district_risks', ['state_code'], unique=False)
    op.create_index('ix_district_risks_state_name', 'district_risks', ['state_name'], unique=False)
    op.create_index('ix_district_risks_risk_score', 'district_risks', ['risk_score'], unique=False)
    op.create_index('ix_district_risks_risk_level', 'district_risks', ['risk_level'], unique=False)

    op.create_table(
        'hrv_readings',
        sa.Column('id', _uuid, primary_key=True, nullable=False),
        sa.Column('user_id', _uuid, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('hrv_ms', sa.Float(), nullable=False),
        sa.Column('nadi_type', sa.String(), nullable=False),
        sa.Column('is_anomaly', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('measured_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_hrv_readings_id', 'hrv_readings', ['id'], unique=False)
    op.create_index('ix_hrv_readings_user_id', 'hrv_readings', ['user_id'], unique=False)
    op.create_index('ix_hrv_readings_nadi_type', 'hrv_readings', ['nadi_type'], unique=False)
    op.create_index('ix_hrv_readings_is_anomaly', 'hrv_readings', ['is_anomaly'], unique=False)
    op.create_index('ix_hrv_readings_measured_at', 'hrv_readings', ['measured_at'], unique=False)

    op.create_table(
        'symptom_reports',
        sa.Column('id', _uuid, primary_key=True, nullable=False),
        sa.Column('user_id', _uuid, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('symptoms', sa.JSON(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_symptom_reports_id', 'symptom_reports', ['id'], unique=False)
    op.create_index('ix_symptom_reports_user_id', 'symptom_reports', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_symptom_reports_user_id', table_name='symptom_reports')
    op.drop_index('ix_symptom_reports_id', table_name='symptom_reports')
    op.drop_table('symptom_reports')

    op.drop_index('ix_hrv_readings_measured_at', table_name='hrv_readings')
    op.drop_index('ix_hrv_readings_is_anomaly', table_name='hrv_readings')
    op.drop_index('ix_hrv_readings_nadi_type', table_name='hrv_readings')
    op.drop_index('ix_hrv_readings_user_id', table_name='hrv_readings')
    op.drop_index('ix_hrv_readings_id', table_name='hrv_readings')
    op.drop_table('hrv_readings')

    op.drop_index('ix_district_risks_risk_level', table_name='district_risks')
    op.drop_index('ix_district_risks_risk_score', table_name='district_risks')
    op.drop_index('ix_district_risks_state_name', table_name='district_risks')
    op.drop_index('ix_district_risks_state_code', table_name='district_risks')
    op.drop_index('ix_district_risks_id', table_name='district_risks')
    op.drop_table('district_risks')

    op.drop_index('ix_recommendation_sessions_season', table_name='recommendation_sessions')
    op.drop_index('ix_recommendation_sessions_user_id', table_name='recommendation_sessions')
    op.drop_index('ix_recommendation_sessions_id', table_name='recommendation_sessions')
    op.drop_table('recommendation_sessions')

    op.drop_index('ix_prakriti_profiles_dominant_dosha', table_name='prakriti_profiles')
    op.drop_index('ix_prakriti_profiles_user_id', table_name='prakriti_profiles')
    op.drop_index('ix_prakriti_profiles_id', table_name='prakriti_profiles')
    op.drop_table('prakriti_profiles')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_firebase_uid', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
